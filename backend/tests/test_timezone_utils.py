"""
Tests for timezone_utils module.
"""

import unittest
from datetime import datetime, time, timedelta, timezone
import pytz

from app.timezone_utils import (
    ET, CT, UTC,
    is_dst, get_et_offset, get_checkpoint_datetime,
    is_market_open, get_market_dates, format_checkpoint_times
)


class TestTimezoneUtils(unittest.TestCase):
    def test_is_dst(self):
        # January 1, 2025 - Not DST
        winter_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        self.assertFalse(is_dst(winter_date))
        
        # July 1, 2025 - DST
        summer_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
        self.assertTrue(is_dst(summer_date))
        
        # Test with naive datetime
        naive_summer = datetime(2025, 7, 1)
        self.assertTrue(is_dst(naive_summer))
    
    def test_get_et_offset(self):
        # January 1, 2025 - EST (-5)
        winter_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(get_et_offset(winter_date), -5)
        
        # July 1, 2025 - EDT (-4)
        summer_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
        self.assertEqual(get_et_offset(summer_date), -4)
    
    def test_get_checkpoint_datetime(self):
        # Test for a specific date (non-DST)
        test_date = datetime(2025, 1, 15)
        
        # Market open (9:30 AM ET)
        open_dt = get_checkpoint_datetime(test_date, "open")
        self.assertEqual(open_dt.hour, 9)
        self.assertEqual(open_dt.minute, 30)
        self.assertEqual(open_dt.tzinfo, ET)
        
        # Market close (4:00 PM ET)
        close_dt = get_checkpoint_datetime(test_date, "close")
        self.assertEqual(close_dt.hour, 16)
        self.assertEqual(close_dt.minute, 0)
        self.assertEqual(close_dt.tzinfo, ET)
        
        # Test with invalid checkpoint
        with self.assertRaises(ValueError):
            get_checkpoint_datetime(test_date, "invalid")
    
    def test_is_market_open(self):
        # Monday at 10:00 AM ET (market open)
        monday_morning = datetime(2025, 1, 6, 10, 0, tzinfo=ET)
        self.assertTrue(is_market_open(monday_morning))
        
        # Monday at 8:00 AM ET (before market open)
        monday_early = datetime(2025, 1, 6, 8, 0, tzinfo=ET)
        self.assertFalse(is_market_open(monday_early))
        
        # Monday at 5:00 PM ET (after market close)
        monday_evening = datetime(2025, 1, 6, 17, 0, tzinfo=ET)
        self.assertFalse(is_market_open(monday_evening))
        
        # Saturday (weekend)
        saturday = datetime(2025, 1, 4, 12, 0, tzinfo=ET)
        self.assertFalse(is_market_open(saturday))
    
    def test_get_market_dates(self):
        # This test is time-dependent, so we'll just check the structure
        start_date, end_date = get_market_dates(5)
        
        # Check that dates are timezone-aware
        self.assertIsNotNone(start_date.tzinfo)
        self.assertIsNotNone(end_date.tzinfo)
        
        # Check that start_date is before end_date
        self.assertLess(start_date, end_date)
        
        # Check that the difference is reasonable
        diff_days = (end_date - start_date).days
        self.assertGreaterEqual(diff_days, 7)  # At least a week for 5 trading days
    
    def test_format_checkpoint_times(self):
        formatted = format_checkpoint_times()
        
        # Check that all expected checkpoints are present
        self.assertIn("open", formatted)
        self.assertIn("noon", formatted)
        self.assertIn("twoPM", formatted)
        self.assertIn("close", formatted)
        
        # Check format of times
        self.assertIn("ET", formatted["open"])
        self.assertIn("9:30", formatted["open"])
        self.assertIn("4:00", formatted["close"])


if __name__ == "__main__":
    unittest.main()

