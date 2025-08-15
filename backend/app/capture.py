from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Dict, Optional

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from .config import settings
from .models import DailyPrediction, AIPrediction


# Checkpoints in America/Chicago. Note: for the market "close" checkpoint, most 1‑minute price feeds label
# the final bar with the minute that STARTS at 2:59 PM CT (which ends exactly at 3:00 PM CT). To reliably
# capture the closing print from minute bars, we will resolve "close" to the last bar at or before 3:00 PM,
# which typically corresponds to 2:59 PM.
CHECKPOINTS = {
    "open": time(8, 30),
    "noon": time(12, 0),
    "twoPM": time(14, 0),
    "close": time(15, 0),  # logical close; selection logic will pick the last bar <= this time
}


def _get_bar_at_or_before(df: pd.DataFrame, ts_local: datetime) -> Optional[pd.Series]:
    """Return the bar at the given local (America/Chicago) time, or the last bar before it.

    For open/noon/2pm, we try to find the exact bar time or the next minute (to account for
    timestamping differences). For close, we specifically want the last bar at or before 3:00 PM CT,
    which typically is the 2:59 PM bar.
    """
    ts_utc = pd.Timestamp(ts_local, tz="America/Chicago").tz_convert("UTC")
    # Exact
    if ts_utc in df.index:
        return df.loc[ts_utc]
    # Next minute tolerance (for open/noon/2pm alignment)
    next_min = ts_utc + pd.Timedelta(minutes=1)
    if next_min in df.index:
        return df.loc[next_min]
    # Otherwise, pick the last bar before the target timestamp
    before = df.loc[:ts_utc]
    if not before.empty:
        return before.iloc[-1]
    return None


def _download_intraday_1m(day: date) -> pd.DataFrame:
    start = pd.Timestamp(day)  # naive
    end = start + pd.Timedelta(days=1)
    df = yf.download(
        tickers=settings.symbol,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval="1m",
        auto_adjust=False,
        prepost=False,
        progress=False,
    )
    if isinstance(df, pd.DataFrame) and not df.empty:
        # Ensure single-symbol format (no column MultiIndex)
        if "Adj Close" in df.columns:
            return df
    return pd.DataFrame()


def refresh_actuals_for_date(db: Session, target_date: date, force: bool = False) -> Dict[str, Optional[float]]:
    """Fill missing checkpoint actuals for the given date using minute bars.

    - Updates `DailyPrediction` fields (open/noon/twoPM/close) if missing
    - Updates `AIPrediction.actual_price` and `prediction_error` for matching checkpoints if missing
    - Returns a dict of filled values
    """
    df = _download_intraday_1m(target_date)
    filled: Dict[str, Optional[float]] = {k: None for k in CHECKPOINTS.keys()}
    if df.empty:
        return filled

    # Ensure a DailyPrediction row exists
    day_row = db.query(DailyPrediction).filter(DailyPrediction.date == target_date).one_or_none()
    if day_row is None:
        day_row = DailyPrediction(date=target_date)
        db.add(day_row)
        db.flush()

    for checkpoint, hhmm in CHECKPOINTS.items():
        ts_local = datetime.combine(target_date, hhmm)
        bar = _get_bar_at_or_before(df, ts_local)
        if bar is None:
            continue

        # select the value for the checkpoint
        if checkpoint == "open":
            price = float(bar["Open"])  # type: ignore[index]
        else:
            price = float(bar["Close"])  # type: ignore[index]

        # update DailyPrediction if missing
        field_name = "twoPM" if checkpoint == "twoPM" else checkpoint
        existing = getattr(day_row, field_name)
        if existing is None or force:
            setattr(day_row, field_name, price)
            filled[checkpoint] = price

        # update AIPrediction actuals if present/missing
        ai = (
            db.query(AIPrediction)
            .filter(
                AIPrediction.date == target_date,
                AIPrediction.checkpoint == ("twoPM" if checkpoint == "twoPM" else checkpoint),
            )
            .one_or_none()
        )
        if ai is not None and (ai.actual_price is None or force):
            ai.actual_price = price
            ai.prediction_error = abs(ai.predicted_price - price)

    db.commit()
    return filled


