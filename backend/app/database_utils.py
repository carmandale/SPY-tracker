"""
Database utility functions for PostgreSQL container management and health checks.

This module provides utilities for managing Docker PostgreSQL containers,
verifying database connectivity, and implementing health checks.
"""

import subprocess
import time
import re
import logging
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse
import psycopg2
import sqlite3

logger = logging.getLogger(__name__)


def validate_database_url(url: str) -> bool:
    """Validate DATABASE_URL format and basic structure."""
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        
        # Check for supported schemes
        if parsed.scheme not in ['postgresql', 'postgresql+psycopg2', 'sqlite']:
            return False
        
        # For PostgreSQL, require host and database
        if parsed.scheme.startswith('postgresql'):
            if not parsed.hostname or not parsed.path.lstrip('/'):
                return False
        
        # For SQLite, path should be present
        if parsed.scheme == 'sqlite':
            if not parsed.path:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False


def parse_database_url(url: str) -> Dict[str, Any]:
    """Parse DATABASE_URL into components."""
    parsed = urlparse(url)
    
    return {
        "scheme": parsed.scheme,
        "user": parsed.username,
        "password": parsed.password, 
        "host": parsed.hostname,
        "port": parsed.port,
        "database": parsed.path.lstrip('/') if parsed.path else None,
        "path": parsed.path
    }


def check_postgres_health(database_url: str, timeout: int = 5) -> bool:
    """Check if PostgreSQL database is healthy and accessible."""
    try:
        parsed = parse_database_url(database_url)
        
        if not parsed["scheme"].startswith("postgresql"):
            return False
        
        conn = psycopg2.connect(
            host=parsed["host"],
            port=parsed["port"] or 5432,
            database=parsed["database"],
            user=parsed["user"],
            password=parsed["password"],
            connect_timeout=timeout
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        conn.close()
        return result[0] == 1
        
    except Exception as e:
        logger.debug(f"PostgreSQL health check failed: {e}")
        return False


def container_exists(container_name: str) -> bool:
    """Check if Docker container exists (running or stopped)."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-aq", "-f", f"name=^/{container_name}$"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return result.returncode == 0 and bool(result.stdout.strip())
        
    except Exception as e:
        logger.error(f"Error checking container existence: {e}")
        return False


def is_container_running(container_name: str) -> bool:
    """Check if Docker container is currently running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", f"name=^/{container_name}$"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return result.returncode == 0 and bool(result.stdout.strip())
        
    except Exception as e:
        logger.error(f"Error checking container status: {e}")
        return False


def start_postgres_container(
    container_name: str = "spydb",
    port: int = 5433,
    user: str = "spy",
    password: str = "pass",
    database: str = "spy"
) -> bool:
    """Start PostgreSQL container with specified configuration."""
    try:
        # Check if container already exists
        if container_exists(container_name):
            if is_container_running(container_name):
                logger.info(f"Container {container_name} already running")
                return True
            else:
                # Start existing container
                result = subprocess.run(
                    ["docker", "start", container_name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    logger.info(f"Started existing container {container_name}")
                    return True
                else:
                    logger.error(f"Failed to start existing container: {result.stderr}")
                    return False
        else:
            # Create and start new container
            cmd = [
                "docker", "run", "--name", container_name, "-d",
                "-e", f"POSTGRES_USER={user}",
                "-e", f"POSTGRES_PASSWORD={password}",
                "-e", f"POSTGRES_DB={database}",
                "-p", f"{port}:5432",
                "postgres:16"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"Created and started container {container_name}")
                return True
            else:
                logger.error(f"Failed to create container: {result.stderr}")
                return False
                
    except Exception as e:
        logger.error(f"Error starting PostgreSQL container: {e}")
        return False


def stop_postgres_container(container_name: str = "spydb") -> bool:
    """Stop PostgreSQL container."""
    try:
        result = subprocess.run(
            ["docker", "stop", container_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info(f"Stopped container {container_name}")
            return True
        else:
            logger.error(f"Failed to stop container: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error stopping container: {e}")
        return False


def wait_for_postgres_ready(
    database_url: str, 
    max_wait_seconds: int = 30,
    check_interval: int = 1
) -> bool:
    """Wait for PostgreSQL to be ready to accept connections."""
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        if check_postgres_health(database_url, timeout=2):
            logger.info("PostgreSQL is ready")
            return True
        
        time.sleep(check_interval)
    
    logger.error(f"PostgreSQL not ready after {max_wait_seconds} seconds")
    return False


def verify_database_connection(database_url: str) -> bool:
    """Verify database connection and basic functionality."""
    try:
        parsed = parse_database_url(database_url)
        
        if parsed["scheme"].startswith("postgresql"):
            return check_postgres_health(database_url)
        
        elif parsed["scheme"] == "sqlite":
            # For SQLite, try to connect and create a test table
            import sqlite3
            import os
            
            # Extract path from SQLite URL (remove 'sqlite:///' prefix)
            db_path = database_url.replace('sqlite:///', '')
            
            # Ensure directory exists
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            return result[0] == 1
        
        return False
        
    except Exception as e:
        logger.error(f"Database connection verification failed: {e}")
        return False


def create_health_check_response(
    is_healthy: bool, 
    database_url: str
) -> Dict[str, Any]:
    """Create standardized health check response."""
    parsed = parse_database_url(database_url)
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": time.time(),
        "database": {
            "type": parsed["scheme"].split('+')[0],  # Remove psycopg2 suffix
            "host": parsed["host"] if parsed["host"] else "local",
            "port": parsed["port"],
            "database": parsed["database"],
            "connected": is_healthy
        }
    }


def startup_database_check(database_url: str) -> Dict[str, Any]:
    """Perform comprehensive database check during application startup."""
    try:
        parsed = parse_database_url(database_url)
        db_type = parsed["scheme"].split('+')[0]
        
        # Validate URL format
        if not validate_database_url(database_url):
            return {
                "success": False,
                "database_type": db_type,
                "error": "Invalid database URL format"
            }
        
        # Test connection
        is_connected = verify_database_connection(database_url)
        
        if is_connected:
            return {
                "success": True,
                "database_type": db_type,
                "host": parsed["host"] if parsed["host"] else "local",
                "port": parsed["port"],
                "database": parsed["database"]
            }
        else:
            return {
                "success": False,
                "database_type": db_type,
                "error": "Unable to connect to database"
            }
            
    except Exception as e:
        return {
            "success": False,
            "database_type": "unknown",
            "error": str(e)
        }


def is_docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def auto_start_postgres_if_needed(database_url: str) -> Tuple[bool, str]:
    """
    Auto-start PostgreSQL container if needed based on DATABASE_URL.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        parsed = parse_database_url(database_url)
        
        # Only auto-start for localhost PostgreSQL connections
        if (not parsed["scheme"].startswith("postgresql") or 
            parsed["host"] not in ["127.0.0.1", "localhost"]):
            return True, "Not a local PostgreSQL connection"
        
        # Check if Docker is available
        if not is_docker_available():
            return False, "Docker not available or not running"
        
        # Check if database is already accessible
        if check_postgres_health(database_url):
            return True, "PostgreSQL already accessible"
        
        # Try to start container
        container_name = "spydb"
        port = parsed["port"] or 5433
        
        if start_postgres_container(
            container_name=container_name,
            port=port,
            user=parsed["user"] or "spy",
            password=parsed["password"] or "pass", 
            database=parsed["database"] or "spy"
        ):
            # Wait for it to be ready
            if wait_for_postgres_ready(database_url, max_wait_seconds=30):
                return True, f"Successfully started and connected to PostgreSQL container"
            else:
                return False, "Container started but PostgreSQL not ready"
        else:
            return False, "Failed to start PostgreSQL container"
            
    except Exception as e:
        return False, f"Error during auto-start: {str(e)}"


# ============================================================================
# ENHANCED DATABASE CONNECTION LOGIC (Task 3)
# ============================================================================

# Import additional dependencies for intelligent connection logic
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import OperationalError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import docker
    from docker.errors import DockerException, NotFound
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class DatabaseResolver:
    """Centralized database resolution with caching and fallback logic."""
    
    def __init__(self):
        self._cached_config: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl_seconds = 300  # 5 minutes
    
    def resolve(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Resolve database configuration with caching.
        
        Args:
            force_refresh: Force refresh of cached configuration
            
        Returns:
            Dict containing database configuration and status
        """
        current_time = time.time()
        
        # Return cached config if valid and not forcing refresh
        if (not force_refresh and 
            self._cached_config and 
            self._cache_timestamp and
            (current_time - self._cache_timestamp) < self._cache_ttl_seconds):
            return self._cached_config
        
        # Resolve fresh configuration
        from .config import settings
        
        # Get preferred and fallback URLs
        preferred_url = settings.database_url
        fallback_url = "sqlite:///./spy_tracker.db"  # Default SQLite fallback
        
        # Resolve using the main logic
        config = resolve_database_url(preferred_url, fallback_url)
        
        # Cache the result
        self._cached_config = config
        self._cache_timestamp = current_time
        
        return config


def check_postgresql_availability_enhanced(host: str, port: int, user: str, password: str, database: str) -> Dict[str, Any]:
    """
    Enhanced PostgreSQL availability check with detailed diagnostics.
    
    Args:
        host: PostgreSQL host
        port: PostgreSQL port  
        user: Username
        password: Password
        database: Database name
        
    Returns:
        Dict with availability status and message
    """
    if not psycopg2:
        return {
            "available": False,
            "message": "psycopg2 not installed - PostgreSQL support unavailable"
        }
    
    try:
        # Attempt connection with short timeout
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=5  # 5 second timeout
        )
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "available": True,
            "message": f"PostgreSQL available at {host}:{port}",
            "version": version
        }
        
    except psycopg2.OperationalError as e:
        return {
            "available": False,
            "message": f"PostgreSQL connection failed: {str(e)}"
        }
    except Exception as e:
        return {
            "available": False,
            "message": f"Unexpected error checking PostgreSQL: {str(e)}"
        }


def check_postgres_container_status_enhanced(container_name: str = "spydb") -> Dict[str, Any]:
    """
    Enhanced Docker PostgreSQL container status check.
    
    Args:
        container_name: Name of PostgreSQL container
        
    Returns:
        Dict with container status and port information
    """
    if not DOCKER_AVAILABLE:
        return {
            "running": False,
            "port": None,
            "message": "Docker not available - container status unknown"
        }
    
    try:
        client = docker.from_env()
        
        try:
            container = client.containers.get(container_name)
            
            if container.status == "running":
                # Extract port mapping
                port_mapping = container.attrs.get("NetworkSettings", {}).get("Ports", {})
                postgres_port = port_mapping.get("5432/tcp")
                host_port = postgres_port[0]["HostPort"] if postgres_port else None
                
                return {
                    "running": True,
                    "port": host_port,
                    "message": f"Container {container_name} is running on port {host_port}"
                }
            else:
                return {
                    "running": False,
                    "port": None,
                    "message": f"Container {container_name} exists but status: {container.status}"
                }
                
        except NotFound:
            return {
                "running": False,
                "port": None,
                "message": f"Container {container_name} not found"
            }
            
    except DockerException as e:
        return {
            "running": False,
            "port": None,
            "message": f"Docker error: {str(e)}"
        }
    except Exception as e:
        return {
            "running": False,
            "port": None,
            "message": f"Unexpected error checking container: {str(e)}"
        }


def resolve_database_url(preferred_url: str, fallback_url: str) -> Dict[str, Any]:
    """
    Intelligently resolve database URL with PostgreSQL preference and SQLite fallback.
    
    Args:
        preferred_url: Preferred database URL (usually PostgreSQL)
        fallback_url: Fallback database URL (usually SQLite)
        
    Returns:
        Dict with resolved database configuration
        
    Raises:
        ValueError: If no valid database configuration can be determined
    """
    logger.info(f"Resolving database configuration...")
    logger.debug(f"Preferred URL type: {preferred_url.split(':')[0] if preferred_url else 'None'}")
    logger.debug(f"Fallback URL type: {fallback_url.split(':')[0] if fallback_url else 'None'}")
    
    # Try to parse preferred URL
    try:
        preferred_parsed = parse_database_url(preferred_url) if preferred_url else None
    except Exception as e:
        logger.warning(f"Invalid preferred URL: {e}")
        preferred_parsed = None
    
    # Try to parse fallback URL
    try:
        fallback_parsed = parse_database_url(fallback_url) if fallback_url else None
    except Exception as e:
        logger.warning(f"Invalid fallback URL: {e}")
        fallback_parsed = None
    
    # Ensure we have at least one valid URL
    if not preferred_parsed and not fallback_parsed:
        raise ValueError("No valid database configuration available")
    
    # If preferred URL is SQLite, use it directly
    if preferred_parsed and preferred_parsed["scheme"] == "sqlite":
        return {
            "database_url": preferred_url,
            "database_type": "sqlite",
            "preferred_database_used": True,
            "message": "SQLite configured as preferred database"
        }
    
    # If preferred URL is PostgreSQL, check availability
    if preferred_parsed and preferred_parsed["scheme"].startswith("postgresql"):
        logger.info("Checking PostgreSQL availability...")
        
        # Check container status first
        container_status = check_postgres_container_status_enhanced()
        logger.debug(f"Container status: {container_status}")
        
        # Check direct PostgreSQL connection
        pg_check = check_postgresql_availability_enhanced(
            host=preferred_parsed["host"] or "localhost",
            port=preferred_parsed["port"] or 5432,
            user=preferred_parsed["user"] or "postgres",
            password=preferred_parsed["password"] or "",
            database=preferred_parsed["database"] or "postgres"
        )
        logger.debug(f"PostgreSQL check: {pg_check}")
        
        if pg_check["available"]:
            return {
                "database_url": preferred_url,
                "database_type": "postgresql",
                "preferred_database_used": True,
                "message": f"PostgreSQL connected successfully: {pg_check['message']}",
                "container_status": container_status,
                "database_version": pg_check.get("version")
            }
        else:
            logger.warning(f"PostgreSQL not available: {pg_check['message']}")
            
            # Fall back to SQLite if available
            if fallback_parsed:
                return {
                    "database_url": fallback_url,
                    "database_type": "sqlite",
                    "preferred_database_used": False,
                    "message": f"Falling back to SQLite - PostgreSQL unavailable: {pg_check['message']}",
                    "container_status": container_status,
                    "fallback_reason": pg_check["message"]
                }
    
    # If we get here, use fallback if available
    if fallback_parsed:
        return {
            "database_url": fallback_url,
            "database_type": fallback_parsed["scheme"],
            "preferred_database_used": False,
            "message": "Using fallback database configuration"
        }
    
    # This shouldn't happen given our earlier check, but just in case
    raise ValueError("No valid database configuration could be resolved")


def get_connect_args(database_type: str) -> Dict[str, Any]:
    """
    Get appropriate connect_args for SQLAlchemy based on database type.
    
    Args:
        database_type: Type of database (sqlite, postgresql, etc.)
        
    Returns:
        Dict with connect_args for SQLAlchemy
    """
    if database_type == "sqlite":
        return {"check_same_thread": False}
    else:
        return {}


def create_engine_with_fallback(preferred_url: str, fallback_url: str) -> Dict[str, Any]:
    """
    Create SQLAlchemy engine with automatic fallback logic.
    
    Args:
        preferred_url: Preferred database URL
        fallback_url: Fallback database URL
        
    Returns:
        Dict with engine and configuration details
    """
    if not SQLALCHEMY_AVAILABLE:
        raise ImportError("SQLAlchemy not available - cannot create engine")
    
    # Resolve database configuration
    config = resolve_database_url(preferred_url, fallback_url)
    
    database_url = config["database_url"]
    database_type = config["database_type"]
    
    # Get appropriate connect_args
    connect_args = get_connect_args(database_type)
    
    try:
        # Create engine
        engine = create_engine(database_url, connect_args=connect_args)
        
        # Test connection
        with engine.connect() as conn:
            # Simple connectivity test
            if database_type == "sqlite":
                result = conn.execute(text("SELECT sqlite_version()"))
            elif database_type.startswith("postgresql"):
                result = conn.execute(text("SELECT version()"))
            else:
                result = conn.execute(text("SELECT 1"))
            
            version_info = result.fetchone()[0] if result else "Unknown"
        
        return {
            "engine": engine,
            "database_type": database_type,
            "database_url": database_url,
            "preferred_database_used": config["preferred_database_used"],
            "connection_successful": True,
            "database_version": version_info,
            "message": config["message"]
        }
        
    except OperationalError as e:
        logger.error(f"Failed to connect to {database_type}: {e}")
        
        # If this was the preferred database, try fallback
        if config["preferred_database_used"] and preferred_url != fallback_url:
            logger.info("Attempting fallback database...")
            return create_engine_with_fallback(fallback_url, fallback_url)
        else:
            # This was already the fallback, so we're out of options
            raise e


def verify_database_connectivity(engine: 'Engine', database_type: str) -> Dict[str, Any]:
    """
    Verify database connectivity and gather version information.
    
    Args:
        engine: SQLAlchemy engine
        database_type: Type of database
        
    Returns:
        Dict with connectivity status and information
    """
    start_time = time.time()
    
    try:
        with engine.connect() as conn:
            # Get database version
            if database_type == "sqlite":
                if SQLALCHEMY_AVAILABLE:
                    result = conn.execute(text("SELECT sqlite_version()"))
                else:
                    raise ImportError("SQLAlchemy not available")
                version_query = "SQLite"
            elif database_type.startswith("postgresql"):
                if SQLALCHEMY_AVAILABLE:
                    result = conn.execute(text("SELECT version()"))
                else:
                    raise ImportError("SQLAlchemy not available")
                version_query = "PostgreSQL"
            else:
                if SQLALCHEMY_AVAILABLE:
                    result = conn.execute(text("SELECT 1 as test"))
                else:
                    raise ImportError("SQLAlchemy not available")
                version_query = "Unknown"
            
            version_info = result.fetchone()[0] if result else "Unknown"
            connection_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "connected": True,
                "database_version": version_info,
                "connection_time_ms": round(connection_time, 2),
                "message": f"Successfully connected to {version_query} database"
            }
            
    except OperationalError as e:
        connection_time = (time.time() - start_time) * 1000
        return {
            "connected": False,
            "database_version": None,
            "connection_time_ms": round(connection_time, 2),
            "message": f"Database connection failed: {str(e)}"
        }


def get_database_status_message(status: Dict[str, Any]) -> str:
    """
    Generate user-friendly database status message.
    
    Args:
        status: Database status information
        
    Returns:
        Formatted status message
    """
    db_type = status.get("database_type", "unknown")
    preferred_used = status.get("preferred_database_used", False)
    version = status.get("database_version", "Unknown version")
    
    if db_type == "postgresql" and preferred_used:
        container_info = status.get("container_status", {})
        port = container_info.get("port", "unknown")
        
        return (f"✅ PostgreSQL database active on port {port}\n"
                f"   Version: {version}\n"
                f"   Container status: {container_info.get('message', 'Unknown')}")
    
    elif db_type == "sqlite" and not preferred_used:
        fallback_reason = status.get("fallback_reason", "PostgreSQL unavailable")
        
        return (f"⚠️  SQLite database active (fallback mode)\n"
                f"   Version: {version}\n"
                f"   Reason: {fallback_reason}\n"
                f"   Tip: Start PostgreSQL container for better performance")
    
    elif db_type == "sqlite" and preferred_used:
        return (f"✅ SQLite database active (configured)\n"
                f"   Version: {version}")
    
    else:
        return (f"❓ Database status: {db_type}\n"
                f"   Version: {version}\n"
                f"   Preferred used: {preferred_used}")


def log_database_status(status: Dict[str, Any]) -> None:
    """
    Log database status information.
    
    Args:
        status: Database status to log
    """
    db_type = status.get("database_type", "unknown")
    preferred = status.get("preferred_database_used", False)
    version = status.get("database_version", "unknown")
    connection_time = status.get("connection_time_ms", 0)
    
    if preferred:
        log_level = logging.INFO
        status_icon = "✅"
    else:
        log_level = logging.WARNING  
        status_icon = "⚠️"
    
    logger.log(log_level, 
               f"{status_icon} Database: {db_type.upper()} ({version}) "
               f"connected in {connection_time}ms - "
               f"Preferred: {'Yes' if preferred else 'No'}")


# Global resolver instance for caching
_database_resolver = DatabaseResolver()


def get_database_config(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get current database configuration with caching.
    
    Args:
        force_refresh: Force refresh of cached configuration
        
    Returns:
        Database configuration dict
    """
    return _database_resolver.resolve(force_refresh=force_refresh)