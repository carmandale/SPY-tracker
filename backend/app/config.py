from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SPY TA Tracker"
    debug: bool = True
    database_url: str = "sqlite:///./spy_tracker.db"
    timezone: str = "America/Chicago"
    symbol: str = "SPY"

    class Config:
        env_file = ".env"


settings = Settings()


