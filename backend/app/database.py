from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings
import logging

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


# Create engine and session factory
engine = _create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
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


