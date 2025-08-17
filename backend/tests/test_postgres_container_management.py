"""
Tests for Docker PostgreSQL container management functionality.

This module tests the Docker PostgreSQL container lifecycle management,
health checks, and readiness verification for local development.
"""

import pytest
import subprocess
import time
import psycopg2
from unittest.mock import patch, MagicMock


class TestPostgreSQLContainerManagement:
    """Test Docker PostgreSQL container management functions."""
    
    def test_docker_availability_check(self):
        """Test that Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            assert result.returncode == 0, "Docker is not running or not available"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker not available for testing")
    
    def test_postgres_image_availability(self):
        """Test that PostgreSQL 16 image is available."""
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", "postgres:16"],
                capture_output=True,
                text=True,
                timeout=30
            )
            # If image doesn't exist, pull it
            if result.returncode != 0:
                print("Pulling postgres:16 image...")
                pull_result = subprocess.run(
                    ["docker", "pull", "postgres:16"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                assert pull_result.returncode == 0, "Failed to pull postgres:16 image"
        except subprocess.TimeoutExpired:
            pytest.skip("Docker image operations timed out")
    
    def test_container_start_stop_cycle(self):
        """Test complete container lifecycle: start, health check, stop."""
        container_name = "spydb-test-lifecycle"
        
        # Cleanup any existing container
        subprocess.run(
            ["docker", "rm", "-f", container_name], 
            capture_output=True
        )
        
        try:
            # Start container
            start_cmd = [
                "docker", "run", "--name", container_name, "-d",
                "-e", "POSTGRES_USER=spy",
                "-e", "POSTGRES_PASSWORD=pass", 
                "-e", "POSTGRES_DB=spy",
                "-p", "5435:5432",  # Use different port to avoid conflicts
                "postgres:16"
            ]
            
            result = subprocess.run(start_cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Failed to start container: {result.stderr}"
            
            # Wait for container to be ready (up to 30 seconds)
            max_wait = 30
            wait_time = 0
            container_ready = False
            
            while wait_time < max_wait:
                health_check = subprocess.run(
                    ["docker", "exec", container_name, "pg_isready", "-U", "spy", "-d", "spy"],
                    capture_output=True,
                    text=True
                )
                
                if health_check.returncode == 0:
                    container_ready = True
                    break
                
                time.sleep(1)
                wait_time += 1
            
            assert container_ready, f"Container not ready after {max_wait} seconds"
            
            # Test database connection
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5435,
                    database="spy", 
                    user="spy",
                    password="pass",
                    connect_timeout=5
                )
                
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    assert result[0] == 1
                
                conn.close()
                
            except psycopg2.Error as e:
                pytest.fail(f"Database connection failed: {e}")
                
        finally:
            # Cleanup
            subprocess.run(
                ["docker", "rm", "-f", container_name], 
                capture_output=True
            )
    
    def test_health_check_implementation(self):
        """Test health check functionality for PostgreSQL readiness."""
        from app.database_utils import check_postgres_health
        
        # Test with non-existent connection (should fail)
        is_healthy = check_postgres_health("postgresql://invalid:invalid@localhost:9999/invalid")
        assert not is_healthy
        
        # Test with valid connection would require actual running container
        # This is covered in integration tests
    
    def test_database_url_validation(self):
        """Test DATABASE_URL format validation and parsing."""
        from app.database_utils import validate_database_url, parse_database_url
        
        valid_urls = [
            "postgresql://spy:pass@localhost:5433/spy",
            "postgresql+psycopg2://spy:pass@localhost:5433/spy",
            "sqlite:///./spy_tracker.db"
        ]
        
        invalid_urls = [
            "invalid_url",
            "postgresql://",
            "postgresql://user@host/",
            ""
        ]
        
        for url in valid_urls:
            assert validate_database_url(url), f"Valid URL incorrectly rejected: {url}"
        
        for url in invalid_urls:
            assert not validate_database_url(url), f"Invalid URL incorrectly accepted: {url}"
        
        # Test URL parsing
        parsed = parse_database_url("postgresql://spy:pass@localhost:5433/spy")
        assert parsed["host"] == "localhost"
        assert parsed["port"] == 5433
        assert parsed["database"] == "spy"
        assert parsed["user"] == "spy"
    
    def test_container_exists_check(self):
        """Test checking if container exists and is running."""
        from app.database_utils import is_container_running, container_exists
        
        # Test with non-existent container
        assert not container_exists("non-existent-container")
        assert not is_container_running("non-existent-container")
        
        # Test with existing container would require actual container
        # This is covered in integration tests
    
    def test_docker_compose_integration(self):
        """Test integration with docker-compose configuration."""
        # Check if docker-compose.yml exists and is valid
        import yaml
        import os
        
        compose_file = "/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/SPY-tracker/.conductor/london/docker-compose.yml"
        assert os.path.exists(compose_file), "docker-compose.yml not found"
        
        with open(compose_file, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Verify db service configuration
        assert "services" in compose_config
        assert "db" in compose_config["services"]
        
        db_config = compose_config["services"]["db"]
        assert db_config["image"] == "postgres:16"
        assert db_config["container_name"] == "spydb"
        
        # Verify environment variables
        env_vars = db_config["environment"]
        assert "POSTGRES_USER=spy" in env_vars
        assert "POSTGRES_PASSWORD=pass" in env_vars
        assert "POSTGRES_DB=spy" in env_vars
        
        # Verify health check
        assert "healthcheck" in db_config
        health_check = db_config["healthcheck"]
        assert "pg_isready" in health_check["test"][1]
        assert health_check["interval"] == "10s"
        assert health_check["retries"] == 5
    
    @patch('subprocess.run')
    def test_container_start_function(self, mock_subprocess):
        """Test container start function with mocked subprocess."""
        from app.database_utils import start_postgres_container
        
        # Mock the function to simulate container doesn't exist initially
        # First call: check if container exists (returns empty = doesn't exist)
        # Second call: create and start new container (returns success)
        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout=""),  # Container doesn't exist
            MagicMock(returncode=0, stdout="container_id")  # Container creation successful
        ]
        
        result = start_postgres_container()
        assert result is True
        
        # Verify that container existence was checked and container was created
        assert mock_subprocess.call_count == 2
        
        # Check the final call was to create the container
        final_call = mock_subprocess.call_args_list[-1]
        expected_cmd = [
            "docker", "run", "--name", "spydb", "-d",
            "-e", "POSTGRES_USER=spy",
            "-e", "POSTGRES_PASSWORD=pass",
            "-e", "POSTGRES_DB=spy", 
            "-p", "5433:5432",
            "postgres:16"
        ]
        
        # Verify the command arguments
        assert final_call[0][0] == expected_cmd
        assert final_call[1]["capture_output"] is True
        assert final_call[1]["text"] is True
    
    @patch('subprocess.run')
    def test_container_stop_function(self, mock_subprocess):
        """Test container stop function with mocked subprocess."""
        from app.database_utils import stop_postgres_container
        
        # Mock successful container stop
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        result = stop_postgres_container()
        assert result is True
        
        # Verify correct docker command was called (including timeout)
        mock_subprocess.assert_called_with(
            ["docker", "stop", "spydb"],
            capture_output=True,
            text=True,
            timeout=30
        )


class TestDatabaseHealthChecks:
    """Test database health check and readiness verification."""
    
    def test_postgres_readiness_check(self):
        """Test PostgreSQL readiness verification."""
        from app.database_utils import wait_for_postgres_ready
        
        # Test with invalid connection (should timeout quickly)
        is_ready = wait_for_postgres_ready(
            "postgresql://invalid:invalid@localhost:9999/invalid",
            max_wait_seconds=2
        )
        assert not is_ready
    
    def test_database_connectivity_verification(self):
        """Test database connectivity and basic operations.""" 
        from app.database_utils import verify_database_connection
        
        # Test with invalid connection
        is_connected = verify_database_connection(
            "postgresql://invalid:invalid@localhost:9999/invalid"
        )
        assert not is_connected
        
        # Test with SQLite (should work if file exists)
        sqlite_result = verify_database_connection("sqlite:///./test.db")
        # SQLite creates file automatically, so this should succeed
        assert sqlite_result is True
    
    def test_health_check_endpoint_simulation(self):
        """Test health check endpoint functionality."""
        from app.database_utils import create_health_check_response
        
        # Test healthy database
        response = create_health_check_response(True, "postgresql://spy:pass@localhost:5433/spy")
        assert response["status"] == "healthy"
        assert response["database"]["type"] == "postgresql"
        assert response["database"]["connected"] is True
        
        # Test unhealthy database  
        response = create_health_check_response(False, "postgresql://spy:pass@localhost:5433/spy")
        assert response["status"] == "unhealthy"
        assert response["database"]["connected"] is False
    
    def test_startup_database_verification(self):
        """Test database verification during application startup."""
        from app.database_utils import startup_database_check
        
        # Test with SQLite (should work)
        result = startup_database_check("sqlite:///./test_startup.db")
        assert result["success"] is True
        assert result["database_type"] == "sqlite"
        
        # Test with invalid PostgreSQL
        result = startup_database_check("postgresql://invalid:invalid@localhost:9999/invalid")
        assert result["success"] is False
        assert result["database_type"] == "postgresql"
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])