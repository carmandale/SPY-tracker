"""
Tests for intelligent database connection logic with automatic fallbacks.

This implements Task 3 from database alignment spec #25:
Write tests for smart database URL resolution with PostgreSQL preference and SQLite fallback.

The connection logic should:
1. Prefer PostgreSQL when available and configured
2. Test PostgreSQL connectivity before using it  
3. Gracefully fall back to SQLite with clear messaging
4. Provide transparent database choice information
5. Handle edge cases and connection failures
"""

import unittest
from unittest.mock import patch, MagicMock, call
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Import dependencies with graceful fallbacks for testing
try:
    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import docker
    from docker.errors import DockerException
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class TestDatabaseConnectionLogic(unittest.TestCase):
    """Test intelligent database connection logic with PostgreSQL preference."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_postgres_url = "postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy"
        self.test_sqlite_url = "sqlite:///./test_spy.db"
    
    @unittest.skipUnless(PSYCOPG2_AVAILABLE, "psycopg2 not available")
    def test_postgresql_availability_check(self):
        """Test PostgreSQL availability checking before connection attempts."""
        # Test case 1: PostgreSQL is available
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            
            from app.database_utils import check_postgresql_availability
            
            result = check_postgresql_availability(
                host="127.0.0.1",
                port=5433,
                user="spy",
                password="pass",
                database="spy"
            )
            
            self.assertTrue(result["available"])
            self.assertIn("PostgreSQL available", result["message"])
            mock_connect.assert_called_once()
            mock_conn.close.assert_called_once()
            
        # Test case 2: PostgreSQL is not available
        with patch('psycopg2.connect') as mock_connect:
            mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
            
            result = check_postgresql_availability(
                host="127.0.0.1",
                port=5433,
                user="spy",
                password="pass", 
                database="spy"
            )
            
            self.assertFalse(result["available"])
            self.assertIn("Connection failed", result["message"])
    
    @unittest.skipUnless(DOCKER_AVAILABLE, "docker package not available") 
    def test_docker_postgres_container_detection(self):
        """Test detection of PostgreSQL Docker container status."""
        # Test case 1: Container is running
        with patch('docker.from_env') as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.status = "running"
            mock_container.attrs = {
                "NetworkSettings": {
                    "Ports": {
                        "5432/tcp": [{"HostPort": "5433"}]
                    }
                }
            }
            mock_client.containers.get.return_value = mock_container
            mock_docker.return_value = mock_client
            
            from app.database_utils import check_postgres_container_status
            
            result = check_postgres_container_status("spydb")
            
            self.assertTrue(result["running"])
            self.assertEqual(result["port"], "5433")
            self.assertIn("Container spydb is running", result["message"])
            
        # Test case 2: Container not found
        with patch('docker.from_env') as mock_docker:
            mock_client = MagicMock()
            mock_client.containers.get.side_effect = docker.errors.NotFound("Container not found")
            mock_docker.return_value = mock_client
            
            result = check_postgres_container_status("spydb")
            
            self.assertFalse(result["running"])
            self.assertIsNone(result["port"])
            self.assertIn("Container spydb not found", result["message"])
            
        # Test case 3: Docker not available
        with patch('docker.from_env') as mock_docker:
            mock_docker.side_effect = DockerException("Docker not available")
            
            result = check_postgres_container_status("spydb")
            
            self.assertFalse(result["running"])
            self.assertIsNone(result["port"])
            self.assertIn("Docker not available", result["message"])
    
    def test_database_url_resolution_logic(self):
        """Test intelligent database URL resolution with fallbacks."""
        from app.database_utils import resolve_database_url
        
        # Test case 1: PostgreSQL preferred and available
        with patch('app.database_utils.check_postgresql_availability') as mock_pg_check, \
             patch('app.database_utils.check_postgres_container_status') as mock_container_check:
            
            mock_pg_check.return_value = {"available": True, "message": "PostgreSQL available"}
            mock_container_check.return_value = {"running": True, "port": "5433", "message": "Container running"}
            
            result = resolve_database_url(
                preferred_url=self.test_postgres_url,
                fallback_url=self.test_sqlite_url
            )
            
            self.assertEqual(result["database_url"], self.test_postgres_url)
            self.assertEqual(result["database_type"], "postgresql")
            self.assertTrue(result["preferred_database_used"])
            self.assertIn("PostgreSQL", result["message"])
            
        # Test case 2: PostgreSQL not available, fallback to SQLite
        with patch('app.database_utils.check_postgresql_availability') as mock_pg_check, \
             patch('app.database_utils.check_postgres_container_status') as mock_container_check:
            
            mock_pg_check.return_value = {"available": False, "message": "Connection failed"}
            mock_container_check.return_value = {"running": False, "port": None, "message": "Container not running"}
            
            result = resolve_database_url(
                preferred_url=self.test_postgres_url,
                fallback_url=self.test_sqlite_url
            )
            
            self.assertEqual(result["database_url"], self.test_sqlite_url)
            self.assertEqual(result["database_type"], "sqlite")
            self.assertFalse(result["preferred_database_used"])
            self.assertIn("Falling back to SQLite", result["message"])
            
        # Test case 3: SQLite-only configuration
        result = resolve_database_url(
            preferred_url=self.test_sqlite_url,
            fallback_url=self.test_sqlite_url
        )
        
        self.assertEqual(result["database_url"], self.test_sqlite_url)
        self.assertEqual(result["database_type"], "sqlite")
        self.assertTrue(result["preferred_database_used"])
        self.assertIn("SQLite configured", result["message"])
    
    def test_database_url_parsing(self):
        """Test parsing of database URLs for connection parameters."""
        from app.database_utils import parse_database_url
        
        test_cases = [
            {
                "url": "postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy",
                "expected": {
                    "scheme": "postgresql+psycopg2",
                    "host": "127.0.0.1", 
                    "port": 5433,
                    "username": "spy",
                    "password": "pass",
                    "database": "spy"
                }
            },
            {
                "url": "postgresql://spy:pass@localhost:5432/spy",
                "expected": {
                    "scheme": "postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "username": "spy", 
                    "password": "pass",
                    "database": "spy"
                }
            },
            {
                "url": "sqlite:///./spy_tracker.db",
                "expected": {
                    "scheme": "sqlite",
                    "host": None,
                    "port": None,
                    "username": None,
                    "password": None,
                    "database": "./spy_tracker.db"
                }
            }
        ]
        
        for test_case in test_cases:
            result = parse_database_url(test_case["url"])
            for key, expected_value in test_case["expected"].items():
                self.assertEqual(result[key], expected_value, 
                               f"Failed parsing {key} from URL: {test_case['url']}")
                               
    def test_sqlalchemy_engine_creation_with_fallback(self):
        """Test SQLAlchemy engine creation with automatic fallback logic."""
        from app.database_utils import create_engine_with_fallback
        
        # Test case 1: Successful PostgreSQL connection
        with patch('app.database_utils.resolve_database_url') as mock_resolve:
            mock_resolve.return_value = {
                "database_url": self.test_postgres_url,
                "database_type": "postgresql",
                "preferred_database_used": True,
                "message": "PostgreSQL connected successfully"
            }
            
            with patch('sqlalchemy.create_engine') as mock_create_engine:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine
                
                # Mock successful connection test
                mock_conn = MagicMock()
                mock_engine.connect.return_value.__enter__.return_value = mock_conn
                
                result = create_engine_with_fallback(
                    preferred_url=self.test_postgres_url,
                    fallback_url=self.test_sqlite_url
                )
                
                self.assertEqual(result["engine"], mock_engine)
                self.assertEqual(result["database_type"], "postgresql")
                self.assertTrue(result["connection_successful"])
                
        # Test case 2: PostgreSQL fails, fallback to SQLite
        with patch('app.database_utils.resolve_database_url') as mock_resolve:
            # First call returns PostgreSQL (preferred)
            # Second call returns SQLite (fallback)
            mock_resolve.side_effect = [
                {
                    "database_url": self.test_postgres_url,
                    "database_type": "postgresql", 
                    "preferred_database_used": True,
                    "message": "PostgreSQL available"
                },
                {
                    "database_url": self.test_sqlite_url,
                    "database_type": "sqlite",
                    "preferred_database_used": False,
                    "message": "Falling back to SQLite"
                }
            ]
            
            with patch('sqlalchemy.create_engine') as mock_create_engine:
                # First engine (PostgreSQL) fails connection
                mock_pg_engine = MagicMock()
                mock_pg_engine.connect.side_effect = OperationalError("Connection failed", None, None)
                
                # Second engine (SQLite) succeeds
                mock_sqlite_engine = MagicMock()
                mock_conn = MagicMock()
                mock_sqlite_engine.connect.return_value.__enter__.return_value = mock_conn
                
                mock_create_engine.side_effect = [mock_pg_engine, mock_sqlite_engine]
                
                result = create_engine_with_fallback(
                    preferred_url=self.test_postgres_url,
                    fallback_url=self.test_sqlite_url
                )
                
                self.assertEqual(result["engine"], mock_sqlite_engine)
                self.assertEqual(result["database_type"], "sqlite")
                self.assertTrue(result["connection_successful"])
                self.assertFalse(result["preferred_database_used"])
    
    def test_startup_database_connectivity_verification(self):
        """Test startup database connectivity verification with clear messaging."""
        from app.database_utils import verify_database_connectivity
        
        # Test case 1: Successful verification
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        # Mock database version query for PostgreSQL
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ["PostgreSQL 16.1"]
        mock_conn.execute.return_value = mock_result
        
        result = verify_database_connectivity(mock_engine, "postgresql")
        
        self.assertTrue(result["connected"])
        self.assertIn("PostgreSQL", result["message"])
        self.assertIn("16.1", result["database_version"])
        
        # Test case 2: Connection failure
        mock_engine.connect.side_effect = OperationalError("Connection failed", None, None)
        
        result = verify_database_connectivity(mock_engine, "postgresql")
        
        self.assertFalse(result["connected"])
        self.assertIn("Connection failed", result["message"])
        self.assertIsNone(result["database_version"])
    
    def test_database_choice_transparency(self):
        """Test that database choice is transparent to developers."""
        from app.database_utils import get_database_status_message
        
        # Test case 1: PostgreSQL active
        status = {
            "database_type": "postgresql",
            "database_url": self.test_postgres_url,
            "preferred_database_used": True,
            "container_status": {"running": True, "port": "5433"},
            "database_version": "PostgreSQL 16.1"
        }
        
        message = get_database_status_message(status)
        
        self.assertIn("PostgreSQL", message)
        self.assertIn("5433", message)
        self.assertIn("16.1", message)
        self.assertIn("✅", message)  # Success indicator
        
        # Test case 2: SQLite fallback
        status = {
            "database_type": "sqlite",
            "database_url": self.test_sqlite_url,
            "preferred_database_used": False,
            "container_status": {"running": False, "port": None},
            "database_version": "SQLite 3.42.0",
            "fallback_reason": "PostgreSQL container not running"
        }
        
        message = get_database_status_message(status)
        
        self.assertIn("SQLite", message)
        self.assertIn("fallback", message.lower())
        self.assertIn("PostgreSQL container not running", message)
        self.assertIn("⚠️", message)  # Warning indicator
    
    def test_configuration_edge_cases(self):
        """Test edge cases in database configuration."""
        from app.database_utils import resolve_database_url
        
        # Test case 1: Invalid PostgreSQL URL format
        with patch('app.database_utils.parse_database_url') as mock_parse:
            mock_parse.side_effect = ValueError("Invalid URL format")
            
            result = resolve_database_url(
                preferred_url="invalid://url/format",
                fallback_url=self.test_sqlite_url
            )
            
            self.assertEqual(result["database_url"], self.test_sqlite_url)
            self.assertEqual(result["database_type"], "sqlite")
            self.assertFalse(result["preferred_database_used"])
            self.assertIn("Invalid URL", result["message"])
        
        # Test case 2: Both URLs invalid (should raise error)
        with patch('app.database_utils.parse_database_url') as mock_parse:
            mock_parse.side_effect = ValueError("Invalid URL format")
            
            with self.assertRaises(ValueError) as context:
                resolve_database_url(
                    preferred_url="invalid://url1",
                    fallback_url="invalid://url2"
                )
            
            self.assertIn("No valid database", str(context.exception))
        
        # Test case 3: Empty database URLs
        result = resolve_database_url(
            preferred_url="",
            fallback_url=self.test_sqlite_url
        )
        
        self.assertEqual(result["database_url"], self.test_sqlite_url)
        self.assertEqual(result["database_type"], "sqlite")
        self.assertFalse(result["preferred_database_used"])
    
    def test_connect_args_configuration(self):
        """Test proper connect_args configuration for different database types."""
        from app.database_utils import get_connect_args
        
        # Test case 1: SQLite connect_args
        sqlite_args = get_connect_args("sqlite")
        self.assertEqual(sqlite_args, {"check_same_thread": False})
        
        # Test case 2: PostgreSQL connect_args
        postgres_args = get_connect_args("postgresql")
        self.assertEqual(postgres_args, {})  # Empty for PostgreSQL
        
        # Test case 3: Unknown database type
        unknown_args = get_connect_args("mysql")
        self.assertEqual(unknown_args, {})  # Empty for unknown types


class TestDatabaseUtilsIntegration(unittest.TestCase):
    """Integration tests for database utilities."""
    
    def test_full_database_resolution_workflow(self):
        """Test the complete database resolution workflow."""
        from app.database_utils import DatabaseResolver
        
        # Create resolver instance
        resolver = DatabaseResolver()
        
        # Test with mock configuration
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy"
        }):
            
            with patch('app.database_utils.check_postgresql_availability') as mock_pg_check, \
                 patch('app.database_utils.check_postgres_container_status') as mock_container_check:
                
                # Mock PostgreSQL available
                mock_pg_check.return_value = {"available": True, "message": "PostgreSQL available"}
                mock_container_check.return_value = {"running": True, "port": "5433", "message": "Container running"}
                
                # Resolve database configuration
                config = resolver.resolve()
                
                self.assertEqual(config["database_type"], "postgresql")
                self.assertTrue(config["preferred_database_used"])
                self.assertIn("postgresql", config["database_url"])
                
                # Test that resolver caches result
                config2 = resolver.resolve()
                self.assertEqual(config, config2)
                
                # Test force refresh
                config3 = resolver.resolve(force_refresh=True)
                self.assertEqual(config["database_type"], config3["database_type"])
    
    def test_database_status_logging(self):
        """Test that database status is properly logged."""
        from app.database_utils import log_database_status
        
        status = {
            "database_type": "postgresql",
            "database_url": "postgresql://spy:pass@127.0.0.1:5433/spy",
            "preferred_database_used": True,
            "database_version": "PostgreSQL 16.1",
            "connection_time_ms": 45.2
        }
        
        with patch('app.database_utils.logger') as mock_logger:
            log_database_status(status)
            
            # Verify logging calls
            mock_logger.info.assert_called()
            log_call_args = mock_logger.info.call_args[0][0]
            
            self.assertIn("PostgreSQL", log_call_args)
            self.assertIn("16.1", log_call_args)
            self.assertIn("45.2ms", log_call_args)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)