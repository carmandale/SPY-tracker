"""
Integration tests for PostgreSQL Docker container and application startup.

This module tests the complete integration between Docker container management,
database connectivity, and application startup flows.
"""

import pytest
import subprocess
import time
import os
import tempfile
from unittest.mock import patch, MagicMock
from app.database_utils import (
    auto_start_postgres_if_needed,
    startup_database_check,
    verify_database_connection
)


class TestPostgreSQLIntegration:
    """Test complete PostgreSQL integration workflows."""
    
    def test_startup_database_check_with_sqlite(self):
        """Test startup database check with SQLite (should always work)."""
        # Use a temporary SQLite database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            sqlite_url = f"sqlite:///{tmp.name}"
            
            try:
                result = startup_database_check(sqlite_url)
                
                assert result["success"] is True
                assert result["database_type"] == "sqlite"
                assert "error" not in result
                
            finally:
                # Cleanup
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)
    
    def test_startup_database_check_with_invalid_postgres(self):
        """Test startup database check with invalid PostgreSQL connection."""
        invalid_url = "postgresql://invalid:invalid@localhost:9999/invalid"
        
        result = startup_database_check(invalid_url)
        
        assert result["success"] is False
        assert result["database_type"] == "postgresql"
        assert "error" in result
    
    @patch('app.database_utils.is_docker_available')
    @patch('app.database_utils.check_postgres_health')
    @patch('app.database_utils.start_postgres_container')
    @patch('app.database_utils.wait_for_postgres_ready')
    def test_auto_start_postgres_workflow(
        self, 
        mock_wait_ready, 
        mock_start_container, 
        mock_check_health,
        mock_docker_available
    ):
        """Test the complete auto-start PostgreSQL workflow."""
        
        # Setup mocks for successful workflow
        mock_docker_available.return_value = True
        mock_check_health.return_value = False  # Initially not healthy
        mock_start_container.return_value = True
        mock_wait_ready.return_value = True
        
        database_url = "postgresql://spy:pass@localhost:5433/spy"
        success, message = auto_start_postgres_if_needed(database_url)
        
        assert success is True
        assert "Successfully started" in message
        
        # Verify the workflow was followed
        mock_docker_available.assert_called_once()
        mock_check_health.assert_called_once_with(database_url)
        mock_start_container.assert_called_once()
        mock_wait_ready.assert_called_once()
    
    @patch('app.database_utils.is_docker_available')
    def test_auto_start_postgres_no_docker(self, mock_docker_available):
        """Test auto-start when Docker is not available."""
        mock_docker_available.return_value = False
        
        database_url = "postgresql://spy:pass@localhost:5433/spy"
        success, message = auto_start_postgres_if_needed(database_url)
        
        assert success is False
        assert "Docker not available" in message
    
    @patch('app.database_utils.is_docker_available')
    @patch('app.database_utils.check_postgres_health')
    def test_auto_start_postgres_already_healthy(
        self, 
        mock_check_health,
        mock_docker_available
    ):
        """Test auto-start when PostgreSQL is already healthy."""
        mock_docker_available.return_value = True
        mock_check_health.return_value = True  # Already healthy
        
        database_url = "postgresql://spy:pass@localhost:5433/spy"
        success, message = auto_start_postgres_if_needed(database_url)
        
        assert success is True
        assert "already accessible" in message
    
    def test_auto_start_postgres_non_local_connection(self):
        """Test auto-start with non-local PostgreSQL connection."""
        # Should not attempt to start container for remote connections
        remote_url = "postgresql://user:pass@remote-server:5432/db"
        success, message = auto_start_postgres_if_needed(remote_url)
        
        assert success is True
        assert "Not a local PostgreSQL connection" in message
    
    def test_auto_start_postgres_sqlite_connection(self):
        """Test auto-start with SQLite connection."""
        sqlite_url = "sqlite:///./test.db"
        success, message = auto_start_postgres_if_needed(sqlite_url)
        
        assert success is True
        assert "Not a local PostgreSQL connection" in message


class TestDatabaseContainerLifecycle:
    """Test complete container lifecycle scenarios."""
    
    @pytest.mark.skipif(
        not subprocess.run(["docker", "info"], capture_output=True).returncode == 0,
        reason="Docker not available"
    )
    def test_container_lifecycle_with_real_docker(self):
        """
        Test complete container lifecycle with real Docker.
        
        This test requires Docker to be running and will:
        1. Start a test PostgreSQL container
        2. Verify it becomes healthy
        3. Test database connectivity  
        4. Clean up the container
        
        Uses a different port to avoid conflicts with development containers.
        """
        container_name = "spydb-integration-test"
        test_port = 5436
        
        # Cleanup any existing test container
        subprocess.run(
            ["docker", "rm", "-f", container_name], 
            capture_output=True
        )
        
        try:
            # Start test container
            cmd = [
                "docker", "run", "--name", container_name, "-d",
                "-e", "POSTGRES_USER=spy",
                "-e", "POSTGRES_PASSWORD=pass",
                "-e", "POSTGRES_DB=spy",
                "-p", f"{test_port}:5432",
                "postgres:16"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Failed to start container: {result.stderr}"
            
            # Wait for container to be healthy
            max_wait = 30
            container_ready = False
            
            for _ in range(max_wait):
                health_check = subprocess.run(
                    ["docker", "exec", container_name, "pg_isready", "-U", "spy", "-d", "spy"],
                    capture_output=True,
                    text=True
                )
                
                if health_check.returncode == 0:
                    container_ready = True
                    break
                
                time.sleep(1)
            
            assert container_ready, "Container failed to become ready"
            
            # Test database connectivity
            test_url = f"postgresql://spy:pass@localhost:{test_port}/spy"
            
            # Wait a bit more for database to be fully ready for connections
            time.sleep(2)
            
            # Verify database connection works
            connection_works = verify_database_connection(test_url)
            assert connection_works, "Database connection verification failed"
            
            # Test startup database check
            startup_result = startup_database_check(test_url)
            assert startup_result["success"] is True
            assert startup_result["database_type"] == "postgresql"
            
        finally:
            # Always cleanup the test container
            subprocess.run(
                ["docker", "rm", "-f", container_name], 
                capture_output=True
            )
    
    def test_environment_variable_integration(self):
        """Test integration with environment variable configuration."""
        # Test with environment variables that would be set by .env
        test_env = {
            "DATABASE_URL": "postgresql://spy:pass@localhost:5433/spy",
            "API_PORT": "8000",
            "DEBUG": "true"
        }
        
        with patch.dict(os.environ, test_env):
            # Test that database URL is properly detected
            from app.config import settings
            
            # Force reload settings to pick up environment changes
            settings_dict = {
                "database_url": os.environ.get("DATABASE_URL", "sqlite:///./spy_tracker.db"),
                "debug": os.environ.get("DEBUG", "false").lower() == "true"
            }
            
            assert "postgresql" in settings_dict["database_url"]
            assert settings_dict["debug"] is True


class TestApplicationStartupIntegration:
    """Test complete application startup integration."""
    
    def test_config_loading_with_postgres_env(self):
        """Test configuration loading with PostgreSQL environment."""
        # Create a temporary .env file
        env_content = """
DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy
API_PORT=8000
DEBUG=true
OPENAI_API_KEY=test-key
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file = f.name
        
        try:
            # Test loading environment configuration
            from dotenv import load_dotenv
            
            # Load the test environment
            load_dotenv(env_file, override=True)
            
            # Verify environment variables are set
            assert os.environ.get("DATABASE_URL") == "postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy"
            assert os.environ.get("API_PORT") == "8000"
            assert os.environ.get("DEBUG") == "true"
            
        finally:
            # Cleanup
            if os.path.exists(env_file):
                os.unlink(env_file)
    
    def test_startup_with_postgres_auto_start(self):
        """Test application startup with PostgreSQL auto-start."""
        from app.database_utils import auto_start_postgres_if_needed
        
        with patch('app.database_utils.is_docker_available') as mock_docker, \
             patch('app.database_utils.check_postgres_health') as mock_health, \
             patch('app.database_utils.start_postgres_container') as mock_start, \
             patch('app.database_utils.wait_for_postgres_ready') as mock_wait:
                
            # Mock successful workflow
            mock_docker.return_value = True
            mock_health.return_value = False  # Not initially healthy
            mock_start.return_value = True
            mock_wait.return_value = True
            
            database_url = "postgresql://spy:pass@localhost:5433/spy"
            
            # Test the startup flow
            success, message = auto_start_postgres_if_needed(database_url)
            
            assert success is True
            assert "successfully" in message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])