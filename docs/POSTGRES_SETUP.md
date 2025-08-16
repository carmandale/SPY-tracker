# PostgreSQL Development Setup Guide

This guide covers the complete PostgreSQL workflow for SPY TA Tracker development, from local development to production deployment.

## Table of Contents

- [Quick Start](#quick-start)
- [Database Configuration Options](#database-configuration-options)
- [Docker Compose Workflow](#docker-compose-workflow)
- [Manual Setup](#manual-setup)
- [Environment Configuration](#environment-configuration)
- [Database Migrations](#database-migrations)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

## Quick Start

### Option 1: Automated Setup (Recommended)

The fastest way to get started with Postgres is using the automatic setup:

```bash
# Start everything with automatic Postgres setup
./start.sh
```

This script will:
- Auto-detect if Postgres is needed
- Start a local Postgres container on port 5433
- Configure the backend to use Postgres automatically
- Start both frontend and backend servers

### Option 2: Docker Compose

```bash
# Start just the database
docker-compose up db

# Start database with Adminer (web UI)
docker-compose --profile tools up db adminer

# Start the full stack (database + app)
docker-compose --profile full up
```

## Database Configuration Options

SPY TA Tracker supports both SQLite and PostgreSQL:

### SQLite (Default for quick testing)
```bash
DATABASE_URL=sqlite:///./spy_tracker.db
```

### PostgreSQL (Recommended for development/production)
```bash
# Local development (default in start.sh)
DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy

# Docker internal
DATABASE_URL=postgresql+psycopg2://spy:pass@db:5432/spy

# Production (use environment-specific values)
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
```

## Docker Compose Workflow

### Services Overview

The `docker-compose.yml` defines three services:

1. **`db`** - PostgreSQL 16 database (always available)
2. **`adminer`** - Web database administration tool (profile: `tools`)
3. **`app`** - Full application container (profile: `full`)

### Development Workflows

#### 1. Database Only (Most Common)

Start just the Postgres database for local development:

```bash
docker-compose up db
```

This provides:
- PostgreSQL on `localhost:5433`
- Persistent data in `db_data` volume
- Health checks to ensure database readiness

Then run your local development servers:
```bash
./start.sh  # Will detect and use the running Postgres container
```

#### 2. Database + Admin Tools

Start database with Adminer web interface:

```bash
docker-compose --profile tools up db adminer
```

Access Adminer at: http://localhost:8080
- **System:** PostgreSQL
- **Server:** db:5432
- **Username:** spy  
- **Password:** pass
- **Database:** spy

#### 3. Full Containerized Stack

Run everything in containers:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key_here

# Start full stack
docker-compose --profile full up
```

This provides:
- Database on `localhost:5433`
- Application on `localhost:8000`
- All services networked together

### Docker Compose Commands

```bash
# Start services in background
docker-compose up -d db

# View logs
docker-compose logs -f db

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache

# Access database directly
docker-compose exec db psql -U spy -d spy
```

## Manual Setup

If you prefer not to use Docker, you can install PostgreSQL directly:

### macOS (Homebrew)

```bash
# Install PostgreSQL
brew install postgresql@16

# Start service
brew services start postgresql@16

# Create user and database
createuser -s spy
createdb -O spy spy
psql -d spy -c "ALTER USER spy WITH PASSWORD 'pass';"
```

### Ubuntu/Debian

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql-16 postgresql-contrib

# Switch to postgres user
sudo -i -u postgres

# Create user and database
createuser --interactive spy
createdb spy
psql -c "ALTER USER spy WITH PASSWORD 'pass';"
```

### Configuration

After manual installation, update your environment:

```bash
# In backend/.env or root .env
DATABASE_URL=postgresql+psycopg2://spy:pass@localhost:5432/spy
```

## Environment Configuration

### Environment File Examples

#### Root `.env` (Primary Configuration)
```bash
# Database Configuration
DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy

# Application Settings
APP_NAME=SPY TA Tracker
DEBUG=true
TIMEZONE=America/Chicago
SYMBOL=SPY
FRONTEND_ORIGIN=*

# OpenAI Configuration (optional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-5
OPENAI_REASONING_EFFORT=minimal
```

#### Backend `.env` (Overrides)
```bash
# Backend-specific overrides (optional)
DATABASE_URL=postgresql+psycopg2://spy:pass@localhost:5432/spy
DEBUG=false
```

#### Frontend `.env.local`
```bash
# Frontend development
PORT=3000
VITE_API_URL=/
```

### Environment Priority

Environment variables are loaded in this order (later values override earlier):

1. System environment variables
2. Root `.env` file
3. `backend/.env` file (backend-specific overrides)
4. `.env.local` (frontend-specific)

## Database Migrations

### Automatic Migration

The application automatically handles database schema creation:

```python
# Backend startup creates tables automatically
from app.database import create_tables
create_tables()
```

### Manual Migration

If you need to run migrations manually:

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate

# Run Python to create tables
python -c "
from app.database import create_tables
create_tables()
print('✅ Database tables created')
"
```

### Schema Management

Current tables:
- `daily_predictions` - User predictions and results
- `price_logs` - Captured market prices
- `ai_predictions` - AI model predictions
- `baseline_models` - Statistical model configurations
- `model_performance` - Model accuracy metrics

## Troubleshooting

### Common Issues

#### 1. Port Conflicts

**Problem:** Port 5432 already in use
**Solution:** The docker-compose uses port 5433 to avoid conflicts

```bash
# Check what's using port 5432
lsof -i :5432

# Use the mapped port 5433
psql -h localhost -p 5433 -U spy -d spy
```

#### 2. Container Won't Start

**Problem:** Database container fails to start
**Solution:** Check logs and clean up if needed

```bash
# Check logs
docker-compose logs db

# Clean up and restart
docker-compose down -v
docker-compose up db
```

#### 3. Connection Refused

**Problem:** Application can't connect to database
**Solution:** Verify database is running and connection string

```bash
# Test connection
docker-compose exec db pg_isready -U spy -d spy

# Check connection string
echo $DATABASE_URL
```

#### 4. Permission Denied

**Problem:** Database access denied
**Solution:** Verify credentials and user permissions

```bash
# Reset user password
docker-compose exec db psql -U spy -d spy -c "ALTER USER spy WITH PASSWORD 'pass';"

# Verify connection
docker-compose exec db psql -U spy -d spy -c "SELECT current_user;"
```

### Health Checks

The Docker setup includes health checks:

```bash
# Check database health
docker-compose ps

# Manual health check
docker-compose exec db pg_isready -U spy -d spy
```

### Data Persistence

Database data is stored in a Docker volume:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect conakry_db_data

# Backup data
docker-compose exec db pg_dump -U spy spy > backup.sql

# Restore data
docker-compose exec -T db psql -U spy spy < backup.sql
```

## Production Considerations

### Security

#### 1. Strong Passwords
```bash
# Generate secure password
openssl rand -base64 32

# Use in production
DATABASE_URL=postgresql+psycopg2://spy:SECURE_PASSWORD@host:5432/spy
```

#### 2. SSL/TLS Connection
```bash
# Production with SSL
DATABASE_URL=postgresql+psycopg2://spy:password@host:5432/spy?sslmode=require
```

#### 3. Limited Permissions
```sql
-- Create read-only user for reporting
CREATE USER spy_readonly WITH PASSWORD 'readonly_pass';
GRANT CONNECT ON DATABASE spy TO spy_readonly;
GRANT USAGE ON SCHEMA public TO spy_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO spy_readonly;
```

### Performance

#### 1. Connection Pooling
```python
# In production, use connection pooling
DATABASE_URL=postgresql+psycopg2://spy:pass@host:5432/spy?pool_size=20&max_overflow=30
```

#### 2. Database Tuning
```sql
-- Example production settings (adjust based on your hardware)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

### Backup Strategy

#### 1. Automated Backups
```bash
#!/bin/bash
# backup_script.sh

DB_HOST="your-db-host"
DB_NAME="spy"
DB_USER="spy"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/spy_backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "spy_backup_*.sql" -mtime +30 -delete
```

#### 2. Point-in-Time Recovery
```bash
# Enable WAL archiving in postgresql.conf
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

### Monitoring

#### 1. Connection Monitoring
```sql
-- Monitor active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'spy';

-- Monitor long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

#### 2. Performance Monitoring
```sql
-- Monitor table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC;

-- Monitor index usage
SELECT indexrelname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes ORDER BY idx_tup_read DESC;
```

### Deployment Platforms

#### Railway/Render
```yaml
# render.yaml
databases:
  - name: spy-db
    databaseName: spy
    user: spy
    region: oregon

services:
  - type: web
    name: spy-tracker
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: spy-db
          property: connectionString
```

#### AWS RDS
```bash
# Example connection for RDS
DATABASE_URL=postgresql+psycopg2://spy:password@spy-db.cluster-xyz.us-east-1.rds.amazonaws.com:5432/spy?sslmode=require
```

#### Docker Compose Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    
  app:
    build: .
    environment:
      DATABASE_URL: postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      DEBUG: false
    depends_on:
      - db
    restart: unless-stopped
```

## Next Steps

1. **Development**: Use `./start.sh` for local development with auto-Postgres
2. **Testing**: Use `docker-compose --profile tools up` for database inspection
3. **Production**: Follow security and performance guidelines above
4. **Monitoring**: Set up automated backups and performance monitoring

For additional help, see the main [README.md](../README.md) or check the troubleshooting section above.