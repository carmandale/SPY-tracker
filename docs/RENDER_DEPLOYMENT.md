# Render Deployment Guide

> **Production Status**: ✅ LIVE at https://spy-tracker.onrender.com
> **Last Updated**: 2025-08-17
> **Deployment Type**: Docker-based with PostgreSQL

## Overview

The SPY TA Tracker is deployed on Render using Docker containers with a managed PostgreSQL database. This guide documents the deployment process, CLI tools, and management procedures.

## Current Production Environment

### Service Configuration
- **Service Name**: SPY-tracker
- **URL**: https://spy-tracker.onrender.com
- **Plan**: Starter
- **Region**: Oregon
- **Environment**: Docker (via Dockerfile)
- **Auto Deploy**: Enabled from main branch

### Database Configuration
- **Type**: PostgreSQL (Render managed)
- **Connection**: Via DATABASE_URL environment variable
- **Backups**: Handled by Render (daily automatic backups on paid plans)

### Key Features
- Multi-stage Docker build (frontend + backend)
- Health checks at `/healthz`
- Static file serving via FastAPI
- Scheduled jobs running in America/Chicago timezone
- SSL/TLS termination handled by Render

## Deployment Files

### render.yaml
```yaml
services:
  - type: web
    name: SPY-tracker
    env: docker
    plan: starter
    region: oregon
    autoDeploy: true
    healthCheckPath: /healthz
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
```

### Dockerfile
Multi-stage build:
1. **Frontend Stage**: Node.js 20 Alpine, builds React app with Vite
2. **Backend Stage**: Python 3.11 slim, installs uv and Python dependencies
3. **Final Image**: FastAPI server with built frontend assets

Key features:
- Uses `uv` for faster Python package installation
- Frontend assets copied to `backend/static/`
- Health check with curl
- Dynamic port binding (`$PORT` environment variable)

## Render CLI Setup

### Prerequisites
- Node.js installed
- Git repository access
- Render account with service access

### Installation and Setup

```bash
# 1. Run the setup script (installs CLI, authenticates, configures)
./scripts/render-setup.sh

# 2. Verify setup
render auth status
render services list
```

The setup script will:
- Install Render CLI via npm
- Authenticate with your Render account
- Discover the SPY-tracker service
- Create helper scripts and configuration files
- Set up read-only database access templates

### Configuration Files Created

After running `render-setup.sh`:

- `scripts/.render-config` - Service ID and URL
- `scripts/.env.production-readonly` - Database access template
- `scripts/connect-production-db.sh` - Database connection helper
- `scripts/check-production-health.sh` - Quick health checks

## CLI Tools and Scripts

### Health Monitoring

```bash
# Comprehensive health check
./scripts/production-health-check.py

# Quick API check only
./scripts/production-health-check.py --api-only

# Continuous monitoring
./scripts/production-health-check.py --monitor 60  # Check every 60 seconds

# Save report to file
./scripts/production-health-check.py --save-report health-report.json
```

### Database Access

```bash
# Verify database connectivity
./scripts/verify-production-db.py

# Quick connectivity check
./scripts/verify-production-db.py --quick-check

# Get database URL from Render service
./scripts/verify-production-db.py --get-url-from-render

# Query production database
./scripts/query-production-db.py --predictions 30    # Last 30 days of predictions
./scripts/query-production-db.py --ai-performance 7  # AI performance last 7 days
./scripts/query-production-db.py --health           # System health stats
./scripts/query-production-db.py --all              # All information

# Custom query (read-only)
./scripts/query-production-db.py --query "SELECT COUNT(*) FROM daily_predictions"
```

### Render CLI Commands

```bash
# Service management
render services list                          # List all services
render services get <service-id>              # Get service details
render services logs <service-id>             # View logs
render services logs <service-id> --tail 100 # Last 100 log lines
render shell <service-id>                     # Connect to service shell

# Deployment management
render services deploys <service-id>          # List deployments
render services env <service-id>              # Show environment variables

# Database management (if using Render PostgreSQL)
render databases list                         # List databases
render databases get <database-id>            # Get database details
```

## Deployment Process

### Automatic Deployment

The service is configured with `autoDeploy: true`, so deployments happen automatically:

1. Push code to `main` branch
2. Render detects the push
3. Trigger new build using Dockerfile
4. Health check at `/healthz` must pass
5. Traffic routes to new deployment
6. Old deployment terminates

### Manual Deployment

```bash
# Force deployment via CLI
render deploy --service-id <service-id>

# Deploy specific branch/commit
render deploy --service-id <service-id> --branch feature-branch
```

### Deployment Status

```bash
# Check deployment status
render services get <service-id>

# View deployment history
render services deploys <service-id>
```

## Environment Variables

### Required Variables
- `DATABASE_URL`: PostgreSQL connection string (set in Render dashboard)
- `OPENAI_API_KEY`: OpenAI API key for AI predictions (set in Render dashboard)

### Optional Variables
- `PORT`: Set automatically by Render (defaults to 8000 in Dockerfile)
- `VITE_API_URL`: Frontend API URL (defaults to "/" for same-origin)

### Setting Environment Variables

Via Render Dashboard:
1. Go to service settings
2. Add environment variable
3. Redeploy service

Via CLI:
```bash
render services env <service-id> set KEY=value
```

## Database Management

### Connection
The production database uses a managed PostgreSQL instance. Connection details are available via:

```bash
# Get database connection string
render services env <service-id> | grep DATABASE_URL

# Connect to database (if psql installed)
./scripts/connect-production-db.sh
```

### Backups
- **Automatic**: Render provides automatic backups (daily on paid plans)
- **Manual**: Use the query tools to export data
- **Local Sync**: Use the database synchronization tools (see Task 5)

### Monitoring
- Database metrics available in Render dashboard
- Custom monitoring via health check scripts
- Connection pooling handled by SQLAlchemy

## Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   render services logs <service-id>
   
   # Common causes:
   # - Missing environment variables
   # - Docker build context issues
   # - Network timeouts during npm/uv installs
   ```

2. **Health Check Failures**
   ```bash
   # Test health endpoint locally
   curl https://spy-tracker.onrender.com/healthz
   
   # Check service status
   ./scripts/production-health-check.py --api-only
   ```

3. **Database Connection Issues**
   ```bash
   # Verify database connectivity
   ./scripts/verify-production-db.py
   
   # Check database status via API
   curl https://spy-tracker.onrender.com/admin/database/status
   ```

4. **Scheduler Not Running**
   ```bash
   # Check scheduler status
   curl https://spy-tracker.onrender.com/scheduler/status
   
   # View logs for scheduler errors
   render services logs <service-id> | grep -i scheduler
   ```

### Performance Issues

1. **Slow Response Times**
   - Check Render service metrics in dashboard
   - Review application logs for bottlenecks
   - Consider upgrading service plan

2. **Memory Issues**
   - Monitor memory usage in Render dashboard
   - Check for memory leaks in logs
   - Optimize database queries

### Emergency Procedures

1. **Service Down**
   ```bash
   # Check service status
   render services get <service-id>
   
   # Force restart
   render deploy --service-id <service-id>
   ```

2. **Database Issues**
   ```bash
   # Check database status
   render databases get <database-id>
   
   # Review connection errors
   render services logs <service-id> | grep -i database
   ```

3. **Rollback Deployment**
   ```bash
   # List recent deployments
   render services deploys <service-id>
   
   # Manual rollback (contact Render support if needed)
   ```

## Monitoring and Alerting

### Health Checks
- **Automatic**: Render monitors health endpoint (`/healthz`)
- **Custom**: Use production-health-check.py for comprehensive monitoring
- **Alerts**: Configure via Render dashboard notifications

### Metrics to Monitor
- Response times (< 1000ms target)
- Error rates (< 1% target)
- Database connections
- Scheduler job success rate
- AI prediction generation rate

### Log Analysis
```bash
# Real-time logs
render services logs <service-id> --follow

# Filter specific events
render services logs <service-id> | grep -i error
render services logs <service-id> | grep "AI predictions"
render services logs <service-id> | grep scheduler
```

## Cost Optimization

### Current Plan: Starter
- **Compute**: 0.1 vCPU, 512 MB RAM
- **Cost**: ~$7/month
- **Database**: Additional cost for PostgreSQL

### Scaling Considerations
- **Vertical**: Upgrade to higher plan for more resources
- **Database**: Consider upgrading for better performance and backups
- **Monitoring**: Use metrics to determine if upgrade needed

## Security

### Best Practices
- Environment variables stored securely in Render
- Database access via read-only credentials where possible
- Regular security updates via automatic deployments
- HTTPS enforced by Render

### Access Control
- Render CLI access requires authentication
- Database access restricted to application and read-only tools
- Service logs accessible only to authenticated users

## Next Steps

### Planned Improvements
1. Enhanced monitoring and alerting
2. Automated database backups to external storage
3. Staging environment setup
4. Performance optimization based on production metrics

### Maintenance Tasks
- Regular dependency updates
- Performance monitoring and optimization
- Log rotation and cleanup
- Database maintenance and optimization

---

## Quick Reference

### Essential Commands
```bash
# Setup
./scripts/render-setup.sh

# Health checks
./scripts/production-health-check.py --api-only

# Database access
./scripts/query-production-db.py --health

# View logs
render services logs <service-id> --tail 100

# Service status
render services get <service-id>
```

### Emergency Contacts
- **Render Support**: Via dashboard or email
- **Production URL**: https://spy-tracker.onrender.com
- **Health Endpoint**: https://spy-tracker.onrender.com/healthz
- **Service Dashboard**: Render console → Services → SPY-tracker