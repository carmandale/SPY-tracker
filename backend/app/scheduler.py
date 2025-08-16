from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from typing import Optional
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .config import settings
from .providers import default_provider
from .models import DailyPrediction, PriceLog, AIPrediction
from .ai_endpoints import create_ai_prediction_for_date

# Set up logging
logger = logging.getLogger(__name__)


# Daily AI prediction run at 08:00 CST (weekdays) - fresh each morning
AI_PREDICTION_CRON = "0 8 * * 1-5"


def capture_price(db: Session, checkpoint: str, target_date: Optional[date] = None) -> None:
    """Capture official price for a specific checkpoint on a target date.
    
    Args:
        db: Database session
        checkpoint: Price checkpoint ('preMarket', 'open', 'noon', 'twoPM', 'close')
        target_date: Target date for price capture (defaults to today in local timezone)
    """
    # Determine target date - use provided date or current local date
    if target_date is None:
        tz = ZoneInfo(settings.timezone)
        target_date = datetime.now(tz).date()
    
    # Get official price using enhanced provider method
    price = default_provider.get_official_checkpoint_price(settings.symbol, checkpoint, target_date)
    
    # Validate the price before storing
    if price is None:
        logger.warning(f"No official price available for {settings.symbol} {checkpoint} on {target_date}")
        return
    
    if not default_provider.validate_official_price(price, settings.symbol, checkpoint):
        logger.warning(f"Invalid official price {price} for {settings.symbol} {checkpoint} on {target_date}")
        return

    # Upsert DailyPrediction row for the target date
    pred = db.query(DailyPrediction).filter(DailyPrediction.date == target_date).first()
    if pred is None:
        pred = DailyPrediction(date=target_date)
        db.add(pred)
        db.flush()

    # Set checkpoint field based on checkpoint type
    if checkpoint == "preMarket":
        pred.preMarket = price
    elif checkpoint == "open":
        pred.open = price
    elif checkpoint == "noon":
        pred.noon = price
    elif checkpoint == "twoPM":
        pred.twoPM = price
    elif checkpoint == "close":
        pred.close = price
    else:
        logger.warning(f"Unknown checkpoint: {checkpoint}")
        return

    # Log the price capture for audit trail
    db.add(PriceLog(date=target_date, checkpoint=checkpoint, price=price))
    
    # Commit changes to database
    db.commit()
    
    # Enhanced logging for monitoring
    logger.info(f"Captured official {checkpoint} price ${price:.2f} for {settings.symbol} on {target_date}")


def start_scheduler(get_db_session_callable):
    scheduler = BackgroundScheduler(timezone=ZoneInfo(settings.timezone))

    # Schedule AI prediction generation + lock for the day at 08:00 CST (fresh daily)
    scheduler.add_job(
        lambda: _run_ai_prediction(get_db_session_callable),
        CronTrigger.from_crontab(AI_PREDICTION_CRON, timezone=ZoneInfo(settings.timezone)),
        id="ai_predict_0800",
        replace_existing=True,
        max_instances=1,
    )

    # Schedule automated price capture at key trading times (CST timezone)
    # Pre-market capture at 08:00 CST (before market open)
    scheduler.add_job(
        lambda: _run_capture(get_db_session_callable, "preMarket"),
        CronTrigger.from_crontab("0 8 * * 1-5", timezone=ZoneInfo(settings.timezone)),
        id="capture_premarket",
        replace_existing=True,
        max_instances=1,
    )

    # Market open capture at 08:30 CST
    scheduler.add_job(
        lambda: _run_capture(get_db_session_callable, "open"),
        CronTrigger.from_crontab("30 8 * * 1-5", timezone=ZoneInfo(settings.timezone)),
        id="capture_open",
        replace_existing=True,
        max_instances=1,
    )

    # Noon capture at 12:00 CST
    scheduler.add_job(
        lambda: _run_capture(get_db_session_callable, "noon"),
        CronTrigger.from_crontab("0 12 * * 1-5", timezone=ZoneInfo(settings.timezone)),
        id="capture_noon",
        replace_existing=True,
        max_instances=1,
    )

    # 2PM capture at 14:00 CST
    scheduler.add_job(
        lambda: _run_capture(get_db_session_callable, "twoPM"),
        CronTrigger.from_crontab("0 14 * * 1-5", timezone=ZoneInfo(settings.timezone)),
        id="capture_2pm",
        replace_existing=True,
        max_instances=1,
    )

    # Market close capture at 15:00 CST
    scheduler.add_job(
        lambda: _run_capture(get_db_session_callable, "close"),
        CronTrigger.from_crontab("0 15 * * 1-5", timezone=ZoneInfo(settings.timezone)),
        id="capture_close",
        replace_existing=True,
        max_instances=1,
    )
    
    # Daily cleanup at midnight CST
    scheduler.add_job(
        lambda: _run_daily_cleanup(get_db_session_callable),
        CronTrigger.from_crontab("0 0 * * *", timezone=ZoneInfo(settings.timezone)),
        id="daily_cleanup",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info(f"Scheduler started with {len(scheduler.get_jobs())} jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"   - {job.id}: {job.next_run_time}")
    
    return scheduler


def _run_capture(get_db_session_callable, checkpoint: str) -> None:
    db = next(get_db_session_callable())
    try:
        capture_price(db, checkpoint)
    finally:
        db.close()


def _run_ai_prediction(get_db_session_callable) -> None:
    tz = ZoneInfo(settings.timezone)
    today_local = datetime.now(tz).date()
    db = next(get_db_session_callable())
    try:
        # Create and lock AI prediction for today if not locked
        try:
            create_ai_prediction_for_date(
                target_date=today_local,
                lookback_days=settings.ai_lookback_days,
                db=db,
            )
        except Exception as e:
            # Do not crash scheduler on 409 or transient failures
            logger.error(f"Failed to create AI prediction for {today_local}: {e}")
    finally:
        db.close()


def _run_daily_cleanup(get_db_session_callable) -> None:
    """Clean up old data at midnight to keep only relevant history."""
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()
    db = next(get_db_session_callable())
    try:
        # Keep 30 days of history for analysis
        cutoff_date = today - timedelta(days=30)
        
        # Clean up old predictions
        old_predictions = db.query(DailyPrediction).filter(
            DailyPrediction.date < cutoff_date
        ).delete()
        
        # Clean up old AI predictions
        old_ai_predictions = db.query(AIPrediction).filter(
            AIPrediction.date < cutoff_date
        ).delete()
        
        # Clean up old price logs
        old_price_logs = db.query(PriceLog).filter(
            PriceLog.date < cutoff_date
        ).delete()
        
        db.commit()
        
        if old_predictions or old_ai_predictions or old_price_logs:
            logger.info(f"Daily cleanup: Removed {old_predictions} predictions, "
                      f"{old_ai_predictions} AI predictions, {old_price_logs} price logs older than {cutoff_date}")
    except Exception as e:
        logger.error(f"Daily cleanup failed: {e}")
        db.rollback()
    finally:
        db.close()


