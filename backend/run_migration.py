#!/usr/bin/env python3
"""
Run database migration to add prompt_version column
This fixes the 500 errors on /ai/predictions/* endpoints
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to add prompt_version column"""
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    print(f"📊 Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Read migration SQL
        migration_sql = """
        -- Add prompt_version column if it doesn't exist
        ALTER TABLE ai_predictions 
        ADD COLUMN IF NOT EXISTS prompt_version VARCHAR(50);
        
        -- Set default value for existing rows
        UPDATE ai_predictions 
        SET prompt_version = 'v1.0.0' 
        WHERE prompt_version IS NULL;
        
        -- Add index for performance
        CREATE INDEX IF NOT EXISTS idx_ai_predictions_prompt_version 
        ON ai_predictions(prompt_version);
        """
        
        print("🔧 Running migration...")
        
        # Execute migration
        with engine.connect() as conn:
            conn.execute(text(migration_sql))
            conn.commit()
            
        print("✅ Migration completed successfully!")
        
        # Verify the column exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ai_predictions' 
                AND column_name = 'prompt_version'
            """))
            if result.fetchone():
                print("✅ Verified: prompt_version column exists")
                return True
            else:
                print("❌ Column not found after migration")
                return False
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)