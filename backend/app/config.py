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

    class Config:
        env_file = ".env"


settings = Settings()


