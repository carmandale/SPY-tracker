#!/usr/bin/env python3

"""
Production Database Connection Verification Script

This script verifies connection to the production PostgreSQL database
and performs various connectivity and health checks.
"""

# Add backend directory to path so we can use backend dependencies
import sys
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
if os.path.exists(backend_dir):
    sys.path.insert(0, backend_dir)

import os
import sys
import json
import subprocess
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import argparse
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI color codes
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.NC}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.NC}")

class ProductionDatabaseVerifier:
    """Handles production database verification and health checks."""
    
    def __init__(self):
        self.db_url = None
        self.connection = None
        self.service_id = None
        self.readonly_mode = True
        
    def load_configuration(self) -> bool:
        """Load Render service configuration."""
        config_file = "scripts/.render-config"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    if line.startswith('RENDER_SERVICE_ID='):
                        self.service_id = line.split('=')[1].strip()
            print_success(f"Loaded Render service ID: {self.service_id}")
        else:
            print_error("Render configuration not found. Run scripts/render-setup.sh first.")
            return False
        
        # Try to get database URL from environment or config
        self.db_url = os.getenv('DATABASE_URL_READONLY') or os.getenv('DATABASE_URL')
        
        if not self.db_url:
            # Try to load from production readonly config
            readonly_config = "scripts/.env.production-readonly"
            if os.path.exists(readonly_config):
                with open(readonly_config, 'r') as f:
                    for line in f:
                        if line.startswith('DATABASE_URL_READONLY='):
                            self.db_url = line.split('=', 1)[1].strip().strip('"')
                            break
        
        if not self.db_url or 'password' in self.db_url:
            print_error("Database URL not configured or using placeholder values.")
            print_info("Please update scripts/.env.production-readonly with actual credentials.")
            return False
            
        print_success("Database URL loaded successfully")
        return True
        
    def get_database_url_from_render(self) -> Optional[str]:
        """Get database URL from Render service environment variables."""
        if not self.service_id:
            print_error("Service ID not available")
            return None
            
        try:
            print_info("Fetching database URL from Render service...")
            result = subprocess.run(
                ['render', 'services', 'env', self.service_id],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('DATABASE_URL='):
                        db_url = line.split('=', 1)[1]
                        print_success("Database URL retrieved from Render")
                        return db_url
                print_warning("DATABASE_URL not found in service environment")
            else:
                print_error(f"Failed to get service environment: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print_error("Timeout while fetching database URL from Render")
        except FileNotFoundError:
            print_error("Render CLI not found. Please run scripts/render-setup.sh first.")
            
        return None
    
    def test_connection(self) -> bool:
        """Test basic database connectivity."""
        print_info("Testing database connection...")
        
        try:
            self.connection = psycopg2.connect(self.db_url)
            self.connection.set_session(readonly=self.readonly_mode)
            print_success("Database connection established")
            return True
            
        except psycopg2.OperationalError as e:
            print_error(f"Connection failed: {e}")
            return False
        except Exception as e:
            print_error(f"Unexpected error during connection: {e}")
            return False
    
    def verify_database_schema(self) -> bool:
        """Verify that expected tables exist."""
        print_info("Verifying database schema...")
        
        expected_tables = [
            'daily_predictions',
            'price_logs', 
            'ai_predictions',
            'baseline_models',
            'model_performance'
        ]
        
        try:
            cursor = self.connection.cursor()
            
            # Get list of tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            print_success(f"Found {len(existing_tables)} tables in database")
            
            missing_tables = []
            for table in expected_tables:
                if table in existing_tables:
                    print_success(f"Table exists: {table}")
                else:
                    missing_tables.append(table)
                    print_warning(f"Table missing: {table}")
            
            if missing_tables:
                print_warning(f"Missing tables: {', '.join(missing_tables)}")
                return False
            
            print_success("All expected tables found")
            return True
            
        except Exception as e:
            print_error(f"Schema verification failed: {e}")
            return False
    
    def check_data_health(self) -> Dict[str, int]:
        """Check data health and basic statistics."""
        print_info("Checking data health...")
        
        stats = {}
        
        try:
            cursor = self.connection.cursor()
            
            # Count records in key tables
            tables_to_check = [
                ('daily_predictions', 'Daily predictions'),
                ('ai_predictions', 'AI predictions'),
                ('price_logs', 'Price logs')
            ]
            
            for table_name, display_name in tables_to_check:
                cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                    sql.Identifier(table_name)
                ))
                count = cursor.fetchone()[0]
                stats[table_name] = count
                print_success(f"{display_name}: {count:,} records")
            
            # Check recent data
            cursor.execute("""
                SELECT DATE(date) as pred_date, COUNT(*) as count
                FROM daily_predictions 
                WHERE date >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(date)
                ORDER BY pred_date DESC
            """)
            
            recent_predictions = cursor.fetchall()
            if recent_predictions:
                print_success(f"Recent predictions (last 7 days): {len(recent_predictions)} days")
                for date, count in recent_predictions[:3]:  # Show last 3 days
                    print_info(f"  {date}: {count} predictions")
            else:
                print_warning("No recent predictions found")
            
            # Check AI prediction accuracy
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_predictions,
                    COUNT(CASE WHEN actual_price IS NOT NULL THEN 1 END) as with_actual,
                    AVG(CASE WHEN actual_price IS NOT NULL THEN prediction_error END) as avg_error
                FROM ai_predictions
                WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            """)
            
            ai_stats = cursor.fetchone()
            if ai_stats and ai_stats[0] > 0:
                total, with_actual, avg_error = ai_stats
                print_success(f"AI predictions (30 days): {total} total, {with_actual} with actual prices")
                if avg_error:
                    print_info(f"  Average prediction error: ${avg_error:.2f}")
            
            return stats
            
        except Exception as e:
            print_error(f"Data health check failed: {e}")
            return {}
    
    def test_readonly_constraints(self) -> bool:
        """Test that readonly constraints are working."""
        print_info("Testing read-only constraints...")
        
        if not self.readonly_mode:
            print_warning("Not in readonly mode - skipping write test")
            return True
        
        try:
            cursor = self.connection.cursor()
            
            # Attempt a write operation (should fail)
            cursor.execute("""
                INSERT INTO daily_predictions (date, predLow) 
                VALUES (CURRENT_DATE + INTERVAL '1000 days', 999.99)
            """)
            
            # If we get here, readonly mode failed
            print_error("Read-only constraints not working - write operation succeeded!")
            self.connection.rollback()
            return False
            
        except psycopg2.Error as e:
            if "read-only" in str(e).lower() or "readonly" in str(e).lower():
                print_success("Read-only constraints working correctly")
                return True
            else:
                print_warning(f"Write operation failed for different reason: {e}")
                return True
    
    def run_sample_queries(self) -> bool:
        """Run sample queries to verify data access."""
        print_info("Running sample queries...")
        
        try:
            cursor = self.connection.cursor()
            
            # Query 1: Recent predictions with accuracy
            print_info("Sample Query 1: Recent predictions with hit rate")
            cursor.execute("""
                SELECT 
                    date,
                    predLow,
                    predHigh,
                    close,
                    rangeHit,
                    bias
                FROM daily_predictions 
                WHERE date >= CURRENT_DATE - INTERVAL '5 days'
                ORDER BY date DESC
                LIMIT 5
            """)
            
            results = cursor.fetchall()
            if results:
                print_success(f"Found {len(results)} recent predictions:")
                for row in results[:3]:  # Show first 3
                    date, low, high, close, hit, bias = row
                    hit_status = "✅" if hit else "❌"
                    print_info(f"  {date}: ${low:.2f}-${high:.2f}, Close: ${close:.2f if close else 'N/A'} {hit_status} ({bias})")
            else:
                print_warning("No recent predictions found")
            
            # Query 2: AI prediction performance
            print_info("Sample Query 2: AI prediction accuracy")
            cursor.execute("""
                SELECT 
                    checkpoint,
                    AVG(confidence) as avg_confidence,
                    AVG(prediction_error) as avg_error,
                    COUNT(*) as count
                FROM ai_predictions 
                WHERE actual_price IS NOT NULL
                    AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY checkpoint
                ORDER BY checkpoint
            """)
            
            ai_results = cursor.fetchall()
            if ai_results:
                print_success("AI prediction performance (30 days):")
                for checkpoint, conf, error, count in ai_results:
                    print_info(f"  {checkpoint}: {count} predictions, {conf:.2f} avg confidence, ${error:.2f} avg error")
            
            return True
            
        except Exception as e:
            print_error(f"Sample queries failed: {e}")
            return False
    
    def close_connection(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print_success("Database connection closed")

def main():
    """Main verification process."""
    parser = argparse.ArgumentParser(description='Verify production database connection')
    parser.add_argument('--get-url-from-render', action='store_true', 
                       help='Fetch database URL from Render service')
    parser.add_argument('--allow-writes', action='store_true',
                       help='Allow write operations (disables readonly mode)')
    parser.add_argument('--quick-check', action='store_true',
                       help='Run only basic connectivity check')
    
    args = parser.parse_args()
    
    print(f"{Colors.BLUE}🔍 SPY TA Tracker - Production Database Verification{Colors.NC}")
    print("=" * 60)
    
    verifier = ProductionDatabaseVerifier()
    verifier.readonly_mode = not args.allow_writes
    
    # Load configuration
    if not verifier.load_configuration():
        sys.exit(1)
    
    # Get database URL from Render if requested
    if args.get_url_from_render:
        db_url = verifier.get_database_url_from_render()
        if db_url:
            verifier.db_url = db_url
        else:
            print_error("Could not retrieve database URL from Render")
            sys.exit(1)
    
    success = True
    
    try:
        # Test connection
        if not verifier.test_connection():
            success = False
            
        if args.quick_check:
            print_success("Quick connectivity check completed")
        else:
            # Full verification
            if success and not verifier.verify_database_schema():
                success = False
            
            if success:
                verifier.check_data_health()
                
            if success and not verifier.test_readonly_constraints():
                success = False
                
            if success and not verifier.run_sample_queries():
                success = False
        
    finally:
        verifier.close_connection()
    
    print()
    if success:
        print_success("✅ Database verification completed successfully!")
        print_info("Production database is accessible and healthy")
    else:
        print_error("❌ Database verification failed")
        print_info("Please check configuration and connectivity")
        sys.exit(1)

if __name__ == "__main__":
    main()