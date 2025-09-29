from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os


"""Application configuration.

Loads environment variables from the repository root `.env` first, then
optionally from a local `.env` in `backend/` if present. This ensures the
root `.env` is the single source of truth regardless of the working directory.
"""

# Load root .env, then backend/.env without overriding existing envs
_ROOT_DIR = Path(__file__).resolve().parents[2]
_BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT_DIR / ".env", override=False)
load_dotenv(_BACKEND_DIR / ".env", override=False)


class Settings(BaseSettings):
    app_name: str = "SPY TA Tracker"
    debug: bool = True
    database_url: str = "sqlite:///./spy_tracker.db"
    timezone: str = "America/Chicago"
    symbol: str = "SPY"
    frontend_origin: str = "*"
    openai_api_key: str = ""
    ai_lookback_days: int = 5
    openai_model: str = "gpt-5"
    openai_reasoning_effort: str = "minimal"
    openai_max_completion_tokens: int = 600
    openai_text_verbosity: str = "low"  # low|medium|high (Responses API)
    openai_temperature: float = 0.2
    
    # Server configuration
    api_port: int = 8000

    # Administrative security
    admin_api_token: str = ""
    
    # Database configuration flags
    use_intelligent_database_detection: bool = True
    fallback_to_sqlite: bool = True
    log_database_status: bool = True

    class Config:
        env_file = ".env"
    
    def get_resolved_database_config(self) -> dict:
        """
        Get intelligently resolved database configuration.
        
        Returns:
            Dict with resolved database URL and metadata
        """
        if not self.use_intelligent_database_detection:
            return {
                "database_url": self.database_url,
                "database_type": "sqlite" if self.database_url.startswith("sqlite") else "postgresql",
                "preferred_database_used": True,
                "message": "Using configured database URL (intelligent detection disabled)"
            }
        
        if not self.database_url:
            return {
                "database_url": self.database_url,
                "database_type": "sqlite" if self.database_url.startswith("sqlite") else "postgresql",
                "preferred_database_used": True,
                "message": "No DATABASE_URL configured; using default"
            }
        
        try:
            from .database_utils import get_database_config
            return get_database_config()
        except ImportError as e:
            # Fallback if database_utils not available
            return {
                "database_url": self.database_url,
                "database_type": "sqlite" if self.database_url.startswith("sqlite") else "postgresql",
                "preferred_database_used": True,
                "message": f"Using configured database URL (database_utils import failed: {e})"
            }


settings = Settings()


# Initialize database configuration resolution at startup
def _initialize_database_config():
    """Initialize and log database configuration at startup."""
    try:
        if settings.use_intelligent_database_detection:
            config = settings.get_resolved_database_config()
            
            if settings.log_database_status:
                from .database_utils import log_database_status, get_database_status_message
                
                # Log status for debugging
                log_database_status(config)
                
                # Print user-friendly message
                status_message = get_database_status_message(config)
                print("\n" + "="*60)
                print("DATABASE CONFIGURATION")
                print("="*60)
                print(status_message)
                print("="*60 + "\n")
                
        else:
            print(f"\n🔧 Database: Using configured URL (intelligent detection disabled)")
            print(f"   URL: {settings.database_url}\n")
            
    except Exception as e:
        print(f"\n⚠️ Warning: Could not initialize database configuration: {e}")
        print(f"   Falling back to configured URL: {settings.database_url}\n")


# Initialize on import (but allow override for testing)
if not os.getenv("SKIP_DATABASE_INIT"):
    _initialize_database_config()


