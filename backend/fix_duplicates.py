#!/usr/bin/env python3
"""
CLI script to fix AI prediction duplicates.
Run this to apply the database migration and cleanup.
"""

import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

try:
    from app.migration_runner import run_ai_prediction_cleanup
    
    if __name__ == "__main__":
        print("🔧 SPY TA Tracker - AI Prediction Duplicate Fix")
        print("=" * 50)
        print("")
        
        try:
            run_ai_prediction_cleanup()
            print("")
            print("🎉 Migration completed successfully!")
            print("✅ Your AI predictions are now deduplicated.")
            print("✅ Future duplicates are prevented by database constraints.")
            
        except Exception as e:
            print(f"")
            print(f"❌ Migration failed: {str(e)}")
            print("")
            print("🔍 Troubleshooting:")
            print("1. Make sure the backend server is not running")
            print("2. Ensure the database file exists and is writable")
            print("3. Check that no other processes are using the database")
            sys.exit(1)
            
except ImportError as e:
    print(f"❌ Could not import migration runner: {e}")
    print("Make sure you're running this from the backend directory")
    print("and all dependencies are installed.")
    sys.exit(1)