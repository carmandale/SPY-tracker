"""
Add prompt_version field to AIPrediction table
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Add prompt_version column to ai_predictions table if it doesn't exist."""
    
    database_url = os.getenv("DATABASE_URL", "sqlite:///./spy_tracker.db")
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        # Check if column already exists
        try:
            result = conn.execute(text("SELECT prompt_version FROM ai_predictions LIMIT 1"))
            print("✅ prompt_version column already exists")
            return
        except OperationalError:
            # Column doesn't exist, add it
            pass
        
        # Add the column
        try:
            conn.execute(text("""
                ALTER TABLE ai_predictions 
                ADD COLUMN prompt_version VARCHAR
            """))
            conn.commit()
            print("✅ Added prompt_version column to ai_predictions table")
        except Exception as e:
            print(f"❌ Error adding prompt_version column: {e}")
            raise

if __name__ == "__main__":
    run_migration()