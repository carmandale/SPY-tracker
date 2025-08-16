-- PostgreSQL initialization script for SPY TA Tracker
-- Applied on fresh Docker volume by entrypoint

-- Create the spy user with appropriate permissions
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'spy') THEN
      CREATE ROLE spy WITH LOGIN PASSWORD 'pass';
      RAISE NOTICE 'Created role spy';
   ELSE
      RAISE NOTICE 'Role spy already exists';
   END IF;
END$$;

-- Create the spy database
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'spy') THEN
      CREATE DATABASE spy OWNER spy;
      RAISE NOTICE 'Created database spy';
   ELSE
      RAISE NOTICE 'Database spy already exists';
   END IF;
END$$;

-- Create test database for automated testing
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'spy_test') THEN
      CREATE DATABASE spy_test OWNER spy;
      RAISE NOTICE 'Created test database spy_test';
   ELSE
      RAISE NOTICE 'Test database spy_test already exists';
   END IF;
END$$;

-- Grant comprehensive privileges
GRANT ALL PRIVILEGES ON DATABASE spy TO spy;
GRANT ALL PRIVILEGES ON DATABASE spy_test TO spy;

-- Connect to spy database to set up extensions and optimizations
\c spy;

-- Enable useful extensions for time-series data and monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO spy;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO spy;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO spy;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO spy;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO spy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO spy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO spy;

-- Optimize for time-series data patterns
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_io_timing = on;
ALTER SYSTEM SET track_functions = all;

-- Connect to test database and set up the same extensions
\c spy_test;

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

GRANT ALL ON SCHEMA public TO spy;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO spy;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO spy;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO spy;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO spy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO spy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO spy;

