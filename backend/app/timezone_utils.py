"""
Timezone utilities for SPY TA Tracker.

This module provides standardized timezone handling for the application,
ensuring consistent treatment of market times across the codebase.
"""

from datetime import datetime, time, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
import pytz

# Standard timezone objects
ET = pytz.timezone('America/New_York')  # Eastern Time (NY)
CT = pytz.timezone('America/Chicago')   # Central Time (Chicago)
UTC = pytz.UTC

# Market hours in ET
MARKET_OPEN = time(9, 30)    # 9:30 AM ET
MARKET_CLOSE = time(16, 0)   # 4:00 PM ET

# Standard prediction checkpoints in ET
CHECKPOINTS = {
    "open": time(9, 30),     # Market open (9:30 AM ET)
    "noon": time(12, 0),     # Midday (12:00 PM ET)
    "twoPM": time(14, 0),    # Afternoon (2:00 PM ET)
    "close": time(16, 0),    # Market close (4:00 PM ET)
}

def is_dst(dt: datetime) -> bool:
    """
    Determine if a date is in Daylight Saving Time for US Eastern Time.
    
    Args:
        dt: The datetime to check (timezone-aware or naive)
        
    Returns:
        bool: True if date is in DST, False otherwise
    """
    # Make timezone-aware if naive
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to Eastern Time
    et_dt = dt.astimezone(ET)
    
    # Check if DST is active
    return et_dt.dst() != timedelta(0)


def get_et_offset(dt: Optional[datetime] = None) -> int:
    """
    Get the UTC offset for Eastern Time on the given date.
    
    Args:
        dt: The datetime to check (defaults to current time)
        
    Returns:
        int: UTC offset in hours (-5 during EST, -4 during EDT)
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    # Make timezone-aware if naive
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to Eastern Time and get offset
    et_dt = dt.astimezone(ET)
    offset_seconds = et_dt.utcoffset().total_seconds()
    return int(offset_seconds / 3600)


def get_checkpoint_datetime(date_obj: datetime, checkpoint: str) -> datetime:
    """
    Get a timezone-aware datetime for a specific checkpoint on a given date.
    
    Args:
        date_obj: The date (can be naive or timezone-aware)
        checkpoint: One of "open", "noon", "twoPM", "close"
        
    Returns:
        datetime: Timezone-aware datetime in ET for the checkpoint
        
    Raises:
        ValueError: If checkpoint is not recognized
    """
    if checkpoint not in CHECKPOINTS:
        raise ValueError(f"Unknown checkpoint: {checkpoint}. Must be one of {list(CHECKPOINTS.keys())}")
    
    # Get the time for this checkpoint
    checkpoint_time = CHECKPOINTS[checkpoint]
    
    # Ensure date_obj has date components only
    if isinstance(date_obj, datetime):
        date_only = date_obj.date()
    else:
        date_only = date_obj
    
    # Create datetime in ET
    naive_dt = datetime.combine(date_only, checkpoint_time)
    aware_dt = ET.localize(naive_dt)
    
    return aware_dt


def is_market_open(dt: Optional[datetime] = None) -> bool:
    """
    Check if the US stock market is open at the given datetime.
    
    Args:
        dt: The datetime to check (defaults to current time)
        
    Returns:
        bool: True if market is open, False otherwise
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    # Make timezone-aware if naive
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to Eastern Time
    et_dt = dt.astimezone(ET)
    
    # Check if it's a weekday
    if et_dt.weekday() > 4:  # Saturday = 5, Sunday = 6
        return False
    
    # Check market hours
    current_time = et_dt.time()
    return MARKET_OPEN <= current_time <= MARKET_CLOSE


def get_market_dates(lookback_days: int = 5) -> Tuple[datetime, datetime]:
    """
    Get appropriate start and end dates for market data lookback.
    
    This function calculates a start date that's likely to include
    the requested number of trading days, accounting for weekends.
    
    Args:
        lookback_days: Number of trading days to look back
        
    Returns:
        Tuple[datetime, datetime]: (start_date, end_date) as timezone-aware datetimes
    """
    end_date = datetime.now(ET)
    
    # Multiply by 1.5 to account for weekends
    calendar_days = int(lookback_days * 1.5)
    start_date = end_date - timedelta(days=calendar_days)
    
    return start_date, end_date


def get_current_cst_time() -> datetime:
    """
    Get the current time in CST/CDT timezone.
    
    Returns:
        datetime: Current time in Central Time
    """
    return datetime.now(CT)


def get_next_market_open(current_time: Optional[datetime] = None) -> datetime:
    """
    Get the next market open time (8:00 AM CST on weekdays).
    
    Args:
        current_time: Current time to calculate from (defaults to now)
        
    Returns:
        datetime: Next 8:00 AM CST on a weekday
    """
    if current_time is None:
        current_time = get_current_cst_time()
    
    # Ensure timezone awareness
    if current_time.tzinfo is None:
        current_time = CT.localize(current_time)
    elif current_time.tzinfo != CT:
        current_time = current_time.astimezone(CT)
    
    # Target is 8:00 AM CST
    target_time = time(8, 0)
    
    # Start with today
    next_run = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
    
    # If it's past 8 AM today, move to tomorrow
    if current_time.time() >= target_time:
        next_run = next_run + timedelta(days=1)
    
    # Skip weekends (Saturday = 5, Sunday = 6)
    while next_run.weekday() >= 5:
        next_run = next_run + timedelta(days=1)
    
    return next_run


def format_checkpoint_times() -> Dict[str, str]:
    """
    Format all checkpoint times in ET for display.
    
    Returns:
        Dict[str, str]: Mapping of checkpoint names to formatted times
    """
    return {
        checkpoint: time_obj.strftime("%-I:%M %p ET")
        for checkpoint, time_obj in CHECKPOINTS.items()
    }

