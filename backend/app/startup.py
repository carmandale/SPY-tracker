"""
Application startup logic for SPY Tracker.
Handles database initialization, scheduler setup, and AI warmup.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from .config import settings
from .database import Base, engine, get_db
from .scheduler import start_scheduler


def initialize_database():
    """Create database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def setup_scheduler():
    """Initialize and start the scheduler."""
    return start_scheduler(get_db)


def warmup_ai_predictions():
    """
    Ensure today's AI band exists after 08:00 CST on weekdays.
    This is a best-effort warmup that won't block startup on failure.
    """
    try:
        from .scheduler import _run_ai_prediction
        from .models import DailyPrediction
        
        tz = ZoneInfo(settings.timezone)
        now_local = datetime.now(tz)
        
        # Only run on weekdays
        if now_local.weekday() >= 5:  # Saturday=5, Sunday=6
            return
        
        # Only auto-generate if we're past 08:00 local time
        past_8am = (now_local.hour, now_local.minute) >= (8, 0)
        if not past_8am:
            return
        
        # Check if we need to generate predictions
        db = next(get_db())
        try:
            existing = (
                db.query(DailyPrediction)
                .filter(DailyPrediction.date == now_local.date())
                .first()
            )
            # Skip if day is already locked by AI
            should_generate = not existing or not (
                getattr(existing, "locked", False) and 
                getattr(existing, "source", None) == "ai"
            )
        finally:
            db.close()
        
        if should_generate:
            # Run the same routine the 08:00 job uses; safe to call repeatedly
            try:
                _run_ai_prediction(get_db)
                print("✅ AI predictions generated for today")
            except Exception as e:
                print(f"⚠️ Could not generate AI predictions: {e}")
                
    except Exception as e:
        # Best-effort warmup only; ignore any import/timezone errors
        print(f"⚠️ AI warmup skipped: {e}")


def run_startup_tasks():
    """
    Run all startup tasks in order.
    Returns the scheduler instance for use in the app.
    """
    print("🚀 Starting SPY Tracker...")
    
    # Initialize database
    initialize_database()
    print("✅ Database initialized")
    
    # Setup scheduler
    scheduler = setup_scheduler()
    print(f"✅ Scheduler started with {len(scheduler.get_jobs())} jobs")
    
    # Warmup AI predictions if needed
    warmup_ai_predictions()
    
    print("🎯 SPY Tracker ready!")
    return scheduler