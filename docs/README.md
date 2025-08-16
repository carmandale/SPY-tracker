# SPY TA Tracker Documentation

Comprehensive documentation for developing, deploying, and maintaining SPY TA Tracker.

## Quick Start

### New to the Project?
1. **[POSTGRES_SETUP.md](./POSTGRES_SETUP.md)** - Complete PostgreSQL setup guide
2. **[.env.example](../.env.example)** - Environment configuration template
3. **[Quick Start Script](../start.sh)** - One-command development setup

### Need Database Help?
- **[POSTGRES_SETUP.md](./POSTGRES_SETUP.md)** - PostgreSQL installation, configuration, and workflows
- **[DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md)** - Migrate between SQLite and PostgreSQL
- **[DOCKER_COMPOSE_REFERENCE.md](./DOCKER_COMPOSE_REFERENCE.md)** - Docker Compose operations and troubleshooting

## Documentation Index

### Setup and Configuration
| Document | Purpose | Audience |
|----------|---------|----------|
| [POSTGRES_SETUP.md](./POSTGRES_SETUP.md) | Complete PostgreSQL workflow guide | All developers |
| [DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md) | SQLite ↔ PostgreSQL migration | DevOps, data migration |
| [DOCKER_COMPOSE_REFERENCE.md](./DOCKER_COMPOSE_REFERENCE.md) | Docker Compose operations | Container users |

### Environment Files
| File | Purpose | Required |
|------|---------|----------|
| [.env.example](../.env.example) | Main environment template | ✅ Copy to `.env` |
| [backend/.env.example](../backend/.env.example) | Backend configuration template | 📋 Optional overrides |
| [backend/.env.postgres.example](../backend/.env.postgres.example) | PostgreSQL-specific backend config | 🐘 PostgreSQL users |

### Project Documentation
| Document | Purpose |
|----------|---------|
| [../README.md](../README.md) | Main project README |
| [../SPY-tracker-PRD.md](../SPY-tracker-PRD.md) | Product Requirements Document |
| [../backend/README.md](../backend/README.md) | Backend-specific documentation |

## Common Workflows

### 🚀 First-Time Setup

1. **Clone and configure**:
   ```bash
   git clone <repo-url>
   cd spy-tracker
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start with automatic PostgreSQL**:
   ```bash
   ./start.sh
   ```
   
   This automatically:
   - Starts a PostgreSQL container if needed
   - Sets up the backend with proper database connection
   - Starts frontend and backend servers
   - Configures everything for development

### 🐘 PostgreSQL Development

1. **Database only** (most common):
   ```bash
   docker-compose up -d db
   ./start.sh
   ```

2. **With database admin interface**:
   ```bash
   docker-compose --profile tools up -d
   # Access Adminer at http://localhost:8080
   ```

3. **Full containerized stack**:
   ```bash
   export OPENAI_API_KEY=sk-your-key
   docker-compose --profile full up
   ```

### 🔄 Database Migration

1. **SQLite to PostgreSQL**:
   ```bash
   # See DATABASE_MIGRATION_GUIDE.md for detailed steps
   cp spy_tracker.db spy_tracker_backup.db  # Backup first
   # Update .env to use PostgreSQL
   ./start.sh  # Creates new PostgreSQL schema
   # Run migration script from guide
   ```

2. **PostgreSQL to SQLite**:
   ```bash
   # Export PostgreSQL data
   docker-compose exec db pg_dump -U spy -d spy > postgres_export.sql
   # Convert and import to SQLite (see migration guide)
   ```

### 🛠️ Troubleshooting

1. **Database connection issues**:
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps
   
   # Test connection
   docker-compose exec db pg_isready -U spy -d spy
   
   # Check logs
   docker-compose logs db
   ```

2. **Port conflicts**:
   ```bash
   # Check what's using port 5433
   lsof -i :5433
   
   # Stop conflicting services or use different port
   ```

3. **Container issues**:
   ```bash
   # Reset everything
   docker-compose down -v
   docker-compose up -d db
   ```

## Environment Configuration

### Database Options

#### SQLite (Testing)
```bash
DATABASE_URL=sqlite:///./spy_tracker.db
```
**Pros**: Simple, no setup required  
**Cons**: Single-user, no concurrency, limited for production

#### PostgreSQL (Recommended)
```bash
# Local Docker (automatic with start.sh)
DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy

# Manual installation
DATABASE_URL=postgresql+psycopg2://spy:pass@localhost:5432/spy

# Production
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db?sslmode=require
```
**Pros**: Production-ready, concurrent, full SQL features  
**Cons**: Requires setup

### Configuration Priority

Environment variables are loaded in this order (later overrides earlier):

1. **System environment variables**
2. **Root `.env`** - Main configuration
3. **`backend/.env`** - Backend-specific overrides
4. **`.env.local`** - Frontend-specific (loaded by start.sh)

### Required vs Optional Settings

#### Required (Minimum for basic operation)
```bash
DATABASE_URL=<your-database-connection>
```

#### Recommended (For full functionality)
```bash
DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy
OPENAI_API_KEY=sk-your-openai-api-key
APP_NAME=SPY TA Tracker
DEBUG=true
TIMEZONE=America/Chicago
```

#### Optional (Advanced features)
```bash
OPENAI_MODEL=gpt-5
OPENAI_REASONING_EFFORT=minimal
AI_LOOKBACK_DAYS=5
FRONTEND_ORIGIN=*
```

## Development Best Practices

### Database Development

1. **Use PostgreSQL for development** - Matches production environment
2. **Use Docker for PostgreSQL** - Consistent, isolated, easy cleanup
3. **Backup before major changes** - `docker-compose exec db pg_dump -U spy spy > backup.sql`
4. **Use separate databases for branches** - Avoid data conflicts

### Environment Management

1. **Never commit `.env` files** - Contains secrets
2. **Update `.env.example`** - Document new environment variables
3. **Use backend/.env for overrides** - Keep backend-specific settings separate
4. **Validate environment on startup** - Ensure required variables are set

### Container Management

1. **Use profiles for different scenarios**:
   - No profile: Database only (development)
   - `tools`: Database + Adminer (debugging)
   - `full`: Complete stack (testing)

2. **Clean up regularly**:
   ```bash
   # Remove stopped containers
   docker-compose down
   
   # Remove data volumes (⚠️ deletes data)
   docker-compose down -v
   
   # Remove unused images
   docker system prune
   ```

3. **Monitor resource usage**:
   ```bash
   docker stats
   ```

## Security Considerations

### Development Security

1. **Use strong passwords** - Even in development
2. **Don't expose databases publicly** - Use Docker's internal networking
3. **Rotate API keys regularly** - Especially OpenAI keys
4. **Use SSL in production** - `?sslmode=require` in connection strings

### Production Security

1. **Environment-specific passwords**:
   ```bash
   DATABASE_URL=postgresql+psycopg2://user:$(openssl rand -base64 32)@host/db
   ```

2. **Restrict CORS origins**:
   ```bash
   FRONTEND_ORIGIN=https://your-production-domain.com
   ```

3. **Use secrets management**:
   ```bash
   # Instead of .env files in production
   export DATABASE_URL="$(vault kv get -field=url secret/database)"
   ```

4. **Network security**:
   - Use private networks for database connections
   - Enable SSL/TLS for all connections
   - Implement connection pooling and rate limiting

## Deployment Guide

### Local Production Test

Test production configuration locally:

```bash
# Use production-like environment
cp .env.example .env.production
# Edit .env.production with production settings
DEBUG=false

# Start with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Cloud Deployment

#### Railway/Render
1. Connect GitHub repository
2. Set environment variables:
   ```
   DATABASE_URL=(provided by platform)
   OPENAI_API_KEY=sk-your-key
   DEBUG=false
   FRONTEND_ORIGIN=https://your-app.railway.app
   ```
3. Deploy automatically on git push

#### AWS/GCP/Azure
1. Set up managed PostgreSQL database
2. Deploy application container
3. Configure environment variables
4. Set up SSL/TLS termination
5. Configure monitoring and logging

### Monitoring

#### Health Checks
```bash
# Application health
curl http://localhost:8000/healthz

# Database health  
docker-compose exec db pg_isready -U spy -d spy
```

#### Performance Monitoring
```sql
-- Slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;

-- Database size
SELECT pg_size_pretty(pg_database_size('spy'));
```

## Getting Help

### Documentation
- **[POSTGRES_SETUP.md](./POSTGRES_SETUP.md)** - Comprehensive PostgreSQL guide
- **[DATABASE_MIGRATION_GUIDE.md](./DATABASE_MIGRATION_GUIDE.md)** - Migration procedures
- **[DOCKER_COMPOSE_REFERENCE.md](./DOCKER_COMPOSE_REFERENCE.md)** - Container operations

### Common Issues
1. **Database connection refused** → Check if PostgreSQL is running
2. **Port already in use** → Check for conflicts with `lsof -i :5433`
3. **Permission denied** → Check database user permissions
4. **Container won't start** → Check logs with `docker-compose logs`

### Community
- Check existing GitHub issues
- Review the main [README.md](../README.md)
- Consult the [Product Requirements Document](../SPY-tracker-PRD.md)

---

**Need something not covered here?** Check the individual documentation files above or create an issue for documentation improvements.