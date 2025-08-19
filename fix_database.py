#!/usr/bin/env python3
"""
Emergency database fix script to add missing prompt_version column to production database.
This script fetches the DATABASE_URL from Render environment variables and applies the fix.
"""

import os
import sys
import subprocess
import json
from urllib.parse import urlparse

def get_render_env_vars(service_id):
    """Get environment variables from Render service."""
    try:
        # Get environment variables in JSON format
        result = subprocess.run(
            ["render", "services", "env", service_id, "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        env_vars = json.loads(result.stdout)
        return {var["key"]: var["value"] for var in env_vars}
    except subprocess.CalledProcessError as e:
        print(f"Error getting environment variables: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"stdout: {result.stdout}")
        return None

def run_migration(database_url):
    """Run the migration to add prompt_version column."""
    # Parse the database URL
    parsed = urlparse(database_url)
    
    # Install psycopg2 if not available
    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary"], check=True)
        import psycopg2
    
    # Connect to the database
    print(f"Connecting to database...")
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    
    try:
        # Check if column already exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ai_predictions' 
            AND column_name = 'prompt_version'
        """)
        
        if cur.fetchone():
            print("✅ Column 'prompt_version' already exists")
        else:
            print("Adding column 'prompt_version' to ai_predictions table...")
            cur.execute("""
                ALTER TABLE ai_predictions 
                ADD COLUMN prompt_version VARCHAR(50)
            """)
            conn.commit()
            print("✅ Column 'prompt_version' added successfully")
        
        # Verify the column exists
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'ai_predictions'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("\n📊 Current ai_predictions table schema:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else ""))
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def main():
    # SPY-tracker service ID from render services list
    SERVICE_ID = "srv-d2eganjipnbc739vqto0"
    
    print("🔧 Emergency Database Fix Script")
    print("=" * 50)
    
    # Get environment variables from Render
    print(f"Fetching environment variables for service {SERVICE_ID}...")
    env_vars = get_render_env_vars(SERVICE_ID)
    
    if not env_vars:
        print("❌ Failed to get environment variables")
        sys.exit(1)
    
    # Get DATABASE_URL
    database_url = env_vars.get("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Available vars:", list(env_vars.keys()))
        sys.exit(1)
    
    # Mask password in output
    parsed = urlparse(database_url)
    safe_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}{parsed.path}"
    print(f"Found DATABASE_URL: {safe_url}")
    
    # Run the migration
    run_migration(database_url)
    
    print("\n✅ Database fix completed successfully!")
    print("You can now test the /ai/predictions/* endpoints")

if __name__ == "__main__":
    main()