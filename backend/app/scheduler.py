from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .config import settings
from .providers import default_provider
from .models import DailyPrediction, PriceLog


CHECKPOINTS = {
    "preMarket": "0 8 * * 1-5",   # 08:00 CST
    "open": "30 8 * * 1-5",       # 08:30 CST
    "noon": "0 12 * * 1-5",       # 12:00 CST
    "twoPM": "0 14 * * 1-5",      # 14:00 CST (2 PM)
    "close": "0 15 * * 1-5",      # 15:00 CST (3 PM)
}


def capture_price(db: Session, checkpoint: str) -> None:
    tz = ZoneInfo(settings.timezone)
    now_local = datetime.now(tz)
    price = default_provider.get_price(settings.symbol)
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

    for cp, cron in CHECKPOINTS.items():
        scheduler.add_job(
            lambda cp=cp: _run_capture(get_db_session_callable, cp),
            CronTrigger.from_crontab(cron, timezone=ZoneInfo(settings.timezone)),
            id=f"capture_{cp}",
            replace_existing=True,
            max_instances=1,
        )

    scheduler.start()
    return scheduler


def _run_capture(get_db_session_callable, checkpoint: str) -> None:
    db = next(get_db_session_callable())
    try:
        capture_price(db, checkpoint)
    finally:
        db.close()


