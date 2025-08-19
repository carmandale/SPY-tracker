"""
Tests for market holiday detection
"""

import pytest
from datetime import date, datetime
from unittest.mock import patch

from app.market_holidays import (
    is_market_holiday,
    is_early_close,
    get_next_trading_day,
    get_holiday_name
)


def test_new_years_day_is_holiday():
    """Test that New Year's Day is recognized as a holiday"""
    assert is_market_holiday(date(2025, 1, 1)) == True
    assert get_holiday_name(date(2025, 1, 1)) == "New Year's Day"


def test_mlk_day_is_holiday():
    """Test that MLK Day is recognized as a holiday"""
    assert is_market_holiday(date(2025, 1, 20)) == True
    assert get_holiday_name(date(2025, 1, 20)) == "Martin Luther King Jr. Day"


def test_independence_day_is_holiday():
    """Test that July 4th is recognized as a holiday"""
    assert is_market_holiday(date(2025, 7, 4)) == True
    assert get_holiday_name(date(2025, 7, 4)) == "Independence Day"


def test_christmas_is_holiday():
    """Test that Christmas is recognized as a holiday"""
    assert is_market_holiday(date(2025, 12, 25)) == True
    assert get_holiday_name(date(2025, 12, 25)) == "Christmas"


def test_regular_weekday_not_holiday():
    """Test that a regular weekday is not a holiday"""
    assert is_market_holiday(date(2025, 8, 19)) == False  # Tuesday
    assert get_holiday_name(date(2025, 8, 19)) is None


def test_early_close_days():
    """Test that early close days are properly detected"""
    assert is_early_close(date(2025, 7, 3)) == True  # Day before July 4th
    assert is_early_close(date(2025, 11, 28)) == True  # Day after Thanksgiving
    assert is_early_close(date(2025, 12, 24)) == True  # Christmas Eve
    assert is_early_close(date(2025, 8, 19)) == False  # Regular day


def test_get_next_trading_day_skip_weekend():
    """Test that get_next_trading_day skips weekends"""
    # Friday -> Monday
    friday = date(2025, 8, 22)
    next_day = get_next_trading_day(friday)
    assert next_day == date(2025, 8, 25)  # Monday


def test_get_next_trading_day_skip_holiday():
    """Test that get_next_trading_day skips holidays"""
    # Day before New Year's -> January 2nd
    dec_31 = date(2024, 12, 31)
    next_day = get_next_trading_day(dec_31)
    assert next_day == date(2025, 1, 2)  # January 2nd (Jan 1 is holiday)


def test_next_prediction_with_holiday(client):
    """Test that next prediction endpoint properly handles holidays"""
    import pytz
    CT = pytz.timezone('America/Chicago')
    
    with patch('app.routers.version.get_current_cst_time') as mock_time:
        # Test on Dec 24, 2025 at 3 PM CST (Christmas Eve)
        mock_time.return_value = CT.localize(datetime(2025, 12, 24, 15, 0, 0))
        
        response = client.get("/api/scheduler/next-prediction")
        data = response.json()
        
        # Should skip Christmas (Dec 25) and skip to Dec 26
        assert data["is_holiday"] == False  # Dec 24 is not a full holiday (just early close)
        assert "2025-12-26" in data["next_run"]  # Friday Dec 26