# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-19-monitoring-alerting-system-#32/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Endpoints

### GET /admin/health

**Purpose:** Comprehensive health check with detailed component status
**Parameters:** None
**Response:**
```json
{
  "status": "healthy|degraded|failed",
  "timestamp": "2025-08-19T10:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "connections": {
        "active": 5,
        "idle": 10,
        "overflow": 0,
        "max": 20
      },
      "response_time_ms": 15,
      "last_check": "2025-08-19T10:00:00Z"
    },
    "scheduler": {
      "status": "healthy",
      "running": true,
      "jobs": {
        "total": 6,
        "pending": 0,
        "running": 1,
        "failed_last_24h": 0
      },
      "next_job": {
        "name": "capture_noon_price",
        "scheduled_at": "2025-08-19T12:00:00Z"
      }
    },
    "ai_service": {
      "status": "healthy",
      "last_prediction": "2025-08-19T08:00:00Z",
      "api_key_valid": true,
      "rate_limit_remaining": 9500
    },
    "api": {
      "status": "healthy",
      "uptime_seconds": 86400,
      "memory_usage_mb": 256,
      "cpu_percent": 15.5
    }
  },
  "alerts": {
    "active": 0,
    "acknowledged": 1,
    "last_24h": 2
  }
}
```
**Errors:** 500 if health check fails

### GET /admin/alerts

**Purpose:** Retrieve alert history with filtering
**Parameters:**
- `status` (optional): active|acknowledged|resolved
- `severity` (optional): critical|warning|info
- `component` (optional): database|scheduler|api|ai_service
- `start_date` (optional): ISO date
- `end_date` (optional): ISO date
- `limit` (optional): default 100

**Response:**
```json
{
  "alerts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "severity": "critical",
      "component": "database",
      "title": "Database Transaction Failed",
      "message": "Transaction aborted, predictions blocked",
      "status": "resolved",
      "sent_at": "2025-08-18T08:00:00Z",
      "acknowledged_at": "2025-08-18T08:05:00Z",
      "resolved_at": "2025-08-19T10:00:00Z",
      "channel": "email"
    }
  ],
  "total": 15,
  "page": 1
}
```

### POST /admin/alerts/{alert_id}/acknowledge

**Purpose:** Acknowledge an active alert
**Parameters:** 
- `alert_id`: UUID of the alert
**Body:**
```json
{
  "acknowledged_by": "admin@example.com",
  "notes": "Investigating database connection issue"
}
```
**Response:** 200 OK with updated alert

### POST /admin/alerts/{alert_id}/resolve

**Purpose:** Mark an alert as resolved
**Parameters:**
- `alert_id`: UUID of the alert
**Body:**
```json
{
  "resolved_by": "admin@example.com",
  "resolution_notes": "Restarted database connection pool"
}
```
**Response:** 200 OK with updated alert

### GET /admin/jobs

**Purpose:** List scheduled jobs and their execution history
**Parameters:**
- `job_id` (optional): Filter by specific job
- `status` (optional): pending|running|success|failed
- `limit` (optional): default 50

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "ai_morning_prediction",
      "job_name": "AI Morning Prediction",
      "last_run": "2025-08-19T08:00:00Z",
      "status": "success",
      "duration_ms": 3500,
      "next_run": "2025-08-20T08:00:00Z",
      "retry_count": 0,
      "success_rate_7d": 0.857
    }
  ]
}
```

### POST /admin/jobs/{job_id}/trigger

**Purpose:** Manually trigger a scheduled job
**Parameters:**
- `job_id`: ID of the job to trigger
**Body:**
```json
{
  "date": "2025-08-19",
  "force": true,
  "reason": "Manual recovery for missed prediction"
}
```
**Response:** 202 Accepted with job execution ID

### POST /admin/recovery/predictions

**Purpose:** Generate predictions for missed dates
**Body:**
```json
{
  "start_date": "2025-08-18",
  "end_date": "2025-08-19",
  "use_baseline": false,
  "override_existing": false
}
```
**Response:**
```json
{
  "dates_processed": ["2025-08-18", "2025-08-19"],
  "success": 2,
  "failed": 0,
  "details": [...]
}
```

### POST /admin/recovery/database

**Purpose:** Attempt database recovery
**Body:**
```json
{
  "action": "reset_connections|clear_transactions|restart_pool",
  "force": false
}
```
**Response:** 200 OK with recovery status

### GET /metrics

**Purpose:** Prometheus-compatible metrics endpoint
**Parameters:** None
**Response:** Plain text Prometheus format
```
# HELP prediction_jobs_total Total prediction jobs
# TYPE prediction_jobs_total counter
prediction_jobs_total{status="success"} 145
prediction_jobs_total{status="failed"} 2

# HELP database_connections Active database connections
# TYPE database_connections gauge
database_connections 5
```

### WebSocket /admin/monitoring/ws

**Purpose:** Real-time monitoring dashboard updates
**Protocol:** WebSocket
**Messages:**
```json
{
  "type": "health_update",
  "component": "database",
  "status": "healthy",
  "timestamp": "2025-08-19T10:00:00Z"
}
```

## Error Responses

All endpoints follow standard error format:
```json
{
  "error": {
    "message": "Detailed error message",
    "type": "ErrorType",
    "details": {
      "field": "Additional context"
    }
  }
}
```

## Authentication

Admin endpoints require authentication (to be implemented):
- Bearer token in Authorization header
- Session cookie for dashboard access
- API key for monitoring services