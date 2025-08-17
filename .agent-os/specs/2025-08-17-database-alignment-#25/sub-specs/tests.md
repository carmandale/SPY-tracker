# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-17-database-alignment-#25/spec.md

> Created: 2025-08-17
> Version: 1.0.0

## Test Coverage

### Unit Tests

**Database Connection Management**
- Test DATABASE_URL environment variable detection
- Test PostgreSQL availability checking
- Test SQLite fallback mechanism
- Test connection string validation
- Test database engine creation with various configurations

**Environment Configuration**
- Test .env file loading from multiple locations
- Test environment variable precedence rules
- Test configuration validation and error handling
- Test database URL parsing and validation

**Data Export/Import Functions**
- Test production data export to JSON format
- Test data import with different conflict resolution strategies
- Test data validation during import/export
- Test error handling for malformed data

### Integration Tests

**Local PostgreSQL Setup**
- Test Docker container startup and health checks
- Test database initialization scripts execution
- Test schema creation via SQLAlchemy migrations
- Test connection establishment after container startup
- Test data persistence across container restarts

**Production Database Access**
- Test Render CLI authentication and connection
- Test read-only access to production database
- Test production data querying without modifications
- Test production connection error handling and retries

**Data Synchronization Workflows**
- Test complete production-to-local data sync
- Test selective table synchronization
- Test date-range based data export/import
- Test data integrity verification after sync
- Test rollback functionality for failed imports

**Environment Switching**
- Test switching from SQLite to PostgreSQL
- Test PostgreSQL unavailable fallback to SQLite
- Test DATABASE_URL override functionality
- Test application startup with different database configurations

### Feature Tests

**Start Script Integration**
- Test enhanced start.sh script with PostgreSQL auto-start
- Test database readiness checking before application start
- Test error messaging when Docker is unavailable
- Test graceful handling of database startup failures

**Database Management Scripts**
- Test database reset functionality
- Test backup creation and restoration
- Test schema verification commands
- Test data validation and integrity checks

**Development Workflow**
- Test complete developer onboarding process
- Test common database operations (reset, sync, verify)
- Test troubleshooting commands and error messages
- Test documentation accuracy against actual implementation

## Mocking Requirements

### External Services

**Docker API**
- Mock Docker daemon availability checks
- Mock container status and health check responses
- Mock container startup and shutdown operations
- Mock volume mounting and network configuration

**Render CLI**
- Mock Render authentication and session management
- Mock production database connection attempts
- Mock data export operations from production
- Mock CLI command execution and output parsing

**Network Connectivity**
- Mock PostgreSQL connection attempts (success/failure)
- Mock database query execution and results
- Mock timeout scenarios and connection drops
- Mock SSL/TLS certificate validation

### File System Operations

**Environment Files**
- Mock .env file reading and parsing
- Mock file existence checks for configuration files
- Mock environment variable setting and retrieval
- Mock file permissions and access errors

**Data Files**
- Mock JSON export file creation and reading
- Mock SQL dump file generation and processing
- Mock temporary file creation and cleanup
- Mock file system space and permission checks

## Test Data Requirements

### Sample Production Data

**Daily Predictions Dataset**
```json
{
    "daily_predictions": [
        {
            "id": 1,
            "date": "2025-08-15",
            "predLow": 580.00,
            "predHigh": 585.00,
            "bias": "neutral",
            "volCtx": "medium",
            "dayType": "range",
            "keyLevels": "580, 585",
            "notes": "Test prediction",
            "open": 581.50,
            "close": 583.25,
            "rangeHit": true,
            "absErrorToClose": 1.25
        }
    ],
    "price_logs": [
        {
            "id": 1,
            "date": "2025-08-15",
            "checkpoint": "open",
            "price": 581.50
        }
    ]
}
```

**AI Predictions Dataset**
- Multiple checkpoints (open, noon, twoPM, close)
- Various confidence levels (0.3 to 0.9)
- Different prediction sources (llm, baseline, ensemble)
- Complete prediction intervals and actual results

### Test Environment Configuration

**Local PostgreSQL Test Instance**
```yaml
test_db:
  image: postgres:16
  environment:
    POSTGRES_DB: spy_test
    POSTGRES_USER: spy_test
    POSTGRES_PASSWORD: test_pass
  ports:
    - "5434:5432"
  tmpfs:
    - /var/lib/postgresql/data  # In-memory for faster tests
```

**Mock Production Environment**
```python
MOCK_RENDER_CONFIG = {
    "service_id": "srv-test-123",
    "database_url": "postgresql://mock:pass@mock-host:5432/mock-db",
    "connection_status": "healthy",
    "last_backup": "2025-08-17T10:00:00Z"
}
```

## Performance Test Requirements

### Database Operation Performance

**Connection Establishment**
- Test local PostgreSQL connection time (target: <500ms)
- Test production database connection time (target: <2s)
- Test connection pool warmup and reuse
- Test connection failure recovery time

**Data Synchronization Performance**
- Test export of 1000+ records (target: <30s)
- Test import of large datasets (target: <60s)
- Test incremental sync vs. full replacement
- Test memory usage during large data operations

**Startup Performance**
- Test Docker container startup time (target: <30s)
- Test application startup with database checks (target: <10s)
- Test schema validation performance
- Test initial data loading performance

### Scalability Tests

**Large Dataset Handling**
- Test sync with 10,000+ prediction records
- Test memory efficiency during large imports
- Test streaming vs. batch processing for large datasets
- Test partial sync capabilities for large production databases

**Concurrent Access**
- Test multiple developer environments accessing same production data
- Test concurrent local database operations
- Test database locking during import operations
- Test backup operations during active development

## Error Scenario Testing

### Database Connectivity Failures

**PostgreSQL Unavailability**
- Test behavior when Docker daemon is stopped
- Test behavior when PostgreSQL container fails to start
- Test behavior when database is locked or corrupted
- Test graceful fallback to SQLite with user notification

**Production Access Failures**
- Test Render CLI authentication failures
- Test network connectivity issues to production
- Test production database maintenance windows
- Test rate limiting and access restrictions

**Data Synchronization Failures**
- Test partial data export/import failures
- Test data corruption during transfer
- Test foreign key constraint violations during import
- Test disk space exhaustion during operations

### Configuration Issues

**Environment Configuration**
- Test missing or malformed .env files
- Test invalid DATABASE_URL formats
- Test conflicting environment variables
- Test permission issues with configuration files

**Docker Configuration**
- Test Docker daemon not running
- Test insufficient Docker resources
- Test port conflicts with existing services
- Test volume mounting permission issues

## Continuous Integration Requirements

### Automated Test Execution

**CI Pipeline Integration**
```yaml
test_database_alignment:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16
      env:
        POSTGRES_PASSWORD: test_pass
        POSTGRES_DB: spy_test
  steps:
    - name: Run database alignment tests
      run: |
        pytest tests/test_database_alignment.py -v
        pytest tests/test_data_sync.py -v
        pytest tests/test_environment_config.py -v
```

**Test Data Management**
- Automated setup of test databases
- Seeding with consistent test data
- Cleanup after test completion
- Isolation between test runs

### Quality Gates

**Test Coverage Requirements**
- Minimum 90% code coverage for database alignment modules
- 100% coverage for critical data sync operations
- Integration test coverage for all main user workflows
- Performance test coverage for database operations

**Success Criteria**
- All unit tests pass in <5 minutes
- Integration tests complete in <10 minutes
- No memory leaks in data sync operations
- Consistent performance across different environments