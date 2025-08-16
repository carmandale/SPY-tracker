# Database Migration Guide

This guide covers migrating between SQLite and PostgreSQL, handling schema changes, and database maintenance.

## Table of Contents

- [SQLite to PostgreSQL Migration](#sqlite-to-postgresql-migration)
- [PostgreSQL to SQLite Migration](#postgresql-to-sqlite-migration)
- [Schema Migrations](#schema-migrations)
- [Data Backup and Restore](#data-backup-and-restore)
- [Troubleshooting Migrations](#troubleshooting-migrations)

## SQLite to PostgreSQL Migration

### Prerequisites

1. **Backup your SQLite database**:
   ```bash
   cp spy_tracker.db spy_tracker_backup_$(date +%Y%m%d).db
   ```

2. **Ensure PostgreSQL is running**:
   ```bash
   # Using Docker
   docker-compose up -d db
   
   # Or start manually
   ./start.sh  # Will auto-start Postgres
   ```

### Method 1: Fresh Start (Recommended for Development)

If you don't need to preserve existing data:

1. **Update environment configuration**:
   ```bash
   # In .env or backend/.env
   DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy
   ```

2. **Start the application**:
   ```bash
   ./start.sh
   ```

3. **Verify tables are created**:
   ```bash
   docker-compose exec db psql -U spy -d spy -c "\dt"
   ```

### Method 2: Data Migration

If you need to preserve existing data:

1. **Export SQLite data**:
   ```bash
   cd backend
   source .venv/bin/activate
   
   python -c "
   import sqlite3
   import json
   from datetime import datetime
   
   # Connect to SQLite
   conn = sqlite3.connect('spy_tracker.db')
   conn.row_factory = sqlite3.Row
   cursor = conn.cursor()
   
   # Export daily_predictions
   cursor.execute('SELECT * FROM daily_predictions')
   predictions = [dict(row) for row in cursor.fetchall()]
   
   # Export price_logs
   cursor.execute('SELECT * FROM price_logs')
   price_logs = [dict(row) for row in cursor.fetchall()]
   
   # Export ai_predictions if exists
   try:
       cursor.execute('SELECT * FROM ai_predictions')
       ai_predictions = [dict(row) for row in cursor.fetchall()]
   except:
       ai_predictions = []
   
   # Save to JSON
   data = {
       'daily_predictions': predictions,
       'price_logs': price_logs,
       'ai_predictions': ai_predictions,
       'exported_at': datetime.now().isoformat()
   }
   
   with open('sqlite_export.json', 'w') as f:
       json.dump(data, f, indent=2, default=str)
   
   print(f'Exported {len(predictions)} predictions and {len(price_logs)} price logs')
   conn.close()
   "
   ```

2. **Switch to PostgreSQL**:
   ```bash
   # Update .env
   DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy
   ```

3. **Import data to PostgreSQL**:
   ```bash
   python -c "
   import json
   import psycopg2
   from psycopg2.extras import RealDictCursor
   from datetime import datetime
   import os
   
   # Load exported data
   with open('sqlite_export.json', 'r') as f:
       data = json.load(f)
   
   # Connect to PostgreSQL
   db_url = os.getenv('DATABASE_URL', 'postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy')
   conn_str = db_url.replace('postgresql+psycopg2://', 'postgresql://')
   conn = psycopg2.connect(conn_str)
   cursor = conn.cursor(cursor_factory=RealDictCursor)
   
   # Import daily_predictions
   for pred in data['daily_predictions']:
       cursor.execute('''
           INSERT INTO daily_predictions 
           (date, preMarket, predLow, predHigh, bias, volCtx, dayType, keyLevels, notes, 
            open, noon, twoPM, close, realizedLow, realizedHigh, rangeHit, absErrorToClose, 
            source, locked, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (date) DO NOTHING
       ''', (
           pred.get('date'), pred.get('preMarket'), pred.get('predLow'), pred.get('predHigh'),
           pred.get('bias'), pred.get('volCtx'), pred.get('dayType'), pred.get('keyLevels'),
           pred.get('notes'), pred.get('open'), pred.get('noon'), pred.get('twoPM'),
           pred.get('close'), pred.get('realizedLow'), pred.get('realizedHigh'),
           pred.get('rangeHit'), pred.get('absErrorToClose'), pred.get('source'),
           pred.get('locked'), pred.get('created_at'), pred.get('updated_at')
       ))
   
   # Import price_logs
   for log in data['price_logs']:
       cursor.execute('''
           INSERT INTO price_logs (date, checkpoint, price, created_at)
           VALUES (%s, %s, %s, %s)
           ON CONFLICT DO NOTHING
       ''', (log.get('date'), log.get('checkpoint'), log.get('price'), log.get('created_at')))
   
   # Import ai_predictions if any
   for ai_pred in data['ai_predictions']:
       cursor.execute('''
           INSERT INTO ai_predictions 
           (date, checkpoint, predicted_price, confidence, reasoning, market_context,
            actual_price, prediction_error, interval_low, interval_high, interval_hit,
            source, model, prompt_version, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (date, checkpoint) DO NOTHING
       ''', (
           ai_pred.get('date'), ai_pred.get('checkpoint'), ai_pred.get('predicted_price'),
           ai_pred.get('confidence'), ai_pred.get('reasoning'), ai_pred.get('market_context'),
           ai_pred.get('actual_price'), ai_pred.get('prediction_error'), ai_pred.get('interval_low'),
           ai_pred.get('interval_high'), ai_pred.get('interval_hit'), ai_pred.get('source'),
           ai_pred.get('model'), ai_pred.get('prompt_version'), ai_pred.get('created_at'),
           ai_pred.get('updated_at')
       ))
   
   conn.commit()
   cursor.close()
   conn.close()
   
   print('Migration completed successfully!')
   "
   ```

4. **Verify migration**:
   ```bash
   docker-compose exec db psql -U spy -d spy -c "
   SELECT 'daily_predictions' as table_name, count(*) FROM daily_predictions
   UNION ALL
   SELECT 'price_logs', count(*) FROM price_logs
   UNION ALL  
   SELECT 'ai_predictions', count(*) FROM ai_predictions;
   "
   ```

## PostgreSQL to SQLite Migration

### Use Case
Useful for local development, testing, or creating portable databases.

### Method 1: Export and Import

1. **Export from PostgreSQL**:
   ```bash
   # Export data to SQL dump
   docker-compose exec db pg_dump -U spy -d spy \
     --data-only \
     --insert \
     --column-inserts \
     > postgres_export.sql
   ```

2. **Create new SQLite database**:
   ```bash
   # Update .env
   DATABASE_URL=sqlite:///./spy_tracker_new.db
   
   # Start app to create tables
   ./start.sh
   ```

3. **Convert and import data**:
   ```bash
   # Convert PostgreSQL dump to SQLite-compatible format
   python -c "
   import re
   import sqlite3
   
   # Read PostgreSQL dump
   with open('postgres_export.sql', 'r') as f:
       sql_content = f.read()
   
   # Simple conversions for SQLite
   sql_content = re.sub(r'true', '1', sql_content)
   sql_content = re.sub(r'false', '0', sql_content)
   sql_content = re.sub(r'::timestamp.*?', '', sql_content)
   sql_content = re.sub(r'::.*?\\b', '', sql_content)
   
   # Connect to SQLite and execute
   conn = sqlite3.connect('spy_tracker_new.db')
   
   # Split and execute statements
   statements = sql_content.split(';')
   for stmt in statements:
       stmt = stmt.strip()
       if stmt and 'INSERT INTO' in stmt.upper():
           try:
               conn.execute(stmt)
           except Exception as e:
               print(f'Skipped statement due to error: {e}')
   
   conn.commit()
   conn.close()
   print('SQLite migration completed')
   "
   ```

### Method 2: Programmatic Migration

```bash
python -c "
import os
import psycopg2
import sqlite3
from psycopg2.extras import RealDictCursor

# Connect to PostgreSQL
pg_conn = psycopg2.connect('postgresql://spy:pass@127.0.0.1:5433/spy')
pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)

# Connect to SQLite
sqlite_conn = sqlite3.connect('spy_tracker_migrated.db')
sqlite_cursor = sqlite_conn.cursor()

# Create tables (run app first or copy schema)
tables = ['daily_predictions', 'price_logs', 'ai_predictions']

for table in tables:
    try:
        pg_cursor.execute(f'SELECT * FROM {table}')
        rows = pg_cursor.fetchall()
        
        if rows:
            columns = rows[0].keys()
            placeholders = ', '.join(['?' for _ in columns])
            
            for row in rows:
                values = [row[col] for col in columns]
                sqlite_cursor.execute(
                    f'INSERT OR IGNORE INTO {table} ({", ".join(columns)}) VALUES ({placeholders})',
                    values
                )
            
            print(f'Migrated {len(rows)} rows from {table}')
    except Exception as e:
        print(f'Error migrating {table}: {e}')

sqlite_conn.commit()
pg_conn.close()
sqlite_conn.close()
print('Migration to SQLite completed')
"
```

## Schema Migrations

### Automatic Schema Management

SPY TA Tracker automatically creates and updates database schema on startup:

```python
# In app/startup.py
from .database import create_tables
create_tables()  # Creates all tables if they don't exist
```

### Manual Schema Updates

For complex schema changes, you may need manual migrations:

1. **Create migration script**:
   ```bash
   # Create backend/migrations/add_new_column.py
   python -c "
   import os
   from sqlalchemy import text
   from app.database import get_engine
   
   def migrate():
       engine = get_engine()
       with engine.connect() as conn:
           # Add new column
           conn.execute(text('''
               ALTER TABLE daily_predictions 
               ADD COLUMN IF NOT EXISTS new_field VARCHAR(255)
           '''))
           conn.commit()
           print('Migration completed: added new_field column')
   
   if __name__ == '__main__':
       migrate()
   "
   ```

2. **Run migration**:
   ```bash
   cd backend
   source .venv/bin/activate
   python migrations/add_new_column.py
   ```

### Schema Versioning

Track schema changes in your migrations:

```python
# backend/migrations/schema_version.py
SCHEMA_VERSION = "1.2.0"

MIGRATIONS = {
    "1.0.0": "Initial schema",
    "1.1.0": "Added AI predictions table", 
    "1.2.0": "Added model performance tracking"
}

def get_current_version():
    # Check database for version table
    pass

def apply_migration(from_version, to_version):
    # Apply specific migration
    pass
```

## Data Backup and Restore

### PostgreSQL Backup

```bash
# Full database backup
docker-compose exec db pg_dump -U spy -d spy > backup_$(date +%Y%m%d_%H%M%S).sql

# Schema only
docker-compose exec db pg_dump -U spy -d spy --schema-only > schema_backup.sql

# Data only
docker-compose exec db pg_dump -U spy -d spy --data-only > data_backup.sql

# Compressed backup
docker-compose exec db pg_dump -U spy -d spy | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### PostgreSQL Restore

```bash
# Restore full backup
docker-compose exec -T db psql -U spy -d spy < backup_20231215_143022.sql

# Restore from compressed backup
gunzip -c backup_20231215_143022.sql.gz | docker-compose exec -T db psql -U spy -d spy

# Restore to new database
docker-compose exec db createdb -U spy spy_restored
docker-compose exec -T db psql -U spy -d spy_restored < backup_20231215_143022.sql
```

### SQLite Backup

```bash
# Simple file copy
cp spy_tracker.db spy_tracker_backup_$(date +%Y%m%d).db

# SQL dump
sqlite3 spy_tracker.db .dump > sqlite_backup_$(date +%Y%m%d).sql

# Restore from dump
sqlite3 spy_tracker_restored.db < sqlite_backup_20231215.sql
```

### Automated Backup Script

```bash
#!/bin/bash
# backup_database.sh

set -e

DB_TYPE=${1:-"postgres"}  # postgres or sqlite
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

if [ "$DB_TYPE" = "postgres" ]; then
    echo "Backing up PostgreSQL database..."
    docker-compose exec db pg_dump -U spy -d spy | gzip > $BACKUP_DIR/postgres_backup_$DATE.sql.gz
    echo "Backup saved: $BACKUP_DIR/postgres_backup_$DATE.sql.gz"
elif [ "$DB_TYPE" = "sqlite" ]; then
    echo "Backing up SQLite database..."
    cp spy_tracker.db $BACKUP_DIR/sqlite_backup_$DATE.db
    echo "Backup saved: $BACKUP_DIR/sqlite_backup_$DATE.db"
fi

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*backup_*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*backup_*.db" -mtime +30 -delete

echo "Backup completed successfully"
```

## Troubleshooting Migrations

### Common Issues

#### 1. Connection Errors During Migration

**Problem**: Can't connect to database during migration
**Solution**: Verify database is running and connection string is correct

```bash
# Test PostgreSQL connection
docker-compose exec db pg_isready -U spy -d spy

# Test SQLite file permissions
ls -la spy_tracker.db
```

#### 2. Data Type Mismatches

**Problem**: Data types don't match between SQLite and PostgreSQL
**Solution**: Handle type conversions in migration script

```python
# Common type conversions
conversions = {
    'INTEGER': lambda x: int(x) if x is not None else None,
    'REAL': lambda x: float(x) if x is not None else None,
    'TEXT': lambda x: str(x) if x is not None else None,
    'BOOLEAN': lambda x: bool(x) if x is not None else None
}
```

#### 3. Foreign Key Constraints

**Problem**: Foreign key violations during import
**Solution**: Disable constraints temporarily

```sql
-- PostgreSQL
SET session_replication_role = replica;
-- Your import statements here
SET session_replication_role = DEFAULT;

-- SQLite
PRAGMA foreign_keys = OFF;
-- Your import statements here
PRAGMA foreign_keys = ON;
```

#### 4. Large Dataset Migration

**Problem**: Migration times out on large datasets
**Solution**: Batch the migration

```python
def migrate_in_batches(source_cursor, dest_cursor, table, batch_size=1000):
    offset = 0
    while True:
        source_cursor.execute(f"SELECT * FROM {table} LIMIT {batch_size} OFFSET {offset}")
        rows = source_cursor.fetchall()
        
        if not rows:
            break
            
        # Insert batch
        for row in rows:
            # Insert logic here
            pass
        
        offset += batch_size
        print(f"Migrated {offset} rows from {table}")
```

#### 5. Schema Conflicts

**Problem**: Table already exists with different schema
**Solution**: Compare and reconcile schemas

```python
def compare_schemas(db1_cursor, db2_cursor, table):
    # Get column info from both databases
    db1_cursor.execute(f"PRAGMA table_info({table})")  # SQLite
    db2_cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table}'
    """)  # PostgreSQL
    
    # Compare and report differences
    pass
```

### Migration Rollback

If migration fails, you can rollback:

```bash
# PostgreSQL - restore from backup
docker-compose exec -T db psql -U spy -d spy < backup_before_migration.sql

# SQLite - restore backup file
cp spy_tracker_backup_before_migration.db spy_tracker.db

# Docker - recreate container and volume
docker-compose down -v
docker-compose up -d db
```

### Validation After Migration

Always validate your migration:

```bash
# Check record counts
python -c "
import sqlite3
import psycopg2

# Count records in both databases
sqlite_conn = sqlite3.connect('spy_tracker.db')
pg_conn = psycopg2.connect('postgresql://spy:pass@127.0.0.1:5433/spy')

tables = ['daily_predictions', 'price_logs', 'ai_predictions']

for table in tables:
    sqlite_count = sqlite_conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    pg_count = pg_conn.cursor().execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    
    print(f'{table}: SQLite={sqlite_count}, PostgreSQL={pg_count}')
    
    if sqlite_count != pg_count:
        print(f'⚠️  Record count mismatch in {table}')
    else:
        print(f'✅ {table} migration verified')
"
```

For additional help with migrations, see the main [POSTGRES_SETUP.md](./POSTGRES_SETUP.md) guide.