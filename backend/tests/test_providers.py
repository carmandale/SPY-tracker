"""
Tests for providers module - YFinanceProvider price capture functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timezone, timedelta
import pandas as pd
import numpy as np

from app.providers import YFinanceProvider


class TestYFinanceProvider(unittest.TestCase):
    def setUp(self):
        self.provider = YFinanceProvider()
    
    def test_get_daily_ohlc_valid_trading_day(self):
        """Test get_daily_ohlc with valid trading day data"""
        # Mock yfinance ticker and history data
        mock_ticker = Mock()
        mock_hist = pd.DataFrame({
            'Open': [580.50],
            'High': [582.75],
            'Low': [579.25],
            'Close': [581.90],
            'Volume': [45000000]
        }, index=[datetime(2025, 8, 15, 9, 30, tzinfo=timezone.utc)])
        
        mock_ticker.history.return_value = mock_hist
        
        with patch('app.providers.yf.Ticker', return_value=mock_ticker):
            result = self.provider.get_daily_ohlc('SPY', date(2025, 8, 15))
        
        self.assertIsNotNone(result)
        self.assertEqual(result['open'], 580.50)
        self.assertEqual(result['high'], 582.75)
        self.assertEqual(result['low'], 579.25)
        self.assertEqual(result['close'], 581.90)
        mock_ticker.history.assert_called_once_with(
            start=date(2025, 8, 15),
            end=date(2025, 8, 16),
            interval="1d"
        )
    
    def test_get_daily_ohlc_weekend(self):
        """Test get_daily_ohlc with weekend date (no market data)"""
        # Mock yfinance ticker with empty history
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        
        with patch('app.providers.yf.Ticker', return_value=mock_ticker):
            result = self.provider.get_daily_ohlc('SPY', date(2025, 8, 16))  # Saturday
        
        self.assertIsNone(result)
    
    def test_get_daily_ohlc_api_failure(self):
        """Test get_daily_ohlc when yfinance API fails"""
        with patch('app.providers.yf.Ticker', side_effect=Exception("API Error")):
            result = self.provider.get_daily_ohlc('SPY', date(2025, 8, 15))
        
        self.assertIsNone(result)
    
    def test_get_official_checkpoint_price_open(self):
        """Test get_official_checkpoint_price for market open"""
        # Mock OHLC data
        mock_ohlc = {
            'open': 580.50,
            'high': 582.75,
            'low': 579.25,
            'close': 581.90
        }
        
        with patch.object(self.provider, 'get_daily_ohlc', return_value=mock_ohlc):
            result = self.provider.get_official_checkpoint_price('SPY', 'open', date(2025, 8, 15))
        
        self.assertEqual(result, 580.50)
    
    def test_get_official_checkpoint_price_close(self):
        """Test get_official_checkpoint_price for market close"""
        mock_ohlc = {
            'open': 580.50,
            'high': 582.75,
            'low': 579.25,
            'close': 581.90
        }
        
        with patch.object(self.provider, 'get_daily_ohlc', return_value=mock_ohlc):
            result = self.provider.get_official_checkpoint_price('SPY', 'close', date(2025, 8, 15))
        
        self.assertEqual(result, 581.90)
    
    def test_get_official_checkpoint_price_intraday(self):
        """Test get_official_checkpoint_price for intraday checkpoints (noon, twoPM)"""
        # Mock yfinance ticker with minute data
        mock_ticker = Mock()
        
        # Create minute-level data with timezone-aware index in UTC
        # 9:30 AM EDT = 13:30 UTC, 12:00 PM EDT = 16:00 UTC, 2:00 PM EDT = 18:00 UTC
        minute_data = []
        prices = []
        
        # Start at 9:30 AM EDT (13:30 UTC) for August date
        base_time = datetime(2025, 8, 15, 13, 30, tzinfo=timezone.utc)
        
        # Generate market data every minute for 6.5 hours (390 minutes)
        for i in range(390):
            minute_data.append(base_time + timedelta(minutes=i))
            prices.append(580.0 + (i * 0.01))  # Price increases by $0.01 per minute
        
        mock_hist = pd.DataFrame({
            'Open': prices,
            'High': [p + 0.25 for p in prices],
            'Low': [p - 0.25 for p in prices],
            'Close': prices,
            'Volume': [100000] * len(prices)
        }, index=minute_data)
        
        mock_ticker.history.return_value = mock_hist
        
        with patch('app.providers.yf.Ticker', return_value=mock_ticker):
            # Test noon price (12:00 PM EDT = 16:00 UTC, which is 150 minutes after 13:30)
            noon_result = self.provider.get_official_checkpoint_price('SPY', 'noon', date(2025, 8, 15))
            
            # Test 2PM price (2:00 PM EDT = 18:00 UTC, which is 270 minutes after 13:30)
            two_pm_result = self.provider.get_official_checkpoint_price('SPY', 'twoPM', date(2025, 8, 15))
        
        self.assertIsNotNone(noon_result)
        self.assertIsNotNone(two_pm_result)
        
        # Expected prices based on our test data:
        # Noon (150 minutes): 580.0 + (150 * 0.01) = 581.50
        # 2PM (270 minutes): 580.0 + (270 * 0.01) = 582.70
        self.assertAlmostEqual(noon_result, 581.50, places=2)
        self.assertAlmostEqual(two_pm_result, 582.70, places=2)
        self.assertGreater(two_pm_result, noon_result)
    
    def test_get_official_checkpoint_price_no_data(self):
        """Test get_official_checkpoint_price when no data available"""
        with patch.object(self.provider, 'get_daily_ohlc', return_value=None):
            with patch.object(self.provider, 'get_price', return_value=580.50):
                result = self.provider.get_official_checkpoint_price('SPY', 'open', date(2025, 8, 15))
        
        # Should fallback to current price
        self.assertEqual(result, 580.50)
    
    def test_validate_official_price_valid(self):
        """Test validate_official_price with reasonable prices"""
        # Valid SPY prices
        self.assertTrue(self.provider.validate_official_price(580.50, 'SPY', 'open'))
        self.assertTrue(self.provider.validate_official_price(582.25, 'SPY', 'close'))
    
    def test_validate_official_price_invalid(self):
        """Test validate_official_price with unreasonable prices"""
        # Prices that are clearly wrong
        self.assertFalse(self.provider.validate_official_price(0.0, 'SPY', 'open'))
        self.assertFalse(self.provider.validate_official_price(-10.0, 'SPY', 'open'))
        self.assertFalse(self.provider.validate_official_price(10000.0, 'SPY', 'open'))
        self.assertFalse(self.provider.validate_official_price(None, 'SPY', 'open'))
    
    def test_validate_official_price_edge_cases(self):
        """Test validate_official_price with edge case prices"""
        # Very low but possible price
        self.assertTrue(self.provider.validate_official_price(100.0, 'SPY', 'open'))
        
        # Very high but possible price
        self.assertTrue(self.provider.validate_official_price(1000.0, 'SPY', 'open'))
    
    def test_timezone_conversion_est(self):
        """Test timezone conversion during EST (non-DST)"""
        # January date (EST)
        target_date = date(2025, 1, 15)
        
        # Mock minute data in UTC
        mock_ticker = Mock()
        utc_9_30 = datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc)  # 9:30 AM EST
        utc_12_00 = datetime(2025, 1, 15, 17, 0, tzinfo=timezone.utc)   # 12:00 PM EST
        
        mock_hist = pd.DataFrame({
            'Close': [580.0, 581.0]
        }, index=[utc_9_30, utc_12_00])
        
        mock_ticker.history.return_value = mock_hist
        
        with patch('app.providers.yf.Ticker', return_value=mock_ticker):
            result = self.provider.get_official_checkpoint_price('SPY', 'noon', target_date)
        
        self.assertEqual(result, 581.0)
    
    def test_timezone_conversion_edt(self):
        """Test timezone conversion during EDT (DST)"""
        # July date (EDT)
        target_date = date(2025, 7, 15)
        
        # Mock minute data in UTC
        mock_ticker = Mock()
        utc_9_30 = datetime(2025, 7, 15, 13, 30, tzinfo=timezone.utc)  # 9:30 AM EDT
        utc_12_00 = datetime(2025, 7, 15, 16, 0, tzinfo=timezone.utc)   # 12:00 PM EDT
        
        mock_hist = pd.DataFrame({
            'Close': [580.0, 581.0]
        }, index=[utc_9_30, utc_12_00])
        
        mock_ticker.history.return_value = mock_hist
        
        with patch('app.providers.yf.Ticker', return_value=mock_ticker):
            result = self.provider.get_official_checkpoint_price('SPY', 'noon', target_date)
        
        self.assertEqual(result, 581.0)


if __name__ == "__main__":
    unittest.main()