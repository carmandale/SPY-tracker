# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-17-database-alignment-#25/spec.md

> Created: 2025-08-17
> Version: 1.0.0

## Schema Overview

The database schema is already established and working correctly in production. This spec focuses on **environment alignment** rather than schema changes. The goal is to ensure local PostgreSQL matches production schema exactly.

## Current Production Schema

### Tables and Structure

**daily_predictions**
- Primary table for user and AI predictions
- Contains prediction data, actual results, and performance metrics
- **Status:** ✅ Working in production with 41+ records

**price_logs** 
- Intraday price capture at scheduled checkpoints
- Supports both manual and automated price logging
- **Status:** ✅ Working in production with automated captures

**ai_predictions**
- AI-generated predictions with confidence intervals
- Tracks GPT-5 model performance and accuracy
- **Status:** ✅ Working in production with daily AI predictions

**baseline_models**
- Configuration for statistical baseline prediction models
- **Status:** ✅ Schema ready, minimal data in production

**model_performance**
- Daily performance metrics for prediction models
- **Status:** ✅ Schema ready, tracking active

## Environment Alignment Tasks

### Local PostgreSQL Initialization

**Database Creation Script** (`db/init.sql`):
```sql
-- Create database and user (if not exists)
CREATE DATABASE spy;
CREATE USER spy WITH ENCRYPTED PASSWORD 'pass';
GRANT ALL PRIVILEGES ON DATABASE spy TO spy;

-- Switch to spy database
\c spy

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO spy;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO spy;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO spy;
```

**Table Creation via SQLAlchemy**:
- Tables automatically created via `Base.metadata.create_all(engine)`
- Alembic migration system available for future schema changes
- **No manual SQL required** - SQLAlchemy handles table creation

### Schema Verification Scripts

**Local Schema Validation**:
```python
def verify_local_schema():
    """Verify local PostgreSQL schema matches production."""
    expected_tables = [
        'daily_predictions',
        'price_logs', 
        'ai_predictions',
        'baseline_models',
        'model_performance'
    ]
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        
        local_tables = [row[0] for row in result]
        missing_tables = set(expected_tables) - set(local_tables)
        
        if missing_tables:
            raise Exception(f"Missing tables: {missing_tables}")
            
        return True
```

**Production Schema Inspection**:
```python
def inspect_production_schema():
    """Inspect production schema for comparison."""
    inspector = inspect(production_engine)
    tables = inspector.get_table_names()
    
    schema_info = {}
    for table in tables:
        columns = inspector.get_columns(table)
        indexes = inspector.get_indexes(table)
        schema_info[table] = {
            'columns': columns,
            'indexes': indexes
        }
    
    return schema_info
```

## Data Migration Strategy

### Production Data Export Structure

**Data Export Format**:
```json
{
    "metadata": {
        "export_date": "2025-08-17T10:00:00Z",
        "source": "production",
        "tables": ["daily_predictions", "price_logs", "ai_predictions"]
    },
    "data": {
        "daily_predictions": [
            {
                "id": 1,
                "date": "2025-08-15",
                "predLow": 580.00,
                "predHigh": 585.00,
                // ... full record
            }
        ],
        "price_logs": [...],
        "ai_predictions": [...]
    }
}
```

### Import Conflict Resolution

**Strategy Options**:
1. **Replace All**: Drop local data, import fresh production data
2. **Merge by Date**: Keep local data for dates not in production export
3. **Update Only**: Update existing records, add new ones
4. **Selective Import**: Import only specific date ranges or tables

**Implementation**:
```python
def import_data(data_file: str, strategy: str = "replace"):
    """Import production data with configurable conflict resolution."""
    
    if strategy == "replace":
        # Truncate tables and import fresh
        for table in ['daily_predictions', 'price_logs', 'ai_predictions']:
            conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    
    elif strategy == "merge":
        # Import only records that don't exist locally
        # Handle foreign key relationships properly
        
    elif strategy == "update":
        # Upsert records (INSERT ... ON CONFLICT UPDATE)
```

## Database Connectivity Requirements

### Connection String Formats

**Local PostgreSQL**:
```
postgresql://spy:pass@localhost:5433/spy
```

**Production PostgreSQL** (via Render):
```
postgresql://user:password@host:port/database
# Obtained via: render connect --service-type postgresql
```

### Connection Pooling Configuration

**Local Development**:
```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    max_overflow=10,
    pool_size=5
)
```

**Production Configuration** (already working):
- Connection pooling handled by Render managed PostgreSQL
- Application uses single connection per request
- No changes needed to existing production setup

## Testing and Validation

### Schema Consistency Tests

**Unit Tests**:
```python
def test_schema_consistency():
    """Test local schema matches expected structure."""
    # Verify all tables exist
    # Verify column types and constraints
    # Verify indexes exist
    
def test_data_import():
    """Test production data import functionality."""
    # Export small dataset from production
    # Import to clean local database
    # Verify data integrity and relationships
```

### Integration Tests

**Database Migration Tests**:
- Test clean PostgreSQL startup
- Test data import from various sources
- Test fallback to SQLite when PostgreSQL unavailable
- Test environment switching

**Production Access Tests**:
- Test Render CLI authentication
- Test read-only production access
- Test production data export functionality

## Backup and Recovery

### Local Database Backup

**Automatic Backups**:
```bash
# Daily backup of local development data
pg_dump postgresql://spy:pass@localhost:5433/spy > backup_$(date +%Y%m%d).sql
```

**Recovery Process**:
```bash
# Restore from backup
psql postgresql://spy:pass@localhost:5433/spy < backup_20250817.sql
```

### Production Data Export

**Regular Export Schedule**:
- Export production data weekly for local development
- Store exports with timestamps for versioning
- Include data validation checksums

**Export Security**:
- No sensitive production credentials in exports
- Clear labeling of production data
- Automatic cleanup of old export files