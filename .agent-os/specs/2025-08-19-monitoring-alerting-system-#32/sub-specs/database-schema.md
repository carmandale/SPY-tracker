# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-19-monitoring-alerting-system-#32/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Schema Changes

### New Tables

#### system_health
Stores system health metrics for historical analysis

```sql
CREATE TABLE system_health (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    component VARCHAR(50) NOT NULL, -- 'database', 'scheduler', 'api', 'ai_service'
    status VARCHAR(20) NOT NULL, -- 'healthy', 'degraded', 'failed'
    details JSONB, -- Component-specific metrics
    response_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_system_health_timestamp ON system_health(timestamp DESC);
CREATE INDEX idx_system_health_component_status ON system_health(component, status);
```

#### alert_history
Tracks all alerts sent and their resolution status

```sql
CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    alert_id UUID DEFAULT gen_random_uuid(),
    severity VARCHAR(20) NOT NULL, -- 'critical', 'warning', 'info'
    component VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'acknowledged', 'resolved'
    channel VARCHAR(50), -- 'email', 'sms', 'webhook'
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by VARCHAR(100),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_alert_history_status ON alert_history(status);
CREATE INDEX idx_alert_history_severity ON alert_history(severity);
CREATE INDEX idx_alert_history_sent_at ON alert_history(sent_at DESC);
```

#### job_execution_log
Detailed tracking of all scheduled job executions

```sql
CREATE TABLE job_execution_log (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) NOT NULL,
    job_name VARCHAR(255) NOT NULL,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL, -- 'pending', 'running', 'success', 'failed', 'skipped'
    duration_ms INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    output JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_job_execution_log_job_id ON job_execution_log(job_id);
CREATE INDEX idx_job_execution_log_status ON job_execution_log(status);
CREATE INDEX idx_job_execution_log_scheduled_time ON job_execution_log(scheduled_time DESC);
```

#### recovery_actions
Tracks automatic recovery attempts

```sql
CREATE TABLE recovery_actions (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL, -- 'db_reconnect', 'job_retry', 'cache_clear', 'fallback_prediction'
    component VARCHAR(50) NOT NULL,
    trigger_reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'initiated', 'success', 'failed'
    attempts INTEGER DEFAULT 1,
    error_details JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_recovery_actions_action_type ON recovery_actions(action_type);
CREATE INDEX idx_recovery_actions_status ON recovery_actions(status);
```

### New Columns

#### daily_predictions table modifications
```sql
ALTER TABLE daily_predictions 
ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_error TEXT,
ADD COLUMN IF NOT EXISTS health_check_passed BOOLEAN DEFAULT TRUE;
```

### Migrations

```python
# Alembic migration
"""Add monitoring and alerting tables

Revision ID: add_monitoring_tables
Revises: previous_revision
Create Date: 2025-08-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create system_health table
    op.create_table('system_health',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('component', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_system_health_timestamp', 'system_health', ['timestamp'], postgresql_using='btree')
    op.create_index('idx_system_health_component_status', 'system_health', ['component', 'status'])

    # Create alert_history table
    op.create_table('alert_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_id', postgresql.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('component', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(20), server_default='active', nullable=True),
        sa.Column('channel', sa.String(50), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledged_by', sa.String(100), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(100), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_alert_history_status', 'alert_history', ['status'])
    op.create_index('idx_alert_history_severity', 'alert_history', ['severity'])
    op.create_index('idx_alert_history_sent_at', 'alert_history', ['sent_at'])

    # Add remaining tables...

def downgrade():
    op.drop_table('recovery_actions')
    op.drop_table('job_execution_log')
    op.drop_table('alert_history')
    op.drop_table('system_health')
```

## Rationale

- **system_health**: Provides historical data for trend analysis and pattern detection
- **alert_history**: Audit trail of all alerts with resolution tracking for compliance
- **job_execution_log**: Detailed job history for debugging and performance optimization
- **recovery_actions**: Track self-healing attempts to improve recovery strategies
- **JSONB columns**: Flexible storage for component-specific data without schema changes
- **Indexes**: Optimized for common queries (recent data, status filters, component grouping)