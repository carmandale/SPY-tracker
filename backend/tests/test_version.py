"""
Tests for version and deployment status endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime
import json


def test_version_endpoint_exists(client):
    """Test that /api/version endpoint exists and returns 200"""
    response = client.get("/api/version")
    assert response.status_code == 200
    

def test_version_response_structure(client):
    """Test that version endpoint returns expected structure"""
    response = client.get("/api/version")
    assert response.status_code == 200
    
    data = response.json()
    
    # Required fields
    assert "version" in data
    assert "environment" in data
    assert "deployment" in data
    assert "scheduler" in data
    
    # Deployment sub-fields
    assert "timestamp" in data["deployment"]
    assert "commit" in data["deployment"]
    assert "branch" in data["deployment"]
    
    # Scheduler sub-fields
    assert "running" in data["scheduler"]
    assert "jobs_count" in data["scheduler"]
    assert "next_prediction" in data["scheduler"]


def test_version_environment_detection(client):
    """Test that environment is correctly detected"""
    response = client.get("/api/version")
    data = response.json()
    
    # Should be 'development' in test environment
    assert data["environment"] in ["development", "production", "staging"]


def test_version_from_package_json(client):
    """Test that version is read from package.json"""
    response = client.get("/api/version")
    data = response.json()
    
    # Version should follow semantic versioning
    import re
    pattern = r'^\d+\.\d+\.\d+(-[\w\.]+)?$'
    assert re.match(pattern, data["version"])


def test_scheduler_status_in_version(client):
    """Test that scheduler status is included in version endpoint"""
    response = client.get("/api/version")
    data = response.json()
    
    scheduler = data["scheduler"]
    assert isinstance(scheduler["running"], bool)
    assert isinstance(scheduler["jobs_count"], int)
    
    # next_prediction should be ISO format timestamp or null
    if scheduler["next_prediction"]:
        # Should be parseable as datetime
        datetime.fromisoformat(scheduler["next_prediction"].replace('Z', '+00:00'))


def test_next_prediction_endpoint_exists(client):
    """Test that /api/scheduler/next-prediction endpoint exists"""
    response = client.get("/api/scheduler/next-prediction")
    assert response.status_code == 200


def test_next_prediction_response_structure(client):
    """Test next prediction endpoint response structure"""
    response = client.get("/api/scheduler/next-prediction")
    assert response.status_code == 200
    
    data = response.json()
    
    assert "next_run" in data
    assert "next_run_cst" in data
    assert "time_until" in data
    assert "market_status" in data
    assert "is_weekend" in data
    assert "is_holiday" in data
    

def test_next_prediction_time_calculation(client):
    """Test that next prediction time is correctly calculated"""
    import pytz
    CT = pytz.timezone('America/Chicago')
    with patch('app.timezone_utils.get_current_cst_time') as mock_time:
        # Test on a weekday at 7 AM CST - should be 8 AM same day
        mock_time.return_value = CT.localize(datetime(2025, 8, 19, 7, 0, 0))  # Tuesday 7 AM CST
        
        response = client.get("/api/scheduler/next-prediction")
        data = response.json()
        
        assert "08:00" in data["next_run_cst"]
        assert "2025-08-19" in data["next_run"]
        

def test_next_prediction_weekend_skip(client):
    """Test that weekends are properly skipped"""
    import pytz
    CT = pytz.timezone('America/Chicago')
    with patch('app.timezone_utils.get_current_cst_time') as mock_time:
        # Test on Friday after 8 AM - should skip to Monday
        mock_time.return_value = CT.localize(datetime(2025, 8, 22, 15, 0, 0))  # Friday 3 PM CST
        
        response = client.get("/api/scheduler/next-prediction")
        data = response.json()
        
        assert data["is_weekend"] == False  # Friday is not weekend
        assert "2025-08-25" in data["next_run"]  # Should be Monday
        assert "Monday" in data["next_run_cst"]


def test_health_check_includes_scheduler(client):
    """Test that health check includes scheduler status"""
    response = client.get("/healthz")
    assert response.status_code == 200
    
    data = response.json()
    assert "scheduler" in data
    assert "running" in data["scheduler"]


def test_changelog_endpoint_exists(client):
    """Test that /api/changelog endpoint exists"""
    response = client.get("/api/changelog")
    assert response.status_code == 200
    

def test_changelog_latest_version(client):
    """Test that changelog returns latest version info"""
    response = client.get("/api/changelog") 
    data = response.json()
    
    assert "latest_version" in data
    assert "latest_date" in data
    assert "changes" in data
    assert isinstance(data["changes"], list)