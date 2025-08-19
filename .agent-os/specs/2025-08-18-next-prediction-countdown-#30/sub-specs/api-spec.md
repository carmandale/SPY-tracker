# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-18-next-prediction-countdown-#30/spec.md

> Created: 2025-08-18
> Version: 1.0.0

## Endpoints

### GET /api/version

**Purpose:** Provide current application version and deployment status information
**Parameters:** None
**Response:** JSON object with version and deployment details
**Errors:** 500 if version information cannot be determined

```json
{
  "version": "2.1.0",
  "environment": "production",
  "deployed_at": "2025-08-18T15:30:00Z",
  "git_commit": "a1b2c3d",
  "next_prediction": "2025-08-19T13:00:00Z"
}
```

### GET /api/scheduler/next-prediction

**Purpose:** Get the exact next run time for AI prediction job
**Parameters:** None  
**Response:** JSON object with next prediction timing
**Errors:** 503 if scheduler is not available

```json
{
  "next_run": "2025-08-19T13:00:00Z",
  "job_id": "ai_predict_0800",
  "timezone": "America/Chicago",
  "is_paused": false,
  "countdown_seconds": 43200
}
```

### GET /healthz (Enhanced)

**Purpose:** Enhanced health check including scheduler status
**Parameters:** None
**Response:** Extended health information  
**Errors:** 503 if critical systems are down

```json
{
  "status": "ok",
  "app": "SPY TA Tracker",
  "version": "2.1.0",
  "scheduler": {
    "running": true,
    "jobs_count": 6,
    "next_ai_prediction": "2025-08-19T13:00:00Z"
  },
  "database": "connected",
  "environment": "production"
}
```

## Controllers

### VersionController
- **get_version()**: Read version from package.json and environment
- **get_deployment_info()**: Extract deployment metadata
- **format_response()**: Structure version response consistently

### SchedulerController (Enhanced)  
- **get_next_prediction_time()**: Calculate next AI job run time
- **get_scheduler_status()**: Validate scheduler health
- **convert_timezone()**: Handle CST/CDT conversion for frontend

## Error Handling

### Version Endpoint Errors
- **FileNotFoundError**: Package.json missing → Return "unknown" version
- **JSONDecodeError**: Malformed package.json → Return error message
- **EnvironmentError**: Missing ENV vars → Use development defaults

### Scheduler Endpoint Errors  
- **SchedulerNotRunning**: Return 503 with error message
- **JobNotFound**: AI prediction job missing → Return null next_run
- **TimezoneError**: Invalid timezone config → Use UTC fallback

## Integration Points

### Frontend Integration
```typescript
// API client extension
export const apiClient = {
  // ... existing methods
  getVersion: () => fetch('/api/version').then(r => r.json()),
  getNextPrediction: () => fetch('/api/scheduler/next-prediction').then(r => r.json())
}
```

### Existing Router Integration
- Add version endpoints to main.py or create new version router
- Enhance existing scheduler router with prediction timing
- Maintain consistency with existing error handling patterns

### Environment Detection
```python
# Environment detection logic
def get_environment():
    if os.getenv('RENDER'):
        return 'production'
    elif os.getenv('VERCEL'):
        return 'production'  
    elif os.getenv('RAILWAY_ENVIRONMENT'):
        return 'production'
    else:
        return 'development'
```