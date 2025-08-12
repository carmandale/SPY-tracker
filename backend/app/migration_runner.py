"""
Database Migration Runner for SPY TA Tracker
Handles schema changes and data cleanup operations safely.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MigrationRunner:
    """Manages database migrations with rollback capability."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations_dir = Path(__file__).parent / "migrations"
        
    def run_migration(self, migration_file: str) -> Dict[str, Any]:
        """
        Run a specific migration file with transaction safety.
        
        Returns:
            Dict with migration results and rollback info
        """
        migration_path = self.migrations_dir / migration_file
        
        if not migration_path.exists():
            raise FileNotFoundError(f"Migration file not found: {migration_file}")
        
        # Read migration SQL
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration in transaction
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # Ensure FK constraints
        
        try:
            # Start transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Execute migration
            conn.executescript(migration_sql)
            
            # Verify migration success
            verification_result = self._verify_migration_001(conn)
            
            if verification_result['success']:
                conn.execute("COMMIT")
                logger.info(f"Migration {migration_file} completed successfully")
                
                return {
                    'status': 'success',
                    'migration': migration_file,
                    'timestamp': datetime.now().isoformat(),
                    'verification': verification_result
                }
            else:
                conn.execute("ROLLBACK")
                raise Exception(f"Migration verification failed: {verification_result['error']}")
                
        except Exception as e:
            conn.execute("ROLLBACK")
            logger.error(f"Migration {migration_file} failed: {str(e)}")
            raise
        finally:
            conn.close()
    
    def _verify_migration_001(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Verify that migration 001 worked correctly."""
        try:
            # Check that unique constraint exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' 
                AND name='idx_ai_predictions_date_checkpoint'
            """)
            
            constraint_exists = cursor.fetchone() is not None
            
            if not constraint_exists:
                return {
                    'success': False,
                    'error': 'Unique constraint was not created'
                }
            
            # Check that duplicates were removed
            cursor = conn.execute("""
                SELECT date, checkpoint, COUNT(*) as count 
                FROM ai_predictions 
                GROUP BY date, checkpoint 
                HAVING COUNT(*) > 1
            """)
            
            remaining_duplicates = cursor.fetchall()
            
            if remaining_duplicates:
                return {
                    'success': False,
                    'error': f'Duplicates still exist: {remaining_duplicates}'
                }
            
            # Count total records after cleanup
            cursor = conn.execute("SELECT COUNT(*) FROM ai_predictions")
            total_records = cursor.fetchone()[0]
            
            return {
                'success': True,
                'constraint_created': True,
                'duplicates_removed': True,
                'remaining_records': total_records
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    def get_duplicate_analysis(self) -> Dict[str, Any]:
        """Analyze current duplicate situation before migration."""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Count duplicates by date/checkpoint
            cursor = conn.execute("""
                SELECT date, checkpoint, COUNT(*) as count, 
                       GROUP_CONCAT(id) as ids,
                       MIN(created_at) as first_created,
                       MAX(created_at) as last_created
                FROM ai_predictions 
                GROUP BY date, checkpoint 
                HAVING COUNT(*) > 1 
                ORDER BY date DESC, checkpoint
            """)
            
            duplicates = [
                {
                    'date': row[0],
                    'checkpoint': row[1],
                    'count': row[2],
                    'ids': row[3].split(','),
                    'first_created': row[4],
                    'last_created': row[5]
                }
                for row in cursor.fetchall()
            ]
            
            # Get total counts
            cursor = conn.execute("SELECT COUNT(*) FROM ai_predictions")
            total_records = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT date || '|' || checkpoint) 
                FROM ai_predictions
            """)
            unique_combinations = cursor.fetchone()[0]
            
            return {
                'total_records': total_records,
                'unique_combinations': unique_combinations,
                'duplicate_records': total_records - unique_combinations,
                'duplicate_groups': duplicates,
                'duplicate_count': len(duplicates)
            }
            
        finally:
            conn.close()


# CLI interface for running migrations
def run_ai_prediction_cleanup():
    """Run the AI prediction deduplication migration."""
    from .config import settings
    
    runner = MigrationRunner(settings.database_path)
    
    print("🔍 Analyzing duplicate AI predictions...")
    analysis = runner.get_duplicate_analysis()
    
    print(f"📊 Current State:")
    print(f"  - Total records: {analysis['total_records']}")
    print(f"  - Unique combinations: {analysis['unique_combinations']}")
    print(f"  - Duplicate records: {analysis['duplicate_records']}")
    print(f"  - Duplicate groups: {analysis['duplicate_count']}")
    
    if analysis['duplicate_count'] == 0:
        print("✅ No duplicates found - migration not needed!")
        return
    
    print(f"\n📋 Duplicate Groups:")
    for dup in analysis['duplicate_groups'][:5]:  # Show first 5
        print(f"  - {dup['date']} {dup['checkpoint']}: {dup['count']} records")
    
    if analysis['duplicate_count'] > 5:
        print(f"  ... and {analysis['duplicate_count'] - 5} more")
    
    print(f"\n🔧 Running migration to fix duplicates...")
    
    try:
        result = runner.run_migration("001_add_ai_prediction_unique_constraint.sql")
        
        print(f"✅ Migration completed successfully!")
        print(f"  - Remaining records: {result['verification']['remaining_records']}")
        print(f"  - Constraint created: {result['verification']['constraint_created']}")
        print(f"  - Duplicates removed: {result['verification']['duplicates_removed']}")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    run_ai_prediction_cleanup()