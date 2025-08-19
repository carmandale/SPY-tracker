"""
US Market Holiday Detection for SPY TA Tracker
"""

from datetime import date, datetime
from typing import Set, Optional

# US Market Holidays for 2025-2026
# These are the days when the US stock market is closed
MARKET_HOLIDAYS = {
    # 2025 Holidays
    date(2025, 1, 1),   # New Year's Day
    date(2025, 1, 20),  # Martin Luther King Jr. Day
    date(2025, 2, 17),  # Presidents' Day
    date(2025, 4, 18),  # Good Friday
    date(2025, 5, 26),  # Memorial Day
    date(2025, 6, 19),  # Juneteenth
    date(2025, 7, 4),   # Independence Day
    date(2025, 9, 1),   # Labor Day
    date(2025, 11, 27), # Thanksgiving
    date(2025, 12, 25), # Christmas
    
    # 2026 Holidays
    date(2026, 1, 1),   # New Year's Day
    date(2026, 1, 19),  # Martin Luther King Jr. Day
    date(2026, 2, 16),  # Presidents' Day
    date(2026, 4, 3),   # Good Friday
    date(2026, 5, 25),  # Memorial Day
    date(2026, 6, 19),  # Juneteenth
    date(2026, 7, 3),   # Independence Day (observed)
    date(2026, 9, 7),   # Labor Day
    date(2026, 11, 26), # Thanksgiving
    date(2026, 12, 25), # Christmas
}

# Early close days (market closes at 1:00 PM ET)
EARLY_CLOSE_DAYS = {
    date(2025, 7, 3),   # Day before Independence Day
    date(2025, 11, 28), # Day after Thanksgiving
    date(2025, 12, 24), # Christmas Eve
    date(2026, 11, 27), # Day after Thanksgiving
    date(2026, 12, 24), # Christmas Eve
}


def is_market_holiday(check_date: Optional[date] = None) -> bool:
    """
    Check if a given date is a US market holiday.
    
    Args:
        check_date: Date to check (defaults to today)
        
    Returns:
        bool: True if the date is a market holiday
    """
    if check_date is None:
        check_date = date.today()
    
    # Convert datetime to date if needed
    if isinstance(check_date, datetime):
        check_date = check_date.date()
    
    return check_date in MARKET_HOLIDAYS


def is_early_close(check_date: Optional[date] = None) -> bool:
    """
    Check if a given date is an early close day (1 PM ET).
    
    Args:
        check_date: Date to check (defaults to today)
        
    Returns:
        bool: True if the market closes early on this date
    """
    if check_date is None:
        check_date = date.today()
    
    # Convert datetime to date if needed
    if isinstance(check_date, datetime):
        check_date = check_date.date()
    
    return check_date in EARLY_CLOSE_DAYS


def get_next_trading_day(start_date: Optional[date] = None) -> date:
    """
    Get the next trading day (non-weekend, non-holiday).
    
    Args:
        start_date: Date to start from (defaults to today)
        
    Returns:
        date: Next trading day
    """
    if start_date is None:
        start_date = date.today()
    
    # Convert datetime to date if needed
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    
    from datetime import timedelta
    next_day = start_date + timedelta(days=1)
    
    # Skip weekends and holidays
    while next_day.weekday() >= 5 or is_market_holiday(next_day):
        next_day = next_day + timedelta(days=1)
    
    return next_day


def get_holiday_name(check_date: Optional[date] = None) -> Optional[str]:
    """
    Get the name of the holiday for a given date.
    
    Args:
        check_date: Date to check (defaults to today)
        
    Returns:
        str or None: Holiday name if it's a holiday, None otherwise
    """
    if check_date is None:
        check_date = date.today()
    
    # Convert datetime to date if needed
    if isinstance(check_date, datetime):
        check_date = check_date.date()
    
    # Map of holidays to names
    holiday_names = {
        (1, 1): "New Year's Day",
        (7, 4): "Independence Day",
        (12, 25): "Christmas",
        (6, 19): "Juneteenth",
    }
    
    # Check fixed-date holidays
    for (month, day), name in holiday_names.items():
        if check_date.month == month and check_date.day == day:
            return name
    
    # Check floating holidays (these require more complex logic)
    if check_date.month == 1 and check_date.weekday() == 0 and 15 <= check_date.day <= 21:
        return "Martin Luther King Jr. Day"
    elif check_date.month == 2 and check_date.weekday() == 0 and 15 <= check_date.day <= 21:
        return "Presidents' Day"
    elif check_date.month == 5 and check_date.weekday() == 0 and check_date.day >= 25:
        return "Memorial Day"
    elif check_date.month == 9 and check_date.weekday() == 0 and check_date.day <= 7:
        return "Labor Day"
    elif check_date.month == 11 and check_date.weekday() == 3 and 22 <= check_date.day <= 28:
        return "Thanksgiving"
    elif check_date in MARKET_HOLIDAYS:
        # For holidays we haven't specifically named
        if check_date.month == 4:
            return "Good Friday"
    
    return None