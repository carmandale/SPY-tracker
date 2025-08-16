# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-16-postgres-migration-#13/spec.md

> Created: 2025-08-16
> Version: 1.0.0

## Schema Changes

### Table Modifications

**No structural changes required** - The existing SQLAlchemy models are already PostgreSQL-compatible with proper type mappings.

### Index Optimizations

**New Indexes for PostgreSQL:**
```sql
-- Optimize daily prediction lookups
CREATE INDEX idx_daily_predictions_date_source ON daily_predictions(date, source);
CREATE INDEX idx_daily_predictions_created_at ON daily_predictions(created_at);

-- Optimize price log queries
CREATE INDEX idx_price_logs_date_checkpoint ON price_logs(date, checkpoint);
CREATE INDEX idx_price_logs_created_at ON price_logs(created_at);

-- Optimize AI prediction queries
CREATE INDEX idx_ai_predictions_date_checkpoint_source ON ai_predictions(date, checkpoint, source);
CREATE INDEX idx_ai_predictions_confidence ON ai_predictions(confidence DESC);
CREATE INDEX idx_ai_predictions_model ON ai_predictions(model);

-- Optimize model performance queries
CREATE INDEX idx_model_performance_date_model ON model_performance(date, model_name);
CREATE INDEX idx_model_performance_mae ON model_performance(mae);
```

### Constraint Enhancements

**Additional Constraints for Data Integrity:**
```sql
-- Ensure prediction confidence is valid
ALTER TABLE ai_predictions ADD CONSTRAINT chk_confidence_range 
CHECK (confidence >= 0.0 AND confidence <= 1.0);

-- Ensure prices are positive
ALTER TABLE daily_predictions ADD CONSTRAINT chk_positive_prices 
CHECK (
    (predLow IS NULL OR predLow > 0) AND
    (predHigh IS NULL OR predHigh > 0) AND
    (open IS NULL OR open > 0) AND
    (noon IS NULL OR noon > 0) AND
    (twoPM IS NULL OR twoPM > 0) AND
    (close IS NULL OR close > 0)
);

ALTER TABLE price_logs ADD CONSTRAINT chk_positive_price 
CHECK (price > 0);

-- Ensure valid prediction ranges
ALTER TABLE daily_predictions ADD CONSTRAINT chk_prediction_range 
CHECK (predLow IS NULL OR predHigh IS NULL OR predLow <= predHigh);
```

## Migration Specifications

### Data Type Mappings

**SQLite to PostgreSQL Type Conversions:**
```sql
-- SQLite -> PostgreSQL mappings (handled automatically by SQLAlchemy)
INTEGER -> SERIAL (for primary keys) or INTEGER
REAL/FLOAT -> DOUBLE PRECISION  
TEXT -> VARCHAR or TEXT
DATE -> DATE
DATETIME -> TIMESTAMP WITH TIME ZONE
BOOLEAN -> BOOLEAN
```

### Migration SQL Commands

**Export from SQLite:**
```sql
-- Extract data from existing SQLite database
.mode insert daily_predictions
.output daily_predictions.sql
SELECT * FROM daily_predictions;

.mode insert price_logs  
.output price_logs.sql
SELECT * FROM price_logs;

.mode insert ai_predictions
.output ai_predictions.sql  
SELECT * FROM ai_predictions;

.mode insert baseline_models
.output baseline_models.sql
SELECT * FROM baseline_models;

.mode insert model_performance
.output model_performance.sql
SELECT * FROM model_performance;
```

**Import to PostgreSQL:**
```sql
-- Create tables (handled by SQLAlchemy create_all())
-- Import data with proper escaping
\i daily_predictions.sql
\i price_logs.sql  
\i ai_predictions.sql
\i baseline_models.sql
\i model_performance.sql

-- Update sequences after data import
SELECT setval('daily_predictions_id_seq', (SELECT MAX(id) FROM daily_predictions));
SELECT setval('price_logs_id_seq', (SELECT MAX(id) FROM price_logs));
SELECT setval('ai_predictions_id_seq', (SELECT MAX(id) FROM ai_predictions));
SELECT setval('baseline_models_id_seq', (SELECT MAX(id) FROM baseline_models));
SELECT setval('model_performance_id_seq', (SELECT MAX(id) FROM model_performance));
```

### Data Integrity Verification

**Post-Migration Verification Queries:**
```sql
-- Verify row counts match
SELECT 'daily_predictions' as table_name, COUNT(*) as row_count FROM daily_predictions
UNION ALL
SELECT 'price_logs', COUNT(*) FROM price_logs  
UNION ALL
SELECT 'ai_predictions', COUNT(*) FROM ai_predictions
UNION ALL
SELECT 'baseline_models', COUNT(*) FROM baseline_models
UNION ALL
SELECT 'model_performance', COUNT(*) FROM model_performance;

-- Verify date ranges are preserved
SELECT 
    MIN(date) as earliest_prediction,
    MAX(date) as latest_prediction,
    COUNT(DISTINCT date) as unique_dates
FROM daily_predictions;

-- Verify foreign key relationships
SELECT COUNT(*) as orphaned_ai_predictions 
FROM ai_predictions ap 
LEFT JOIN daily_predictions dp ON ap.date = dp.date 
WHERE dp.date IS NULL;

-- Verify critical data points
SELECT 
    COUNT(*) as total_predictions,
    COUNT(predLow) as predictions_with_low,
    COUNT(predHigh) as predictions_with_high,
    COUNT(CASE WHEN rangeHit = true THEN 1 END) as successful_predictions
FROM daily_predictions;
```

## Performance Optimizations

### Query Optimization

**Frequently Used Query Patterns:**
```sql
-- Dashboard queries (optimized with indexes)
SELECT * FROM daily_predictions WHERE date = CURRENT_DATE;
SELECT * FROM ai_predictions WHERE date = CURRENT_DATE ORDER BY checkpoint;

-- Historical analysis (optimized with date indexes)  
SELECT * FROM daily_predictions 
WHERE date >= CURRENT_DATE - INTERVAL '20 days'
ORDER BY date DESC;

-- Performance metrics (optimized with composite indexes)
SELECT model_name, AVG(mae), AVG(hit_rate_1dollar)
FROM model_performance 
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY model_name;
```

### Connection Pool Configuration

**Production Settings:**
```python
# SQLAlchemy engine configuration for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Base connection pool size
    max_overflow=20,        # Additional connections allowed
    pool_timeout=30,        # Timeout for getting connection
    pool_recycle=1800,      # Recycle connections every 30 minutes
    pool_pre_ping=True,     # Verify connections before use
    echo=False              # Disable SQL logging in production
)
```

## Rationale

### Index Strategy
- **Date indexes**: Most queries filter by date for daily predictions and analysis
- **Composite indexes**: Common query patterns use multiple columns together
- **Confidence index**: AI prediction analysis often sorts by confidence scores
- **Model indexes**: Performance comparisons group by model type

### Constraint Strategy  
- **Business rule enforcement**: Prices must be positive, confidence within valid range
- **Data quality**: Prediction ranges must be logical (low <= high)
- **Referential integrity**: Maintained through foreign key relationships

### Migration Approach
- **Minimal downtime**: Export/import approach allows for quick cutover
- **Data verification**: Comprehensive checks ensure no data loss
- **Sequence synchronization**: PostgreSQL sequences must be updated after bulk import