#!/usr/bin/env python3

"""
Read-Only Production Database Query Tool

This script provides safe, read-only access to the production database
with predefined queries and custom query capabilities.
"""

# Add backend directory to path so we can use backend dependencies
import sys
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
if os.path.exists(backend_dir):
    sys.path.insert(0, backend_dir)

import os
import sys
import json
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import argparse
from typing import Dict, List, Optional, Tuple, Any
import logging
import tabulate

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI color codes
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.NC}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.NC}")

def print_query(message: str):
    print(f"{Colors.CYAN}🔍 {message}{Colors.NC}")

class ProductionDatabaseQuerier:
    """Handles read-only queries to production database."""
    
    def __init__(self):
        self.db_url = None
        self.connection = None
        self.readonly_mode = True
        
    def load_database_url(self) -> bool:
        """Load database URL from configuration."""
        # Try environment variables first
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
            
        return True
        
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(self.db_url)
            self.connection.set_session(readonly=True)
            print_success("Connected to production database (read-only mode)")
            return True
            
        except psycopg2.Error as e:
            print_error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print_success("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Tuple]:
        """Execute a read-only query safely."""
        if not self.connection:
            raise Exception("No database connection")
        
        # Safety check - prevent write operations
        query_upper = query.upper().strip()
        forbidden_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        
        for keyword in forbidden_keywords:
            if keyword in query_upper:
                raise Exception(f"Write operation '{keyword}' not allowed in read-only mode")
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_table_info(self) -> Dict[str, int]:
        """Get basic table information."""
        print_query("Getting table information...")
        
        query = """
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes
            FROM pg_stat_user_tables 
            ORDER BY tablename
        """
        
        results = self.execute_query(query)
        
        if results:
            headers = ['Schema', 'Table', 'Inserts', 'Updates', 'Deletes']
            print(tabulate.tabulate(results, headers=headers, tablefmt='grid'))
        
        return {row[1]: row[2] for row in results}  # tablename: inserts
    
    def get_daily_predictions_summary(self, days: int = 30) -> List[Tuple]:
        """Get summary of daily predictions."""
        print_query(f"Getting daily predictions summary (last {days} days)...")
        
        query = """
            SELECT 
                date,
                predLow,
                predHigh,
                bias,
                close,
                rangeHit,
                absErrorToClose,
                CASE 
                    WHEN source = 'ai' THEN '🤖 AI'
                    WHEN source = 'manual' THEN '👤 Manual'
                    ELSE '❓ Unknown'
                END as source_type
            FROM daily_predictions 
            WHERE date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY date DESC
        """
        
        results = self.execute_query(query, (days,))
        
        if results:
            headers = ['Date', 'Low', 'High', 'Bias', 'Close', 'Hit', 'Error', 'Source']
            formatted_results = []
            for row in results:
                date, low, high, bias, close, hit, error, source = row
                formatted_row = [
                    str(date),
                    f"${low:.2f}" if low else "N/A",
                    f"${high:.2f}" if high else "N/A", 
                    bias or "N/A",
                    f"${close:.2f}" if close else "N/A",
                    "✅" if hit else "❌",
                    f"${error:.2f}" if error else "N/A",
                    source
                ]
                formatted_results.append(formatted_row)
                
            print(tabulate.tabulate(formatted_results, headers=headers, tablefmt='grid'))
            
            # Summary stats
            hit_rate = sum(1 for row in results if row[5]) / len(results) * 100
            avg_error = sum(row[6] for row in results if row[6]) / len([r for r in results if r[6]])
            print_info(f"Summary: {len(results)} predictions, {hit_rate:.1f}% hit rate, ${avg_error:.2f} avg error")
        
        return results
    
    def get_ai_predictions_performance(self, days: int = 30) -> List[Tuple]:
        """Get AI predictions performance analysis."""
        print_query(f"Getting AI predictions performance (last {days} days)...")
        
        query = """
            SELECT 
                checkpoint,
                DATE(created_at) as prediction_date,
                predicted_price,
                actual_price,
                prediction_error,
                confidence,
                CASE 
                    WHEN actual_price BETWEEN interval_low AND interval_high THEN '✅ In Range'
                    ELSE '❌ Out of Range'
                END as interval_hit
            FROM ai_predictions 
            WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
                AND actual_price IS NOT NULL
            ORDER BY created_at DESC, checkpoint
        """
        
        results = self.execute_query(query, (days,))
        
        if results:
            headers = ['Checkpoint', 'Date', 'Predicted', 'Actual', 'Error', 'Confidence', 'Interval Hit']
            formatted_results = []
            for row in results:
                checkpoint, date, pred, actual, error, conf, interval_hit = row
                formatted_row = [
                    checkpoint,
                    str(date),
                    f"${pred:.2f}",
                    f"${actual:.2f}",
                    f"${error:.2f}" if error else "N/A",
                    f"{conf:.2f}" if conf else "N/A",
                    interval_hit
                ]
                formatted_results.append(formatted_row)
                
            print(tabulate.tabulate(formatted_results[:20], headers=headers, tablefmt='grid'))  # Show last 20
            
            # Performance stats by checkpoint
            print_query("Performance by checkpoint:")
            checkpoint_query = """
                SELECT 
                    checkpoint,
                    COUNT(*) as predictions,
                    AVG(prediction_error) as avg_error,
                    AVG(confidence) as avg_confidence,
                    AVG(CASE WHEN actual_price BETWEEN interval_low AND interval_high THEN 1 ELSE 0 END) as interval_hit_rate
                FROM ai_predictions 
                WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
                    AND actual_price IS NOT NULL
                GROUP BY checkpoint
                ORDER BY checkpoint
            """
            
            perf_results = self.execute_query(checkpoint_query, (days,))
            if perf_results:
                perf_headers = ['Checkpoint', 'Count', 'Avg Error', 'Avg Confidence', 'Interval Hit %']
                perf_formatted = []
                for row in perf_results:
                    checkpoint, count, error, conf, hit_rate = row
                    perf_formatted.append([
                        checkpoint,
                        count,
                        f"${error:.2f}" if error else "N/A",
                        f"{conf:.2f}" if conf else "N/A",
                        f"{hit_rate*100:.1f}%" if hit_rate else "N/A"
                    ])
                print(tabulate.tabulate(perf_formatted, headers=perf_headers, tablefmt='grid'))
        
        return results
    
    def get_recent_price_logs(self, days: int = 7) -> List[Tuple]:
        """Get recent price logs."""
        print_query(f"Getting recent price logs (last {days} days)...")
        
        query = """
            SELECT 
                date,
                checkpoint,
                price,
                created_at
            FROM price_logs 
            WHERE date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY date DESC, 
                CASE checkpoint 
                    WHEN 'premarket' THEN 1
                    WHEN 'open' THEN 2  
                    WHEN 'noon' THEN 3
                    WHEN 'twoPM' THEN 4
                    WHEN 'close' THEN 5
                    ELSE 6
                END
        """
        
        results = self.execute_query(query, (days,))
        
        if results:
            headers = ['Date', 'Checkpoint', 'Price', 'Logged At']
            formatted_results = []
            for row in results:
                date, checkpoint, price, logged_at = row
                formatted_row = [
                    str(date),
                    checkpoint,
                    f"${price:.2f}",
                    logged_at.strftime("%Y-%m-%d %H:%M:%S") if logged_at else "N/A"
                ]
                formatted_results.append(formatted_row)
                
            print(tabulate.tabulate(formatted_results[:30], headers=headers, tablefmt='grid'))  # Show last 30
        
        return results
    
    def get_system_health_stats(self) -> Dict[str, Any]:
        """Get system health statistics."""
        print_query("Getting system health statistics...")
        
        stats = {}
        
        # Database size
        size_query = """
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """
        
        size_results = self.execute_query(size_query)
        stats['table_sizes'] = size_results
        
        if size_results:
            print_info("Table sizes:")
            for schema, table, size in size_results:
                print_info(f"  {table}: {size}")
        
        # Record counts
        count_queries = [
            ("daily_predictions", "SELECT COUNT(*) FROM daily_predictions"),
            ("ai_predictions", "SELECT COUNT(*) FROM ai_predictions"),
            ("price_logs", "SELECT COUNT(*) FROM price_logs"),
            ("recent_predictions", "SELECT COUNT(*) FROM daily_predictions WHERE date >= CURRENT_DATE - INTERVAL '30 days'"),
            ("recent_ai_predictions", "SELECT COUNT(*) FROM ai_predictions WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'")
        ]
        
        print_info("Record counts:")
        for name, query in count_queries:
            try:
                result = self.execute_query(query)
                count = result[0][0] if result else 0
                stats[name] = count
                print_info(f"  {name.replace('_', ' ').title()}: {count:,}")
            except Exception as e:
                print_warning(f"  Could not get {name}: {e}")
        
        # Data freshness
        freshness_query = """
            SELECT 
                'Daily Predictions' as table_name,
                MAX(date) as latest_date,
                CURRENT_DATE - MAX(date) as days_old
            FROM daily_predictions
            
            UNION ALL
            
            SELECT 
                'AI Predictions' as table_name,
                MAX(DATE(created_at)) as latest_date,
                CURRENT_DATE - MAX(DATE(created_at)) as days_old
            FROM ai_predictions
            
            UNION ALL
            
            SELECT 
                'Price Logs' as table_name,
                MAX(date) as latest_date, 
                CURRENT_DATE - MAX(date) as days_old
            FROM price_logs
        """
        
        freshness_results = self.execute_query(freshness_query)
        stats['data_freshness'] = freshness_results
        
        if freshness_results:
            print_info("Data freshness:")
            for table, latest, days_old in freshness_results:
                status = "✅" if days_old <= 1 else "⚠️" if days_old <= 3 else "❌"
                print_info(f"  {table}: {latest} ({days_old} days old) {status}")
        
        return stats
    
    def execute_custom_query(self, query: str) -> List[Tuple]:
        """Execute a custom read-only query."""
        print_query("Executing custom query...")
        print_info(f"Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        results = self.execute_query(query)
        
        if results:
            # Get column names
            cursor = self.connection.cursor()
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]
            
            print(tabulate.tabulate(results, headers=column_names, tablefmt='grid'))
            print_info(f"Returned {len(results)} rows")
        else:
            print_info("Query returned no results")
        
        return results

def main():
    """Main query interface."""
    parser = argparse.ArgumentParser(description='Query production database (read-only)')
    parser.add_argument('--predictions', '-p', type=int, metavar='DAYS', 
                       help='Show daily predictions for last N days (default: 30)')
    parser.add_argument('--ai-performance', '-a', type=int, metavar='DAYS',
                       help='Show AI prediction performance for last N days (default: 30)')
    parser.add_argument('--price-logs', '-l', type=int, metavar='DAYS',
                       help='Show recent price logs for last N days (default: 7)')
    parser.add_argument('--health', action='store_true',
                       help='Show system health statistics')
    parser.add_argument('--tables', '-t', action='store_true',
                       help='Show table information')
    parser.add_argument('--query', '-q', type=str,
                       help='Execute custom read-only query')
    parser.add_argument('--all', action='store_true',
                       help='Show all available information')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)
    
    print(f"{Colors.BLUE}🔍 SPY TA Tracker - Production Database Query Tool{Colors.NC}")
    print("=" * 60)
    
    querier = ProductionDatabaseQuerier()
    
    # Load configuration and connect
    if not querier.load_database_url():
        sys.exit(1)
    
    if not querier.connect():
        sys.exit(1)
    
    try:
        # Execute requested queries
        if args.all or args.tables:
            querier.get_table_info()
            print()
        
        if args.all or args.predictions is not None:
            days = args.predictions if args.predictions is not None else 30
            querier.get_daily_predictions_summary(days)
            print()
        
        if args.all or args.ai_performance is not None:
            days = args.ai_performance if args.ai_performance is not None else 30
            querier.get_ai_predictions_performance(days)
            print()
        
        if args.all or args.price_logs is not None:
            days = args.price_logs if args.price_logs is not None else 7
            querier.get_recent_price_logs(days)
            print()
        
        if args.all or args.health:
            querier.get_system_health_stats()
            print()
        
        if args.query:
            querier.execute_custom_query(args.query)
            print()
    
    except Exception as e:
        print_error(f"Query execution failed: {e}")
        sys.exit(1)
    
    finally:
        querier.disconnect()
    
    print_success("Query execution completed successfully!")

if __name__ == "__main__":
    main()