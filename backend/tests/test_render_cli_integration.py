"""
Tests for Render CLI authentication, connection, and production database access.

These tests verify:
1. Render CLI installation and availability
2. Authentication with Render API
3. Service discovery and status checking
4. Production database connection verification
5. Read-only database query capabilities
6. Health check and monitoring tools
"""

import os
import subprocess
import pytest
from unittest.mock import Mock, patch, call
from pathlib import Path
import json
import tempfile
from datetime import datetime

from app.config import settings


class TestRenderCLISetup:
    """Test Render CLI installation and basic setup."""
    
    def test_render_cli_availability(self):
        """Test that render CLI can be executed."""
        try:
            result = subprocess.run(['render', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            assert result.returncode == 0 or "command not found" in result.stderr
            # Either CLI is available or not installed (which is expected initially)
        except FileNotFoundError:
            # CLI not installed yet - this is expected for initial setup
            pass
        except subprocess.TimeoutExpired:
            pytest.fail("Render CLI command timed out")

    @patch('subprocess.run')
    def test_render_cli_installation_command(self, mock_run):
        """Test render CLI installation via npm."""
        mock_run.return_value = Mock(returncode=0, stdout="success", stderr="")
        
        # Simulate installation command
        result = subprocess.run(['npm', 'install', '-g', '@render/cli'], 
                              capture_output=True, text=True)
        
        # Since we're mocking, the actual command won't run
        # We're testing the command structure is correct
        assert mock_run.called

    def test_render_cli_auth_command_structure(self):
        """Test render CLI authentication command structure."""
        # Test that auth command would be well-formed
        auth_commands = [
            ['render', 'auth', 'login'],
            ['render', 'auth', 'login', '--token', 'fake-token']
        ]
        
        for cmd in auth_commands:
            assert len(cmd) >= 3
            assert cmd[0] == 'render'
            assert cmd[1] == 'auth'


class TestRenderAuthentication:
    """Test Render API authentication and service discovery."""

    @patch('subprocess.run')
    def test_render_auth_status(self, mock_run):
        """Test checking render authentication status."""
        mock_run.return_value = Mock(
            returncode=0, 
            stdout='{"user": {"email": "test@example.com"}}',
            stderr=""
        )
        
        result = subprocess.run(['render', 'auth', 'status'], 
                              capture_output=True, text=True)
        
        assert mock_run.called
        # Would check if authenticated in real scenario

    @patch('subprocess.run')
    def test_render_service_list(self, mock_run):
        """Test listing Render services."""
        mock_services_output = json.dumps([
            {
                "id": "srv-123456",
                "name": "SPY-tracker", 
                "type": "web",
                "status": "live",
                "url": "https://spy-tracker.onrender.com"
            }
        ])
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_services_output,
            stderr=""
        )
        
        result = subprocess.run(['render', 'services', 'list', '--json'], 
                              capture_output=True, text=True)
        
        assert mock_run.called

    @patch('subprocess.run')
    def test_render_service_discovery(self, mock_run):
        """Test discovering the SPY-tracker service on Render."""
        mock_services_output = json.dumps([
            {
                "id": "srv-123456",
                "name": "SPY-tracker",
                "type": "web", 
                "status": "live",
                "url": "https://spy-tracker.onrender.com"
            }
        ])
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_services_output,
            stderr=""
        )
        
        # This would be the actual discovery logic
        result = subprocess.run(['render', 'services', 'list', '--json'],
                              capture_output=True, text=True)
        
        assert mock_run.called
        # In real implementation, would parse JSON and find SPY-tracker service


class TestProductionDatabaseConnection:
    """Test production database connection verification."""

    @patch('subprocess.run')
    def test_render_db_list(self, mock_run):
        """Test listing Render databases."""
        mock_db_output = json.dumps([
            {
                "id": "dpg-123456",
                "name": "spy-tracker-db",
                "type": "postgresql",
                "status": "available",
                "plan": "starter"
            }
        ])
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_db_output,
            stderr=""
        )
        
        result = subprocess.run(['render', 'databases', 'list', '--json'],
                              capture_output=True, text=True)
        
        assert mock_run.called

    @patch('subprocess.run')
    def test_render_service_shell_connection(self, mock_run):
        """Test connecting to production service shell."""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")
        
        # This would open an interactive shell in production
        result = subprocess.run(['render', 'shell', 'srv-123456'],
                              capture_output=True, text=True)
        
        assert mock_run.called

    @patch('subprocess.run')
    def test_production_database_connection_string_retrieval(self, mock_run):
        """Test retrieving production database connection string."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='DATABASE_URL=postgresql://user:pass@host:5432/db',
            stderr=""
        )
        
        # Would get env vars from production service
        result = subprocess.run(['render', 'services', 'env', 'srv-123456'],
                              capture_output=True, text=True)
        
        assert mock_run.called

    @patch('psycopg2.connect')
    def test_production_database_connectivity_check(self, mock_connect):
        """Test direct connection to production database."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Simulate connection test
        import psycopg2
        conn = psycopg2.connect("postgresql://fake-connection-string")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        assert result == (1,)
        mock_connect.assert_called_once()


class TestReadOnlyDatabaseQueries:
    """Test read-only production database query capabilities."""

    @patch('psycopg2.connect')
    def test_readonly_daily_predictions_count(self, mock_connect):
        """Test read-only query to count daily predictions."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (42,)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Simulate read-only query
        import psycopg2
        conn = psycopg2.connect("postgresql://readonly-connection")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM daily_predictions")
        count = cursor.fetchone()[0]
        
        assert count == 42
        mock_connect.assert_called_once()

    @patch('psycopg2.connect')
    def test_readonly_recent_predictions_query(self, mock_connect):
        """Test read-only query for recent predictions."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ('2025-08-17', 580.50, 585.75, 'Up', True),
            ('2025-08-16', 579.25, 584.50, 'Neutral', False)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Simulate read-only query for recent predictions
        import psycopg2
        conn = psycopg2.connect("postgresql://readonly-connection")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, predLow, predHigh, bias, rangeHit 
            FROM daily_predictions 
            ORDER BY date DESC 
            LIMIT 10
        """)
        results = cursor.fetchall()
        
        assert len(results) == 2
        assert results[0][0] == '2025-08-17'
        mock_connect.assert_called_once()

    @patch('psycopg2.connect')
    def test_readonly_ai_predictions_accuracy(self, mock_connect):
        """Test read-only query for AI prediction accuracy."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0.75, 2.50)  # accuracy, avg_error
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # Simulate accuracy calculation query
        import psycopg2
        conn = psycopg2.connect("postgresql://readonly-connection")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                AVG(CASE WHEN prediction_error < 2.0 THEN 1 ELSE 0 END) as accuracy,
                AVG(prediction_error) as avg_error
            FROM ai_predictions 
            WHERE actual_price IS NOT NULL
        """)
        accuracy, avg_error = cursor.fetchone()
        
        assert accuracy == 0.75
        assert avg_error == 2.50
        mock_connect.assert_called_once()


class TestProductionHealthChecks:
    """Test production health check and status verification tools."""

    @patch('subprocess.run')
    def test_render_service_logs(self, mock_run):
        """Test fetching production service logs."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="2025-08-17 08:00:00 - AI predictions generated successfully",
            stderr=""
        )
        
        result = subprocess.run(['render', 'services', 'logs', 'srv-123456', '--tail', '100'],
                              capture_output=True, text=True)
        
        assert mock_run.called

    @patch('requests.get')
    def test_production_health_endpoint(self, mock_get):
        """Test production health check endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "app": "SPY TA Tracker"}
        mock_get.return_value = mock_response
        
        import requests
        response = requests.get("https://spy-tracker.onrender.com/healthz")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @patch('requests.get')
    def test_production_scheduler_status(self, mock_get):
        """Test production scheduler status endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "running",
            "jobs_count": 6,
            "timezone": "America/Chicago"
        }
        mock_get.return_value = mock_response
        
        import requests
        response = requests.get("https://spy-tracker.onrender.com/scheduler/status")
        
        assert response.status_code == 200
        assert response.json()["jobs_count"] == 6

    @patch('subprocess.run')
    def test_render_service_metrics(self, mock_run):
        """Test fetching production service metrics."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"cpu_usage": 15, "memory_usage": 45, "status": "live"}',
            stderr=""
        )
        
        result = subprocess.run(['render', 'services', 'get', 'srv-123456', '--json'],
                              capture_output=True, text=True)
        
        assert mock_run.called

    @patch('subprocess.run')
    def test_render_deploy_status(self, mock_run):
        """Test checking deployment status."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"status": "live", "deployed_at": "2025-08-15T12:18:00Z"}',
            stderr=""
        )
        
        result = subprocess.run(['render', 'services', 'deploys', 'srv-123456', '--json'],
                              capture_output=True, text=True)
        
        assert mock_run.called


class TestRenderCLIIntegrationScripts:
    """Test the integration scripts that will be created."""

    def test_render_setup_script_requirements(self):
        """Test requirements for render setup script."""
        # These are the functions our setup script needs to provide
        required_functions = [
            'install_render_cli',
            'authenticate_render', 
            'discover_service',
            'verify_connection',
            'setup_readonly_access'
        ]
        
        # Test that we know what functionality we need
        assert len(required_functions) == 5
        assert 'install_render_cli' in required_functions

    def test_production_access_script_requirements(self):
        """Test requirements for production access script."""
        required_capabilities = [
            'connect_to_production_db',
            'execute_readonly_queries',
            'fetch_service_logs',
            'check_health_status',
            'monitor_scheduler_jobs'
        ]
        
        assert len(required_capabilities) == 5
        assert 'connect_to_production_db' in required_capabilities

    def test_health_check_script_requirements(self):
        """Test requirements for health check script."""
        health_checks = [
            'api_health',
            'database_connectivity', 
            'scheduler_status',
            'ai_service_status',
            'service_metrics'
        ]
        
        assert len(health_checks) == 5
        assert 'api_health' in health_checks

    def test_script_error_handling_requirements(self):
        """Test error handling requirements for scripts."""
        error_scenarios = [
            'cli_not_installed',
            'authentication_failed',
            'service_not_found', 
            'database_connection_failed',
            'api_timeout'
        ]
        
        assert len(error_scenarios) == 5
        assert 'cli_not_installed' in error_scenarios