# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-17-database-alignment-#25/spec.md

> Created: 2025-08-17
> Version: 1.0.0

## Technical Requirements

### Local PostgreSQL Setup
- **Docker Compose**: PostgreSQL 16 container with persistent volumes
- **Auto-start**: Integration with existing `start.sh` script to automatically start PostgreSQL
- **Port Configuration**: PostgreSQL on port 5433 to avoid conflicts with system PostgreSQL
- **Database Initialization**: Automatic creation of `spy` database with correct user permissions
- **Health Checks**: Container health monitoring and startup verification
- **Data Persistence**: Local volume mounting for data preservation across container restarts

### Environment Configuration Management
- **DATABASE_URL Required**: Local `.env` file MUST have PostgreSQL connection string
- **No Fallback**: Application fails fast if PostgreSQL unavailable (no SQLite)
- **Environment Detection**: Verify PostgreSQL is running before application start
- **Configuration Validation**: Startup checks that exit if database unavailable
- **Documentation Sync**: All environment files updated for PostgreSQL-only setup

### Render CLI Integration
- **CLI Installation**: Automated Render CLI setup with authentication
- **Database Access**: Secure connection to production PostgreSQL instance
- **Read-only Operations**: Safe querying of production data without modification risk
- **Connection Verification**: Health checks and connectivity testing commands
- **Logging Integration**: All production access operations logged locally

### Data Synchronization Tools
- **Export Functionality**: Python scripts to export production data to JSON/SQL formats
- **Import Functionality**: Scripts to import production data to local PostgreSQL
- **Selective Sync**: Option to sync specific tables or date ranges
- **Data Validation**: Integrity checks during import/export operations
- **Conflict Resolution**: Handling of duplicate data and constraint violations

### Script Integration
- **Enhanced start.sh**: Updated startup script with PostgreSQL auto-detection and startup
- **Database Management Scripts**: New scripts for database operations (sync, reset, verify)
- **Development Workflow**: Streamlined commands for common database operations
- **Error Handling**: Comprehensive error messages and troubleshooting guidance

## Approach Options

**Option A:** PostgreSQL-Only Everywhere (Selected)
- Pros: Complete dev/prod parity, no engine-specific bugs, true testing environment
- Cons: Requires Docker, no quick prototyping without database

**Option B:** Keep SQLite Fallback (Rejected)
- Pros: Easier onboarding, works without Docker
- Cons: Different engines cause bugs, false test results, production surprises

**Rationale:** PostgreSQL-only is the industry best practice. Different database engines between environments is an anti-pattern that causes subtle bugs, performance issues, and failed deployments. The minor convenience of SQLite is not worth the risk.

## External Dependencies

**Docker & Docker Compose**
- Purpose: Container orchestration for PostgreSQL
- Justification: Provides consistent, isolated PostgreSQL environment across all development machines

**Render CLI**
- Purpose: Production database access and management
- Justification: Official Render tooling for secure production operations

**psycopg2-binary** (already included)
- Purpose: PostgreSQL adapter for Python
- Justification: Required for PostgreSQL connectivity in Python applications

**pg_dump/pg_restore** (via Docker container)
- Purpose: Database backup and restore operations
- Justification: Standard PostgreSQL tools for data export/import operations

## Implementation Details

### Database Connection Logic
```python
def get_database_url():
    """PostgreSQL-only database URL resolution."""
    # 1. Check explicit DATABASE_URL environment variable
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    # 2. Check for local PostgreSQL availability
    if is_postgresql_available("localhost", 5433):
        return "postgresql://spy:pass@localhost:5433/spy"
    
    # 3. FAIL FAST - No fallback to SQLite
    raise RuntimeError(
        "PostgreSQL is required but not available.\n"
        "Please run: docker-compose up db -d\n"
        "Or set DATABASE_URL environment variable"
    )
```

### Docker Service Definition
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: spy
      POSTGRES_USER: spy
      POSTGRES_PASSWORD: pass
    ports:
      - "5433:5432"
    volumes:
      - spy_postgres_data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U spy -d spy"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### Data Sync Script Architecture
```python
class DatabaseSync:
    def __init__(self, prod_url: str, local_url: str):
        self.prod_engine = create_engine(prod_url)
        self.local_engine = create_engine(local_url)
    
    def export_production_data(self, tables: List[str] = None):
        """Export production data to local files."""
        
    def import_to_local(self, data_path: str, strategy: str = "replace"):
        """Import data to local database with conflict resolution."""
        
    def verify_data_integrity(self):
        """Verify data consistency between environments."""
```

## Security Considerations

### Production Access
- **Read-only Access**: All production queries are read-only by default
- **Audit Logging**: All production database access logged with timestamps
- **Connection Encryption**: All production connections use SSL/TLS
- **Credential Management**: Production credentials never stored in code or configs

### Local Development
- **Isolated Environment**: Local PostgreSQL runs in isolated Docker container
- **Development Data**: Local data clearly marked as development/test data
- **No Production Secrets**: Local environment uses separate, non-production credentials

### Data Handling
- **Data Classification**: Clear labeling of production vs. development data
- **Temporary Files**: Automatic cleanup of exported data files
- **Sensitive Data**: Option to exclude sensitive fields during data sync