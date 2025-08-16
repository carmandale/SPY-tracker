"""
Tests for admin endpoints - Official price refresh and monitoring functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

# Import the FastAPI app to create test client
from app.main import app
from app.models import DailyPrediction, PriceLog


class TestAdminEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_refresh_official_prices_single_date_success(self):
        """Test refresh official prices for a single date"""
        test_date = "2025-08-15"
        
        with patch('app.routers.admin.default_provider') as mock_provider:
            with patch('app.routers.admin.get_db') as mock_get_db:
                # Mock successful price retrieval
                mock_ohlc = {
                    'open': 580.50,
                    'high': 582.75,
                    'low': 579.25,
                    'close': 581.90
                }
                mock_provider.get_daily_ohlc.return_value = mock_ohlc
                mock_provider.validate_official_price.return_value = True
                
                # Mock database
                mock_db = Mock(spec=Session)
                mock_pred = DailyPrediction(date=date(2025, 8, 15))
                mock_db.query.return_value.filter.return_value.first.return_value = mock_pred
                mock_get_db.return_value = mock_db
                
                response = self.client.post(f"/admin/refresh-official-prices/{test_date}")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["date"], test_date)
        self.assertEqual(response_data["status"], "success")
        self.assertIn("prices_updated", response_data)
        self.assertEqual(len(response_data["prices_updated"]), 4)  # open, noon, twoPM, close
    
    def test_refresh_official_prices_single_date_no_data(self):
        """Test refresh official prices when no market data available"""
        test_date = "2025-08-17"  # Saturday
        
        with patch('app.routers.admin.default_provider') as mock_provider:
            with patch('app.routers.admin.get_db') as mock_get_db:
                # Mock no data available
                mock_provider.get_daily_ohlc.return_value = None
                
                # Mock database
                mock_db = Mock(spec=Session)
                mock_get_db.return_value = mock_db
                
                response = self.client.post(f"/admin/refresh-official-prices/{test_date}")
        
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        self.assertIn("No official price data available", response_data["detail"])
    
    def test_refresh_official_prices_single_date_with_force(self):
        """Test refresh official prices with force flag overwrites existing data"""
        test_date = "2025-08-15"
        
        with patch('app.routers.admin.default_provider') as mock_provider:
            with patch('app.routers.admin.get_db') as mock_get_db:
                # Mock successful price retrieval
                mock_ohlc = {
                    'open': 580.50,
                    'high': 582.75,
                    'low': 579.25,
                    'close': 581.90
                }
                mock_provider.get_daily_ohlc.return_value = mock_ohlc
                mock_provider.validate_official_price.return_value = True
                
                # Mock database with existing data
                mock_db = Mock(spec=Session)
                mock_pred = DailyPrediction(date=date(2025, 8, 15))
                mock_pred.open = 579.00  # Existing different price
                mock_pred.close = 580.00  # Existing different price
                mock_db.query.return_value.filter.return_value.first.return_value = mock_pred
                mock_get_db.return_value = mock_db
                
                response = self.client.post(f"/admin/refresh-official-prices/{test_date}?force=true")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["status"], "success")
        self.assertTrue(response_data["force_overwrite"])
        
        # Verify prices were updated
        self.assertEqual(mock_pred.open, 580.50)
        self.assertEqual(mock_pred.close, 581.90)
    
    def test_refresh_official_prices_date_range_success(self):
        """Test refresh official prices for a date range"""
        with patch('app.routers.admin.default_provider') as mock_provider:
            with patch('app.routers.admin.get_db') as mock_get_db:
                # Mock successful price retrieval
                mock_ohlc = {
                    'open': 580.50,
                    'high': 582.75,
                    'low': 579.25,
                    'close': 581.90
                }
                mock_provider.get_daily_ohlc.return_value = mock_ohlc
                mock_provider.validate_official_price.return_value = True
                
                # Mock database
                mock_db = Mock(spec=Session)
                mock_get_db.return_value = mock_db
                
                # Mock query that returns multiple predictions
                mock_pred1 = DailyPrediction(date=date(2025, 8, 15))
                mock_pred2 = DailyPrediction(date=date(2025, 8, 16))
                mock_db.query.return_value.filter.return_value.all.return_value = [mock_pred1, mock_pred2]
                
                response = self.client.post(
                    "/admin/refresh-official-prices-range",
                    params={"start_date": "2025-08-15", "end_date": "2025-08-16"}
                )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["start_date"], "2025-08-15")
        self.assertEqual(response_data["end_date"], "2025-08-16")
        self.assertEqual(response_data["total_dates"], 2)
        self.assertEqual(response_data["successful_updates"], 2)
        self.assertEqual(response_data["failed_updates"], 0)
    
    def test_refresh_official_prices_date_range_validation(self):
        """Test refresh official prices date range validation"""
        # Test start_date after end_date
        response = self.client.post(
            "/admin/refresh-official-prices-range",
            params={"start_date": "2025-08-16", "end_date": "2025-08-15"}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("start_date must be before or equal to end_date", response.json()["detail"])
        
        # Test date range too large
        response = self.client.post(
            "/admin/refresh-official-prices-range",
            params={"start_date": "2025-01-01", "end_date": "2025-12-31"}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Date range too large", response.json()["detail"])
    
    def test_price_capture_status_endpoint(self):
        """Test price capture status monitoring endpoint"""
        with patch('app.routers.admin.get_db') as mock_get_db:
            # Mock database with sample data
            mock_db = Mock(spec=Session)
            
            # Mock recent predictions
            recent_preds = [
                DailyPrediction(date=date(2025, 8, 15), open=580.50, noon=581.00, twoPM=581.50, close=581.90),  # Complete
                DailyPrediction(date=date(2025, 8, 14), open=579.25, noon=580.00, twoPM=580.50, close=580.75),  # Complete
                DailyPrediction(date=date(2025, 8, 13), open=None, close=None),  # Missing data
            ]
            
            # Set up mock database query chain more carefully
            mock_query = Mock()
            mock_filter = Mock()
            mock_order_by = Mock()
            mock_limit = Mock()
            
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_filter
            mock_filter.order_by.return_value = mock_order_by
            mock_order_by.limit.return_value = mock_limit
            mock_limit.all.return_value = recent_preds
            
            # Mock price logs count query (separate chain)
            mock_count_query = Mock()
            mock_count_filter = Mock()
            mock_db.query.side_effect = [mock_query, mock_count_query]  # First call returns prediction query, second returns count query
            mock_count_query.filter.return_value = mock_count_filter
            mock_count_filter.count.return_value = 25
            
            mock_get_db.return_value = mock_db
            
            response = self.client.get("/admin/price-capture-status")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Check response structure
        self.assertIn("recent_captures", response_data)
        self.assertIn("capture_quality", response_data)
        self.assertIn("total_price_logs", response_data)
        
        # Check capture quality metrics
        quality_data = response_data["capture_quality"]
        self.assertIn("completeness_rate", quality_data)
        self.assertIn("days_with_complete_data", quality_data)
        self.assertIn("days_with_missing_data", quality_data)
        
        # Verify calculations
        self.assertEqual(quality_data["days_with_complete_data"], 2)
        self.assertEqual(quality_data["days_with_missing_data"], 1)
        self.assertEqual(quality_data["completeness_rate"], 2/3)  # 66.7%
        
        self.assertEqual(response_data["total_price_logs"], 25)
    
    def test_price_capture_status_empty_data(self):
        """Test price capture status with no data"""
        with patch('app.routers.admin.get_db') as mock_get_db:
            # Mock database with no data
            mock_db = Mock(spec=Session)
            mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_db.query.return_value.filter.return_value.count.return_value = 0
            mock_get_db.return_value = mock_db
            
            response = self.client.get("/admin/price-capture-status")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertEqual(len(response_data["recent_captures"]), 0)
        self.assertEqual(response_data["capture_quality"]["completeness_rate"], 0.0)
        self.assertEqual(response_data["total_price_logs"], 0)


if __name__ == "__main__":
    unittest.main()