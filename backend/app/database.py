from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import DBAPIError, DisconnectionError, OperationalError
from contextlib import contextmanager
from .config import settings
import logging
import time

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


# Initialize database engine with intelligent connection logic
def _create_database_engine():
    """Create database engine with intelligent fallback logic."""
    try:
        if settings.use_intelligent_database_detection:
            from .database_utils import create_engine_with_fallback
            
            # Get resolved configuration
            config = settings.get_resolved_database_config()
            database_url = config["database_url"]
            fallback_url = "sqlite:///./spy_tracker.db"
            
            # Create engine with fallback
            engine_result = create_engine_with_fallback(database_url, fallback_url)
            return engine_result["engine"]
            
        else:
            # Use traditional direct engine creation
            connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
            return create_engine(settings.database_url, connect_args=connect_args)
            
    except Exception as e:
        logger.error(f"Failed to create database engine with intelligent logic: {e}")
        logger.info("Falling back to direct engine creation")
        
        # Fallback to direct engine creation
        connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
        return create_engine(settings.database_url, connect_args=connect_args)


# Create engine and session factory with better pool settings
def _configure_engine_pool(engine_kwargs: dict) -> dict:
    """Configure connection pool settings based on database type."""
    db_url = settings.database_url
    
    if db_url.startswith("postgresql"):
        # PostgreSQL specific pool settings
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "pool_pre_ping": True,  # Verify connections before using
        })
    
    return engine_kwargs

# Update engine creation
engine = _create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Add connection pool listeners for PostgreSQL
if not str(engine.url).startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Set session parameters on connect."""
        try:
            with dbapi_conn.cursor() as cursor:
                # Set statement timeout to prevent stuck queries
                cursor.execute("SET statement_timeout = '30s'")
                # Set lock timeout to prevent stuck locks  
                cursor.execute("SET lock_timeout = '10s'")
                # Set idle in transaction timeout
                cursor.execute("SET idle_in_transaction_session_timeout = '60s'")
        except Exception as e:
            logger.warning(f"Failed to set session parameters: {e}")

    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """Verify connection is still valid on checkout."""
        try:
            # Try to execute a simple query
            with dbapi_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            # Connection is broken, raise DisconnectionError to trigger reconnect
            raise DisconnectionError("Connection failed on checkout")


def get_db():
    """Dependency to get database session with proper error handling."""
    db = SessionLocal()
    try:
        # Verify connection is working
        db.execute(text("SELECT 1"))
        yield db
        db.commit()  # Commit any pending transactions
    except OperationalError as e:
        logger.error(f"Database operational error: {e}")
        db.rollback()  # Always rollback on error
        # Try to recover
        try:
            engine.dispose()  # Reset connection pool
            logger.info("Reset connection pool after operational error")
        except Exception:
            pass
        raise
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()  # Always rollback on error
        raise
    finally:
        try:
            db.close()
        except Exception:
            pass  # Ignore close errors


@contextmanager
def get_db_context():
    """Context manager for database sessions with automatic rollback."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_database_info():
    """Get current database configuration information."""
    try:
        config = settings.get_resolved_database_config()
        return {
            "engine_url": str(engine.url),
            "database_type": config.get("database_type", "unknown"),
            "preferred_database_used": config.get("preferred_database_used", False),
            "message": config.get("message", "No status message available")
        }
    except Exception as e:
        return {
            "engine_url": str(engine.url),
            "database_type": "unknown",
            "preferred_database_used": None,
            "message": f"Error getting database info: {e}"
        }


def verify_database_connection():
    """Verify that database connection is working."""
    try:
        from .database_utils import verify_database_connectivity
        
        # Determine database type from URL
        db_url = str(engine.url)
        if db_url.startswith("sqlite"):
            db_type = "sqlite"
        elif db_url.startswith("postgresql"):
            db_type = "postgresql"
        else:
            db_type = "unknown"
        
        return verify_database_connectivity(engine, db_type)
        
    except Exception as e:
        return {
            "connected": False,
            "database_version": None,
            "connection_time_ms": 0,
            "message": f"Verification failed: {e}"
        }


