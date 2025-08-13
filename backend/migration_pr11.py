#!/usr/bin/env python3
"""
Database migration for PR #11 - Prediction System Improvements

This script adds new columns to the AIPrediction table and creates
new tables for BaselineModel and ModelPerformance.

Run with: python migration_pr11.py
"""

import sqlite3
import sys
from pathlib import Path

def run_migration(db_path: str = "spy_tracker.db"):
    """Run the database migration for PR #11 changes."""
    
    print(f"🔧 Starting migration for {db_path}")
    
    # Check if database exists
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"❌ Database file {db_path} not found")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📋 Checking current schema...")
        
        # Check if new columns already exist in ai_predictions table
        cursor.execute("PRAGMA table_info(ai_predictions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns_needed = []
        expected_new_columns = [
            'interval_low', 'interval_high', 'interval_hit', 
            'source', 'model'
        ]
        
        for col in expected_new_columns:
            if col not in columns:
                new_columns_needed.append(col)
        
        if new_columns_needed:
            print(f"➕ Adding new columns to ai_predictions: {new_columns_needed}")
            
            # Add new columns to ai_predictions table
            column_definitions = {
                'interval_low': 'REAL',
                'interval_high': 'REAL', 
                'interval_hit': 'BOOLEAN',
                'source': 'VARCHAR',
                'model': 'VARCHAR'
            }
            
            for col in new_columns_needed:
                sql = f"ALTER TABLE ai_predictions ADD COLUMN {col} {column_definitions[col]}"
                print(f"   {sql}")
                cursor.execute(sql)
        else:
            print("✅ AIPrediction table already has new columns")
        
        # Check if baseline_models table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='baseline_models'")
        if not cursor.fetchone():
            print("➕ Creating baseline_models table")
            cursor.execute('''
                CREATE TABLE baseline_models (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR NOT NULL UNIQUE,
                    description VARCHAR,
                    parameters VARCHAR,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            print("✅ baseline_models table already exists")
        
        # Check if model_performance table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_performance'")
        if not cursor.fetchone():
            print("➕ Creating model_performance table")
            cursor.execute('''
                CREATE TABLE model_performance (
                    id INTEGER PRIMARY KEY,
                    date DATE NOT NULL,
                    model_name VARCHAR NOT NULL,
                    mae REAL,
                    rmse REAL,
                    hit_rate_1dollar REAL,
                    interval_coverage REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, model_name)
                )
            ''')
            cursor.execute('CREATE INDEX idx_model_performance_date ON model_performance(date)')
            cursor.execute('CREATE INDEX idx_model_performance_model ON model_performance(model_name)')
        else:
            print("✅ model_performance table already exists")
        
        # Commit changes
        conn.commit()
        print("💾 Migration completed successfully!")
        
        # Verify changes
        print("\n🔍 Verifying migration...")
        cursor.execute("PRAGMA table_info(ai_predictions)")
        ai_pred_columns = [column[1] for column in cursor.fetchall()]
        print(f"   ai_predictions columns: {len(ai_pred_columns)} total")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Database tables: {', '.join(tables)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def rollback_migration(db_path: str = "spy_tracker.db"):
    """Rollback the migration (limited - SQLite doesn't support DROP COLUMN easily)."""
    print("⚠️  Rollback for SQLite is limited. Restore from backup instead:")
    print(f"   cp spy_tracker_backup_*.db {db_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate database for PR #11 changes")
    parser.add_argument("--db", default="spy_tracker.db", help="Database file path")
    parser.add_argument("--rollback", action="store_true", help="Rollback migration")
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration(args.db)
    else:
        success = run_migration(args.db)
        sys.exit(0 if success else 1)