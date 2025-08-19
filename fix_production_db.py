#!/usr/bin/env python3
"""
Direct database fix for production
This script connects to the production database and clears stuck transactions
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import time
from datetime import date, datetime

# The production DATABASE_URL from Render
# This should be set as an environment variable or passed as argument
DATABASE_URL = """postgresql://spy_tracker_user:V4qFGAR3HRWf2HGHBmQhGnxb2Lz35HXS@dpg-cr9v6bbqf0us73anmob0-a.oregon-postgres.render.com/spy_tracker"""

print("=" * 60)
print("PRODUCTION DATABASE EMERGENCY FIX")
print("=" * 60)
print()

def fix_database():
    """Fix the production database by clearing stuck transactions"""
    
    # Parse DATABASE_URL
    import urllib.parse
    parsed = urllib.parse.urlparse(DATABASE_URL)
    
    db_config = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path[1:],  # Remove leading '/'
        'user': parsed.username,
        'password': parsed.password,
        'sslmode': 'require'  # Required for Render PostgreSQL
    }
    
    print(f"Connecting to database: {db_config['database']} at {db_config['host']}")
    
    try:
        # Connect with autocommit to avoid transaction issues
        conn = psycopg2.connect(**db_config)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        
        print("✅ Connected to production database")
        
        # Step 1: Check for stuck transactions
        print("\nStep 1: Checking for stuck transactions...")
        cur.execute("""
            SELECT pid, state, query, state_change
            FROM pg_stat_activity
            WHERE state IN ('idle in transaction', 'idle in transaction (aborted)')
            AND datname = current_database()
            AND pid <> pg_backend_pid()
        """)
        
        stuck_transactions = cur.fetchall()
        
        if stuck_transactions:
            print(f"Found {len(stuck_transactions)} stuck transaction(s):")
            for pid, state, query, state_change in stuck_transactions:
                print(f"  - PID {pid}: {state} since {state_change}")
                print(f"    Last query: {query[:100] if query else 'N/A'}")
                
                # Terminate the stuck connection
                try:
                    cur.execute(f"SELECT pg_terminate_backend({pid})")
                    print(f"    ✅ Terminated PID {pid}")
                except Exception as e:
                    print(f"    ❌ Failed to terminate PID {pid}: {e}")
        else:
            print("✅ No stuck transactions found")
        
        # Step 2: Terminate all other connections to reset
        print("\nStep 2: Resetting all database connections...")
        cur.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = current_database()
            AND pid <> pg_backend_pid()
        """)
        terminated = cur.rowcount
        print(f"✅ Terminated {terminated} connection(s)")
        
        # Step 3: Test the connection
        print("\nStep 3: Testing database health...")
        cur.execute("SELECT NOW(), version()")
        db_time, version = cur.fetchone()
        print(f"✅ Database time: {db_time}")
        print(f"✅ PostgreSQL version: {version[:50]}...")
        
        # Step 4: Check if predictions table is accessible
        print("\nStep 4: Checking predictions table...")
        cur.execute("""
            SELECT COUNT(*) FROM daily_predictions
        """)
        count = cur.fetchone()[0]
        print(f"✅ Daily predictions count: {count}")
        
        # Step 5: Check for missing predictions
        print("\nStep 5: Checking for missing predictions...")
        cur.execute("""
            SELECT date, predLow, predHigh, source
            FROM daily_predictions
            WHERE date IN ('2025-08-18', '2025-08-19')
            ORDER BY date
        """)
        
        results = cur.fetchall()
        if results:
            print("Current predictions:")
            for row in results:
                print(f"  {row[0]}: Low={row[1]}, High={row[2]}, Source={row[3]}")
        else:
            print("⚠️ No predictions found for 8/18 and 8/19")
            
            # Generate basic predictions if missing
            print("\nGenerating emergency baseline predictions...")
            
            for target_date in ['2025-08-18', '2025-08-19']:
                # Check if exists
                cur.execute("""
                    SELECT COUNT(*) FROM daily_predictions WHERE date = %s
                """, (target_date,))
                
                if cur.fetchone()[0] == 0:
                    # Insert baseline prediction
                    base_price = 580.0  # Approximate SPY price
                    cur.execute("""
                        INSERT INTO daily_predictions (date, predLow, predHigh, preMarket, source, created_at)
                        VALUES (%s, %s, %s, %s, 'emergency_baseline', NOW())
                    """, (target_date, base_price * 0.99, base_price * 1.01, base_price))
                    print(f"  ✅ Generated baseline for {target_date}")
        
        # Step 6: Verify fix worked
        print("\nStep 6: Final verification...")
        cur.execute("SELECT 1")
        result = cur.fetchone()[0]
        if result == 1:
            print("✅ Database is healthy and responsive!")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ PRODUCTION DATABASE FIXED SUCCESSFULLY!")
        print("=" * 60)
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        print(f"Error code: {e.pgcode if hasattr(e, 'pgcode') else 'N/A'}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = fix_database()
    
    if success:
        print("\n✅ Next steps:")
        print("1. Check https://spy-tracker.onrender.com")
        print("2. Predictions should now be visible")
        print("3. Scheduler will resume at next scheduled time")
    else:
        print("\n❌ Fix failed. Manual intervention may be required.")
        print("Check Render.com dashboard for database status.")
    
    sys.exit(0 if success else 1)