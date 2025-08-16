from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .config import settings
from .providers import default_provider
from .models import DailyPrediction, PriceLog, AIPrediction
from .ai_endpoints import create_ai_prediction_for_date


# Daily AI prediction run at 08:00 CST (weekdays) - fresh each morning
AI_PREDICTION_CRON = "0 8 * * 1-5"


def capture_price(db: Session, checkpoint: str) -> None:
    tz = ZoneInfo(settings.timezone)
    now_local = datetime.now(tz)
    # Use official OHLC prices instead of current price
    price = default_provider.get_official_price(settings.symbol, checkpoint)
    if price is None:
        return

    # Upsert DailyPrediction row for the date
    pred = db.query(DailyPrediction).filter(DailyPrediction.date == now_local.date()).first()
    if pred is None:
        pred = DailyPrediction(date=now_local.date())
        db.add(pred)
        db.flush()

    # Set checkpoint field if exists
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

    db.add(PriceLog(date=now_local.date(), checkpoint=checkpoint, price=price))
    db.commit()


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
    print(f"📅 Scheduler started with {len(scheduler.get_jobs())} jobs:")
    for job in scheduler.get_jobs():
        print(f"   - {job.id}: {job.next_run_time}")
    
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
        except Exception:
            # Do not crash scheduler on 409 or transient failures
            pass
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
            print(f"🧹 Daily cleanup: Removed {old_predictions} predictions, "
                  f"{old_ai_predictions} AI predictions, {old_price_logs} price logs older than {cutoff_date}")
    except Exception as e:
        print(f"❌ Daily cleanup failed: {e}")
        db.rollback()
    finally:
        db.close()


