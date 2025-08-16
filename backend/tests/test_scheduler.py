"""
Tests for scheduler module - Price capture functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timezone, timedelta
from sqlalchemy.orm import Session

from app.scheduler import capture_price
from app.models import DailyPrediction, PriceLog


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock(spec=Session)
        
    def test_capture_price_with_valid_official_price(self):
        """Test capture_price successfully stores valid official price"""
        # Mock the provider to return a valid official price
        mock_official_price = 580.50
        
        # Mock existing prediction in database
        mock_pred = DailyPrediction(date=date(2025, 8, 15))
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_pred
        
        with patch('app.scheduler.default_provider') as mock_provider:
            with patch('app.scheduler.settings') as mock_settings:
                mock_provider.get_official_checkpoint_price.return_value = mock_official_price
                mock_provider.validate_official_price.return_value = True
                mock_settings.symbol = 'SPY'
                mock_settings.timezone = 'America/Chicago'
                
                # Execute capture_price
                capture_price(self.mock_db, 'open', date(2025, 8, 15))
        
        # Verify official price method was called correctly
        mock_provider.get_official_checkpoint_price.assert_called_once_with('SPY', 'open', date(2025, 8, 15))
        mock_provider.validate_official_price.assert_called_once_with(mock_official_price, 'SPY', 'open')
        
        # Verify price was set on prediction
        self.assertEqual(mock_pred.open, mock_official_price)
        
        # Verify database operations
        self.mock_db.add.assert_called()
        self.mock_db.commit.assert_called_once()
    
    def test_capture_price_creates_new_prediction_if_none_exists(self):
        """Test capture_price creates new DailyPrediction if none exists"""
        # Mock no existing prediction in database
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        mock_official_price = 581.25
        
        with patch('app.scheduler.default_provider') as mock_provider:
            with patch('app.scheduler.settings') as mock_settings:
                with patch('app.scheduler.DailyPrediction') as mock_pred_class:
                    mock_provider.get_official_checkpoint_price.return_value = mock_official_price
                    mock_provider.validate_official_price.return_value = True
                    mock_settings.symbol = 'SPY'
                    mock_settings.timezone = 'America/Chicago'
                    
                    mock_new_pred = Mock()
                    mock_pred_class.return_value = mock_new_pred
                    
                    # Execute capture_price
                    capture_price(self.mock_db, 'close', date(2025, 8, 15))
        
        # Verify new prediction was created with correct date
        mock_pred_class.assert_called_once_with(date=date(2025, 8, 15))
        
        # Verify price was set on new prediction
        self.assertEqual(mock_new_pred.close, mock_official_price)
        
        # Verify database operations
        self.mock_db.add.assert_called()
        self.mock_db.flush.assert_called_once()
        self.mock_db.commit.assert_called_once()
    
    def test_capture_price_with_invalid_official_price(self):
        """Test capture_price handles invalid official price by skipping"""
        # Mock existing prediction
        mock_pred = DailyPrediction(date=date(2025, 8, 15))
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_pred
        
        with patch('app.scheduler.default_provider') as mock_provider:
            with patch('app.scheduler.settings') as mock_settings:
                mock_provider.get_official_checkpoint_price.return_value = 0.0  # Invalid price
                mock_provider.validate_official_price.return_value = False
                mock_settings.symbol = 'SPY'
                mock_settings.timezone = 'America/Chicago'
                
                # Execute capture_price
                capture_price(self.mock_db, 'noon', date(2025, 8, 15))
        
        # Verify validation was called
        mock_provider.validate_official_price.assert_called_once_with(0.0, 'SPY', 'noon')
        
        # Verify price was NOT set (should remain None)
        self.assertIsNone(mock_pred.noon)
        
        # Verify no database operations occurred
        self.mock_db.add.assert_not_called()
        self.mock_db.commit.assert_not_called()
    
    def test_capture_price_with_none_official_price(self):
        """Test capture_price handles None official price by skipping"""
        # Mock existing prediction
        mock_pred = DailyPrediction(date=date(2025, 8, 15))
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_pred
        
        with patch('app.scheduler.default_provider') as mock_provider:
            with patch('app.scheduler.settings') as mock_settings:
                mock_provider.get_official_checkpoint_price.return_value = None
                mock_settings.symbol = 'SPY'
                mock_settings.timezone = 'America/Chicago'
                
                # Execute capture_price
                capture_price(self.mock_db, 'twoPM', date(2025, 8, 15))
        
        # Verify no validation was called since price is None
        mock_provider.validate_official_price.assert_not_called()
        
        # Verify price was NOT set
        self.assertIsNone(mock_pred.twoPM)
        
        # Verify no database operations occurred
        self.mock_db.add.assert_not_called()
        self.mock_db.commit.assert_not_called()
    
    def test_capture_price_handles_all_checkpoint_types(self):
        """Test capture_price handles all supported checkpoint types"""
        checkpoints = ['preMarket', 'open', 'noon', 'twoPM', 'close']
        test_price = 582.00
        
        for checkpoint in checkpoints:
            with self.subTest(checkpoint=checkpoint):
                # Reset mock
                mock_db = Mock(spec=Session)
                mock_pred = DailyPrediction(date=date(2025, 8, 15))
                mock_db.query.return_value.filter.return_value.first.return_value = mock_pred
                
                with patch('app.scheduler.default_provider') as mock_provider:
                    with patch('app.scheduler.settings') as mock_settings:
                        mock_provider.get_official_checkpoint_price.return_value = test_price
                        mock_provider.validate_official_price.return_value = True
                        mock_settings.symbol = 'SPY'
                        mock_settings.timezone = 'America/Chicago'
                        
                        # Execute capture_price
                        capture_price(mock_db, checkpoint, date(2025, 8, 15))
                
                # Verify price was set on correct field
                expected_field = checkpoint
                actual_value = getattr(mock_pred, expected_field)
                self.assertEqual(actual_value, test_price, 
                               f"Price not set correctly for checkpoint {checkpoint}")
                
                # Verify database operations
                mock_db.add.assert_called()
                mock_db.commit.assert_called()
    
    def test_capture_price_logs_price_data(self):
        """Test capture_price creates PriceLog entries"""
        mock_pred = DailyPrediction(date=date(2025, 8, 15))
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_pred
        
        test_price = 583.75
        test_checkpoint = 'open'
        test_date = date(2025, 8, 15)
        
        with patch('app.scheduler.default_provider') as mock_provider:
            with patch('app.scheduler.settings') as mock_settings:
                with patch('app.scheduler.PriceLog') as mock_price_log:
                    mock_provider.get_official_checkpoint_price.return_value = test_price
                    mock_provider.validate_official_price.return_value = True
                    mock_settings.symbol = 'SPY'
                    mock_settings.timezone = 'America/Chicago'
                    
                    # Execute capture_price
                    capture_price(self.mock_db, test_checkpoint, test_date)
        
        # Verify PriceLog was created with correct data
        mock_price_log.assert_called_once_with(
            date=test_date,
            checkpoint=test_checkpoint,
            price=test_price
        )
        
        # Verify PriceLog was added to database
        self.mock_db.add.assert_called()
    
    def test_capture_price_enhanced_logging(self):
        """Test capture_price includes enhanced logging for monitoring"""
        mock_pred = DailyPrediction(date=date(2025, 8, 15))
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_pred
        
        test_price = 584.50
        
        with patch('app.scheduler.default_provider') as mock_provider:
            with patch('app.scheduler.settings') as mock_settings:
                with patch('builtins.print') as mock_print:
                    mock_provider.get_official_checkpoint_price.return_value = test_price
                    mock_provider.validate_official_price.return_value = True
                    mock_settings.symbol = 'SPY'
                    mock_settings.timezone = 'America/Chicago'
                    
                    # Execute capture_price
                    capture_price(self.mock_db, 'close', date(2025, 8, 15))
        
        # Verify successful capture was logged
        mock_print.assert_called_with(
            f"✅ Captured official close price ${test_price:.2f} for SPY on 2025-08-15"
        )


if __name__ == "__main__":
    unittest.main()