#!/usr/bin/env python3

"""
Production Health Check and Status Verification Tool

This script performs comprehensive health checks on the SPY TA Tracker
production environment including API, database, scheduler, and services.
"""

# Add backend directory to path so we can use backend dependencies
import sys
import os
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
if os.path.exists(backend_dir):
    sys.path.insert(0, backend_dir)

import json
import subprocess
import requests
import psycopg2
from datetime import datetime, timedelta
import argparse
from typing import Dict, List, Optional, Tuple, Any
import logging
import time

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
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.NC}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.NC}")

def print_check(message: str):
    print(f"{Colors.CYAN}🔍 {message}{Colors.NC}")

def print_metric(message: str):
    print(f"{Colors.MAGENTA}📊 {message}{Colors.NC}")

class ProductionHealthChecker:
    """Comprehensive production health checker."""
    
    def __init__(self, base_url: str = "https://spy-tracker.onrender.com"):
        self.base_url = base_url.rstrip('/')
        self.service_id = None
        self.db_url = None
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Load configuration
        self.load_configuration()
        
    def load_configuration(self):
        """Load service configuration."""
        config_file = "scripts/.render-config"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    if line.startswith('RENDER_SERVICE_ID='):
                        self.service_id = line.split('=')[1].strip()
                    elif line.startswith('RENDER_SERVICE_URL='):
                        url = line.split('=')[1].strip()
                        if url and url != self.base_url:
                            self.base_url = url
        
        # Load database URL
        self.db_url = os.getenv('DATABASE_URL_READONLY') or os.getenv('DATABASE_URL')
        if not self.db_url:
            readonly_config = "scripts/.env.production-readonly"
            if os.path.exists(readonly_config):
                with open(readonly_config, 'r') as f:
                    for line in f:
                        if line.startswith('DATABASE_URL_READONLY='):
                            self.db_url = line.split('=', 1)[1].strip().strip('"')
                            break
    
    def check_api_health(self) -> Dict[str, Any]:
        """Check API health and basic connectivity."""
        print_check("Checking API health...")
        
        health_data = {
            'status': 'unknown',
            'response_time': None,
            'endpoints': {}
        }
        
        # Test health endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/healthz")
            response_time = (time.time() - start_time) * 1000
            
            health_data['response_time'] = response_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'ok':
                        print_success(f"API health check passed ({response_time:.0f}ms)")
                        health_data['status'] = 'healthy'
                        health_data['app_name'] = data.get('app', 'Unknown')
                    else:
                        print_warning(f"API returned non-OK status: {data}")
                        health_data['status'] = 'degraded'
                except json.JSONDecodeError:
                    print_warning(f"API returned non-JSON response: {response.text[:100]}")
                    health_data['status'] = 'degraded'
            else:
                print_error(f"API health check failed: HTTP {response.status_code}")
                health_data['status'] = 'failed'
                
        except requests.exceptions.RequestException as e:
            print_error(f"API health check failed: {e}")
            health_data['status'] = 'failed'
        
        # Test key endpoints
        endpoints_to_test = [
            ('/scheduler/status', 'Scheduler Status'),
            ('/admin/database/status', 'Database Status'),  
            ('/admin/predictions/count', 'Predictions Count'),
            ('/market/current', 'Market Data')
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    print_success(f"{description} endpoint: OK")
                    health_data['endpoints'][endpoint] = 'ok'
                elif response.status_code == 404:
                    print_info(f"{description} endpoint: Not found (may be normal)")
                    health_data['endpoints'][endpoint] = 'not_found'
                else:
                    print_warning(f"{description} endpoint: HTTP {response.status_code}")
                    health_data['endpoints'][endpoint] = 'error'
            except requests.exceptions.RequestException as e:
                print_error(f"{description} endpoint failed: {e}")
                health_data['endpoints'][endpoint] = 'failed'
        
        return health_data
    
    def check_scheduler_status(self) -> Dict[str, Any]:
        """Check scheduler status and jobs."""
        print_check("Checking scheduler status...")
        
        scheduler_data = {
            'status': 'unknown',
            'jobs_count': 0,
            'timezone': None,
            'next_runs': []
        }
        
        try:
            response = self.session.get(f"{self.base_url}/scheduler/status")
            
            if response.status_code == 200:
                data = response.json()
                scheduler_data.update(data)
                
                status = data.get('status', 'unknown')
                jobs_count = data.get('jobs_count', 0)
                timezone = data.get('timezone', 'Unknown')
                
                if status == 'running':
                    print_success(f"Scheduler running with {jobs_count} jobs in {timezone}")
                else:
                    print_warning(f"Scheduler status: {status}")
                
                # Check next job runs
                next_runs = data.get('next_runs', [])
                if next_runs:
                    print_info("Next scheduled jobs:")
                    for job in next_runs[:5]:  # Show next 5 jobs
                        job_id = job.get('job_id', 'unknown')
                        next_run = job.get('next_run_time', 'unknown')
                        print_info(f"  {job_id}: {next_run}")
                
            else:
                print_error(f"Scheduler status check failed: HTTP {response.status_code}")
                scheduler_data['status'] = 'failed'
                
        except requests.exceptions.RequestException as e:
            print_error(f"Scheduler status check failed: {e}")
            scheduler_data['status'] = 'failed'
        except json.JSONDecodeError as e:
            print_error(f"Invalid scheduler response: {e}")
            scheduler_data['status'] = 'failed'
        
        return scheduler_data
    
    def check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity and basic stats."""
        print_check("Checking database connectivity...")
        
        db_data = {
            'status': 'unknown',
            'connection_time': None,
            'record_counts': {},
            'data_freshness': {}
        }
        
        if not self.db_url or 'password' in self.db_url:
            print_warning("Database URL not configured properly")
            db_data['status'] = 'not_configured'
            return db_data
        
        try:
            start_time = time.time()
            connection = psycopg2.connect(self.db_url)
            connection.set_session(readonly=True)
            connection_time = (time.time() - start_time) * 1000
            
            db_data['connection_time'] = connection_time
            print_success(f"Database connection established ({connection_time:.0f}ms)")
            
            cursor = connection.cursor()
            
            # Check record counts
            count_queries = [
                ('daily_predictions', 'Daily Predictions'),
                ('ai_predictions', 'AI Predictions'),
                ('price_logs', 'Price Logs')
            ]
            
            for table, description in count_queries:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    db_data['record_counts'][table] = count
                    print_success(f"{description}: {count:,} records")
                except psycopg2.Error as e:
                    print_warning(f"Could not count {table}: {e}")
            
            # Check data freshness
            freshness_queries = [
                ('daily_predictions', 'date', 'Daily Predictions'),
                ('price_logs', 'date', 'Price Logs'),
                ('ai_predictions', 'DATE(created_at)', 'AI Predictions')
            ]
            
            print_info("Data freshness check:")
            for table, date_col, description in freshness_queries:
                try:
                    cursor.execute(f"""
                        SELECT MAX({date_col}) as latest_date,
                               CURRENT_DATE - MAX({date_col}) as days_old
                        FROM {table}
                    """)
                    result = cursor.fetchone()
                    if result and result[0]:
                        latest_date, days_old = result
                        db_data['data_freshness'][table] = {
                            'latest_date': str(latest_date),
                            'days_old': days_old
                        }
                        
                        status_icon = "✅" if days_old <= 1 else "⚠️" if days_old <= 3 else "❌"
                        print_info(f"  {description}: {latest_date} ({days_old} days old) {status_icon}")
                    else:
                        print_warning(f"  {description}: No data found")
                        
                except psycopg2.Error as e:
                    print_warning(f"Could not check freshness for {table}: {e}")
            
            db_data['status'] = 'healthy'
            connection.close()
            
        except psycopg2.Error as e:
            print_error(f"Database connectivity check failed: {e}")
            db_data['status'] = 'failed'
        
        return db_data
    
    def check_render_service_status(self) -> Dict[str, Any]:
        """Check Render service status via CLI."""
        print_check("Checking Render service status...")
        
        service_data = {
            'status': 'unknown',
            'deploy_status': None,
            'resource_usage': {},
            'logs_available': False
        }
        
        if not self.service_id:
            print_warning("Service ID not available - run scripts/render-setup.sh first")
            service_data['status'] = 'not_configured'
            return service_data
        
        try:
            # Get service status
            result = subprocess.run(
                ['render', 'services', 'get', self.service_id, '--json'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                service_data['status'] = data.get('status', 'unknown')
                service_data['deploy_status'] = data.get('deployStatus', 'unknown')
                
                status = data.get('status', 'unknown')
                deploy_status = data.get('deployStatus', 'unknown')
                
                if status == 'live':
                    print_success(f"Service is live (deploy status: {deploy_status})")
                else:
                    print_warning(f"Service status: {status} (deploy: {deploy_status})")
                
                # Check resource usage if available
                if 'resourceUsage' in data:
                    usage = data['resourceUsage']
                    service_data['resource_usage'] = usage
                    print_metric(f"Resource usage: CPU {usage.get('cpu', 'N/A')}, Memory {usage.get('memory', 'N/A')}")
                
            else:
                print_error(f"Could not get service status: {result.stderr}")
                service_data['status'] = 'cli_failed'
                
        except subprocess.TimeoutExpired:
            print_error("Render CLI timeout - service status check failed")
            service_data['status'] = 'timeout'
        except FileNotFoundError:
            print_warning("Render CLI not found - install with scripts/render-setup.sh")
            service_data['status'] = 'cli_not_found'
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON from Render CLI: {e}")
            service_data['status'] = 'cli_error'
        
        # Check if logs are available
        try:
            result = subprocess.run(
                ['render', 'services', 'logs', self.service_id, '--tail', '1'],
                capture_output=True, text=True, timeout=10
            )
            service_data['logs_available'] = result.returncode == 0
            if result.returncode == 0:
                print_success("Service logs accessible")
            else:
                print_warning("Service logs not accessible")
                
        except Exception:
            service_data['logs_available'] = False
        
        return service_data
    
    def check_ai_service_health(self) -> Dict[str, Any]:
        """Check AI service health and recent predictions."""
        print_check("Checking AI service health...")
        
        ai_data = {
            'status': 'unknown',
            'recent_predictions': 0,
            'prediction_accuracy': None,
            'last_prediction_time': None
        }
        
        # Check via database if available
        if self.db_url and 'password' not in self.db_url:
            try:
                connection = psycopg2.connect(self.db_url)
                connection.set_session(readonly=True)
                cursor = connection.cursor()
                
                # Check recent AI predictions
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM ai_predictions 
                    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                """)
                recent_count = cursor.fetchone()[0]
                ai_data['recent_predictions'] = recent_count
                
                # Check latest prediction time
                cursor.execute("""
                    SELECT MAX(created_at)
                    FROM ai_predictions
                """)
                latest = cursor.fetchone()[0]
                if latest:
                    ai_data['last_prediction_time'] = latest.isoformat()
                    hours_ago = (datetime.now() - latest.replace(tzinfo=None)).total_seconds() / 3600
                    
                    if hours_ago <= 24:
                        print_success(f"AI predictions active: {recent_count} in last 7 days, latest {hours_ago:.1f}h ago")
                        ai_data['status'] = 'active'
                    else:
                        print_warning(f"AI predictions stale: latest {hours_ago:.1f}h ago")
                        ai_data['status'] = 'stale'
                else:
                    print_warning("No AI predictions found")
                    ai_data['status'] = 'no_data'
                
                # Check prediction accuracy
                cursor.execute("""
                    SELECT AVG(prediction_error) 
                    FROM ai_predictions 
                    WHERE actual_price IS NOT NULL
                        AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                avg_error = cursor.fetchone()[0]
                if avg_error:
                    ai_data['prediction_accuracy'] = float(avg_error)
                    print_metric(f"30-day average prediction error: ${avg_error:.2f}")
                
                connection.close()
                
            except psycopg2.Error as e:
                print_warning(f"Could not check AI service via database: {e}")
                ai_data['status'] = 'db_check_failed'
        
        # Try to check via API endpoint
        try:
            response = self.session.get(f"{self.base_url}/ai/predictions/latest")
            if response.status_code == 200:
                data = response.json()
                if data:
                    print_success("AI predictions API accessible")
                    if ai_data['status'] == 'unknown':
                        ai_data['status'] = 'api_accessible'
            elif response.status_code == 404:
                print_info("AI predictions API endpoint not found (may be normal)")
            else:
                print_warning(f"AI predictions API returned HTTP {response.status_code}")
                
        except requests.exceptions.RequestException:
            pass  # API check is secondary
        
        return ai_data
    
    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check and return results."""
        print(f"{Colors.BLUE}🏥 SPY TA Tracker - Comprehensive Production Health Check{Colors.NC}")
        print("=" * 70)
        print_info(f"Checking production environment: {self.base_url}")
        print_info(f"Service ID: {self.service_id or 'Not configured'}")
        print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'service_id': self.service_id,
            'checks': {}
        }
        
        # Run all health checks
        checks = [
            ('api', self.check_api_health),
            ('scheduler', self.check_scheduler_status),
            ('database', self.check_database_connectivity),
            ('render_service', self.check_render_service_status),
            ('ai_service', self.check_ai_service_health)
        ]
        
        for check_name, check_func in checks:
            print()
            try:
                check_result = check_func()
                results['checks'][check_name] = check_result
            except Exception as e:
                print_error(f"{check_name.title()} check failed with error: {e}")
                results['checks'][check_name] = {'status': 'error', 'error': str(e)}
        
        # Overall health assessment
        print()
        print("="*70)
        self.print_health_summary(results)
        
        return results
    
    def print_health_summary(self, results: Dict[str, Any]):
        """Print overall health summary."""
        print_check("Overall Health Summary:")
        
        checks = results['checks']
        total_checks = len(checks)
        healthy_checks = 0
        warnings = []
        errors = []
        
        for check_name, check_data in checks.items():
            status = check_data.get('status', 'unknown')
            
            if status in ['healthy', 'active', 'live', 'ok']:
                healthy_checks += 1
                print_success(f"{check_name.replace('_', ' ').title()}: Healthy")
            elif status in ['degraded', 'stale', 'not_found', 'api_accessible']:
                warnings.append(check_name)
                print_warning(f"{check_name.replace('_', ' ').title()}: {status.replace('_', ' ').title()}")
            elif status in ['failed', 'error', 'timeout']:
                errors.append(check_name)
                print_error(f"{check_name.replace('_', ' ').title()}: {status.replace('_', ' ').title()}")
            else:
                warnings.append(check_name)
                print_info(f"{check_name.replace('_', ' ').title()}: {status.replace('_', ' ').title()}")
        
        print()
        health_percentage = (healthy_checks / total_checks) * 100
        
        if health_percentage >= 80:
            print_success(f"🎉 Overall System Health: {health_percentage:.0f}% ({healthy_checks}/{total_checks} checks healthy)")
        elif health_percentage >= 60:
            print_warning(f"⚠️ Overall System Health: {health_percentage:.0f}% ({healthy_checks}/{total_checks} checks healthy)")
        else:
            print_error(f"🚨 Overall System Health: {health_percentage:.0f}% ({healthy_checks}/{total_checks} checks healthy)")
        
        if warnings:
            print_warning(f"Warnings in: {', '.join(warnings)}")
        if errors:
            print_error(f"Errors in: {', '.join(errors)}")
        
        # Recommendations
        print()
        print_info("📋 Recommendations:")
        if not self.service_id:
            print_info("  • Run scripts/render-setup.sh to configure Render CLI access")
        if self.db_url and 'password' in self.db_url:
            print_info("  • Update scripts/.env.production-readonly with actual database credentials")
        if errors:
            print_info("  • Investigate and resolve error conditions immediately")
        if warnings:
            print_info("  • Monitor warning conditions for potential issues")

def main():
    """Main health check interface."""
    parser = argparse.ArgumentParser(description='Production health check and monitoring')
    parser.add_argument('--url', type=str, default='https://spy-tracker.onrender.com',
                       help='Base URL for production API (default: https://spy-tracker.onrender.com)')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--save-report', type=str, metavar='FILE',
                       help='Save health check report to file')
    parser.add_argument('--api-only', action='store_true',
                       help='Run only API health checks (fastest)')
    parser.add_argument('--monitor', type=int, metavar='SECONDS',
                       help='Run health checks in monitoring mode (repeat every N seconds)')
    
    args = parser.parse_args()
    
    checker = ProductionHealthChecker(args.url)
    
    def run_health_check():
        if args.api_only:
            print(f"{Colors.BLUE}🚀 Quick API Health Check{Colors.NC}")
            print("=" * 40)
            api_health = checker.check_api_health()
            scheduler_health = checker.check_scheduler_status()
            
            if api_health['status'] == 'healthy' and scheduler_health['status'] == 'running':
                print_success("🎉 Core services are healthy!")
                return True
            else:
                print_error("❌ Core services have issues")
                return False
        else:
            results = checker.run_comprehensive_health_check()
            
            if args.json:
                print(json.dumps(results, indent=2))
            
            if args.save_report:
                with open(args.save_report, 'w') as f:
                    json.dump(results, f, indent=2)
                print_success(f"Health check report saved to {args.save_report}")
            
            return results['checks']
    
    if args.monitor:
        print_info(f"Starting health monitoring (checking every {args.monitor} seconds)")
        print_info("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                run_health_check()
                print()
                print_info(f"Next check in {args.monitor} seconds...")
                time.sleep(args.monitor)
        except KeyboardInterrupt:
            print_info("Health monitoring stopped")
    else:
        run_health_check()

if __name__ == "__main__":
    main()