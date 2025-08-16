# Docker Compose Reference

Complete reference for using Docker Compose with SPY TA Tracker, including service definitions, profiles, and operational commands.

## Table of Contents

- [Service Overview](#service-overview)
- [Profiles](#profiles)
- [Common Operations](#common-operations)
- [Service Configuration](#service-configuration)
- [Networking](#networking)
- [Volumes and Data](#volumes-and-data)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Service Overview

The `docker-compose.yml` defines three services:

### `db` (PostgreSQL Database)
- **Image**: `postgres:16`
- **Container**: `spydb`
- **Port**: `5433:5432` (host:container)
- **Purpose**: Primary database for all environments
- **Always Available**: No profile required

### `adminer` (Database Admin)
- **Image**: `adminer:latest`
- **Container**: `spy-adminer`
- **Port**: `8080:8080`
- **Purpose**: Web-based database administration
- **Profile**: `tools` (optional)

### `app` (Full Application)
- **Build**: Local Dockerfile
- **Container**: `spy-tracker-app`
- **Port**: `8000:8000`
- **Purpose**: Complete containerized application
- **Profile**: `full` (optional)

## Profiles

Docker Compose profiles allow selective service activation:

### Default (No Profile)
```bash
docker-compose up
# Starts: db only
```

### Tools Profile
```bash
docker-compose --profile tools up
# Starts: db + adminer
```

### Full Profile
```bash
docker-compose --profile full up
# Starts: db + app (includes web application)
```

### Multiple Profiles
```bash
docker-compose --profile tools --profile full up
# Starts: db + adminer + app
```

## Common Operations

### Starting Services

```bash
# Database only (most common for development)
docker-compose up db

# Database with admin interface
docker-compose --profile tools up

# Full stack
docker-compose --profile full up

# Background mode
docker-compose up -d db

# Force recreate containers
docker-compose up --force-recreate db
```

### Stopping Services

```bash
# Stop all running services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop db

# Kill services immediately
docker-compose kill
```

### Service Management

```bash
# View running services
docker-compose ps

# View service logs
docker-compose logs db
docker-compose logs -f adminer  # Follow logs

# Execute commands in services
docker-compose exec db psql -U spy -d spy
docker-compose exec db bash

# Restart services
docker-compose restart db

# Scale services (not applicable to our setup)
docker-compose up --scale app=2
```

### Building and Images

```bash
# Build application image
docker-compose build app

# Build without cache
docker-compose build --no-cache app

# Pull latest images
docker-compose pull

# View service images
docker-compose images
```

## Service Configuration

### Database Service (`db`)

```yaml
db:
  image: postgres:16
  container_name: spydb
  environment:
    - POSTGRES_USER=spy
    - POSTGRES_PASSWORD=pass  
    - POSTGRES_DB=spy
  ports:
    - "5433:5432"  # Avoids conflicts with host Postgres
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U spy -d spy"]
    interval: 10s
    timeout: 5s
    retries: 5
  volumes:
    - db_data:/var/lib/postgresql/data
    - ./db/init.sql:/docker-entrypoint-initdb.d/00-init.sql:ro
```

**Key Features**:
- **Port Mapping**: Uses 5433 to avoid conflicts
- **Health Checks**: Ensures database is ready before dependent services start
- **Persistent Storage**: Data survives container restarts
- **Initialization**: Runs `db/init.sql` on first start

### Adminer Service (`adminer`)

```yaml
adminer:
  image: adminer:latest
  container_name: spy-adminer
  ports:
    - "8080:8080"
  depends_on:
    db:
      condition: service_healthy  # Waits for database health check
  profiles: ["tools"]
```

**Access Adminer**:
- URL: http://localhost:8080
- System: PostgreSQL
- Server: `db` (internal network) or `localhost:5433` (external)
- Username: `spy`
- Password: `pass`
- Database: `spy`

### Application Service (`app`)

```yaml
app:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: spy-tracker-app
  environment:
    - PORT=8000
    - DATABASE_URL=postgresql+psycopg2://spy:pass@db:5432/spy
    - OPENAI_API_KEY=${OPENAI_API_KEY:-}
  ports:
    - "8000:8000"
  depends_on:
    db:
      condition: service_healthy
  profiles: ["full"]
```

**Key Features**:
- **Local Build**: Builds from project Dockerfile
- **Environment Injection**: Uses host environment variables
- **Database Connection**: Uses internal network (`db:5432`)
- **Health Dependencies**: Waits for database to be ready

## Networking

### Internal Network

Docker Compose creates an internal network where services communicate:

```bash
# Services can reach each other by name:
# db:5432        - Database from app perspective
# app:8000       - Application from other services
# adminer:8080   - Adminer from other services
```

### External Access

Host machine access to services:

```bash
# Database: localhost:5433
psql -h localhost -p 5433 -U spy -d spy

# Adminer: http://localhost:8080
curl http://localhost:8080

# Application: http://localhost:8000  
curl http://localhost:8000/healthz
```

### Network Commands

```bash
# List networks
docker network ls

# Inspect compose network
docker network inspect $(docker-compose ps -q | head -1 | xargs docker inspect --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}')

# Connect external container to compose network
docker run --network conakry_default -it postgres:16 psql -h db -U spy -d spy
```

## Volumes and Data

### Persistent Volumes

```yaml
volumes:
  db_data:  # Named volume for database persistence
```

### Volume Operations

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect conakry_db_data

# Backup volume data
docker run --rm -v conakry_db_data:/data -v $(pwd):/backup ubuntu tar czf /backup/db_backup.tar.gz /data

# Restore volume data
docker run --rm -v conakry_db_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/db_backup.tar.gz -C /

# Remove volume (⚠️ deletes all data)
docker volume rm conakry_db_data
```

### Database Initialization

The `db/init.sql` file runs once when the database volume is first created:

```sql
-- Creates role and database if they don't exist
-- Grants necessary permissions
-- Only runs on fresh volume creation
```

**Important**: Init scripts only run on fresh volumes. To re-run:

```bash
# Remove volume and recreate
docker-compose down -v
docker-compose up db
```

## Environment Variables

### Compose Environment

Set environment variables for Docker Compose:

```bash
# In .env file (read by docker-compose)
OPENAI_API_KEY=sk-your-key-here
POSTGRES_PASSWORD=secure_password

# Or export before running
export OPENAI_API_KEY=sk-your-key-here
docker-compose --profile full up
```

### Service Environment

Each service can access different environment variables:

#### Database Service
```yaml
environment:
  - POSTGRES_USER=spy
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-pass}
  - POSTGRES_DB=spy
```

#### Application Service
```yaml
environment:
  - PORT=8000
  - DATABASE_URL=postgresql+psycopg2://spy:pass@db:5432/spy
  - OPENAI_API_KEY=${OPENAI_API_KEY:-}
  - DEBUG=${DEBUG:-true}
```

### Override Files

Create environment-specific overrides:

#### `docker-compose.override.yml` (Development)
```yaml
version: '3.8'
services:
  db:
    environment:
      - POSTGRES_PASSWORD=dev_password
  app:
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
```

#### `docker-compose.prod.yml` (Production)
```yaml
version: '3.8'
services:
  db:
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - /opt/spy-tracker/backups:/backups
  app:
    environment:
      - DEBUG=false
      - LOG_LEVEL=info
    restart: unless-stopped
```

**Usage**:
```bash
# Development (uses override.yml automatically)
docker-compose up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Troubleshooting

### Service Issues

#### Database Won't Start

```bash
# Check logs
docker-compose logs db

# Common issues:
# 1. Port conflict
sudo lsof -i :5433

# 2. Permission issues
docker-compose down -v  # Remove volume
docker-compose up db    # Recreate

# 3. Init script errors
docker-compose exec db cat /var/log/postgresql/postgresql*.log
```

#### Application Can't Connect to Database

```bash
# Verify database is healthy
docker-compose ps

# Check internal connectivity
docker-compose exec app ping db

# Verify environment variables
docker-compose exec app env | grep DATABASE

# Test connection manually
docker-compose exec app python -c "
import psycopg2
conn = psycopg2.connect('postgresql://spy:pass@db:5432/spy')
print('Connection successful')
"
```

#### Adminer Connection Issues

```bash
# Verify Adminer is running
docker-compose ps adminer

# Test internal connectivity
docker-compose exec adminer ping db

# Access logs
docker-compose logs adminer

# Try external connection string in Adminer:
# Server: host.docker.internal:5433 (macOS/Windows)
# Server: 172.17.0.1:5433 (Linux)
```

### Performance Issues

#### Slow Database Operations

```bash
# Check resource usage
docker stats

# Analyze slow queries (requires logging)
docker-compose exec db psql -U spy -d spy -c "
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;
"

# Optimize database settings
docker-compose exec db psql -U spy -d spy -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
"
```

#### Container Resource Limits

Add resource limits to services:

```yaml
services:
  db:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

### Data Recovery

#### Database Corruption

```bash
# Stop services
docker-compose down

# Check volume integrity
docker run --rm -v conakry_db_data:/data ubuntu fsck /data

# Restore from backup
docker volume rm conakry_db_data
docker volume create conakry_db_data
docker run --rm -v conakry_db_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/db_backup.tar.gz -C /

# Start services
docker-compose up db
```

#### Lost Configuration

```bash
# Recreate containers with fresh config
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Development Helpers

#### Quick Database Reset

```bash
#!/bin/bash
# reset_db.sh
echo "Resetting database..."
docker-compose down
docker volume rm conakry_db_data 2>/dev/null || true
docker-compose up -d db
echo "Database reset complete"
```

#### Health Check Script

```bash
#!/bin/bash
# health_check.sh
echo "Checking service health..."

# Database
if docker-compose exec db pg_isready -U spy -d spy >/dev/null 2>&1; then
    echo "✅ Database: healthy"
else
    echo "❌ Database: unhealthy"
fi

# Adminer
if curl -s http://localhost:8080 >/dev/null 2>&1; then
    echo "✅ Adminer: accessible"
else
    echo "⚠️  Adminer: not running or accessible"
fi

# Application
if curl -s http://localhost:8000/healthz >/dev/null 2>&1; then
    echo "✅ Application: healthy"
else
    echo "⚠️  Application: not running or accessible"
fi
```

#### Log Aggregation

```bash
#!/bin/bash
# collect_logs.sh
mkdir -p logs
docker-compose logs db > logs/db.log 2>&1
docker-compose logs adminer > logs/adminer.log 2>&1
docker-compose logs app > logs/app.log 2>&1
echo "Logs collected in ./logs/"
```

For additional Docker Compose guidance, see:
- [POSTGRES_SETUP.md](./POSTGRES_SETUP.md) - Database-specific setup
- [DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md) - Data migration procedures