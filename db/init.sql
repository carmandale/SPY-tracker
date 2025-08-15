-- One-time init for local Postgres (applied on fresh volume by Docker entrypoint)
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'spy') THEN
      CREATE ROLE spy WITH LOGIN PASSWORD 'pass';
   END IF;
END$$;

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'spy') THEN
      CREATE DATABASE spy OWNER spy;
   END IF;
END$$;

GRANT ALL PRIVILEGES ON DATABASE spy TO spy;

