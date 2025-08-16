#!/bin/bash

# PostgreSQL Setup Checker for SPY TA Tracker
# This script verifies your PostgreSQL setup and provides troubleshooting guidance

set -e

echo "🔍 SPY TA Tracker - PostgreSQL Setup Checker"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_success() {
    print_status $GREEN "✅ $1"
}

print_error() {
    print_status $RED "❌ $1"
}

print_warning() {
    print_status $YELLOW "⚠️  $1"
}

print_info() {
    print_status $BLUE "ℹ️  $1"
}

# Check if Docker is available
echo ""
echo "1. Checking Docker availability..."
if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        print_success "Docker is installed and running"
    else
        print_error "Docker is installed but not running"
        print_info "Start Docker Desktop or run: sudo systemctl start docker"
        exit 1
    fi
else
    print_error "Docker is not installed"
    print_info "Install Docker Desktop: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
echo ""
echo "2. Checking Docker Compose..."
if command -v docker-compose >/dev/null 2>&1; then
    print_success "docker-compose is available"
elif docker compose version >/dev/null 2>&1; then
    print_success "docker compose (v2) is available"
    alias docker-compose='docker compose'
else
    print_error "Docker Compose is not available"
    print_info "Install Docker Compose or update Docker Desktop"
    exit 1
fi

# Check for docker-compose.yml
echo ""
echo "3. Checking project configuration..."
if [ -f "docker-compose.yml" ]; then
    print_success "docker-compose.yml found"
else
    print_error "docker-compose.yml not found"
    print_info "Run this script from the project root directory"
    exit 1
fi

# Check if PostgreSQL container exists
echo ""
echo "4. Checking PostgreSQL container status..."
if docker ps -a --format "table {{.Names}}" | grep -q "^spydb$"; then
    if docker ps --format "table {{.Names}}" | grep -q "^spydb$"; then
        print_success "PostgreSQL container 'spydb' is running"
    else
        print_warning "PostgreSQL container 'spydb' exists but is stopped"
        print_info "Starting container..."
        docker start spydb
        sleep 3
        if docker ps --format "table {{.Names}}" | grep -q "^spydb$"; then
            print_success "PostgreSQL container started successfully"
        else
            print_error "Failed to start PostgreSQL container"
            print_info "Check logs: docker logs spydb"
        fi
    fi
else
    print_info "PostgreSQL container 'spydb' does not exist"
    print_info "Starting PostgreSQL with docker-compose..."
    docker-compose up -d db
    sleep 5
    if docker ps --format "table {{.Names}}" | grep -q "^spydb$"; then
        print_success "PostgreSQL container created and started"
    else
        print_error "Failed to create PostgreSQL container"
        print_info "Check logs: docker-compose logs db"
        exit 1
    fi
fi

# Check PostgreSQL health
echo ""
echo "5. Checking PostgreSQL health..."
max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker-compose exec -T db pg_isready -U spy -d spy >/dev/null 2>&1; then
        print_success "PostgreSQL is healthy and accepting connections"
        break
    else
        if [ $attempt -eq $max_attempts ]; then
            print_error "PostgreSQL health check failed after $max_attempts attempts"
            print_info "Check logs: docker-compose logs db"
            exit 1
        else
            print_info "Waiting for PostgreSQL to be ready... (attempt $attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    fi
done

# Test connection with actual credentials
echo ""
echo "6. Testing database connection..."
if docker-compose exec -T db psql -U spy -d spy -c "SELECT version();" >/dev/null 2>&1; then
    print_success "Database connection successful"
    
    # Get PostgreSQL version
    PG_VERSION=$(docker-compose exec -T db psql -U spy -d spy -t -c "SELECT version();" 2>/dev/null | head -1 | xargs)
    print_info "PostgreSQL version: $PG_VERSION"
else
    print_error "Database connection failed"
    print_info "Check credentials in docker-compose.yml"
    exit 1
fi

# Check port accessibility from host
echo ""
echo "7. Checking port accessibility..."
if nc -z localhost 5433 2>/dev/null; then
    print_success "Port 5433 is accessible on localhost"
else
    print_warning "Port 5433 may not be accessible"
    print_info "Check if another service is using port 5433: lsof -i :5433"
fi

# Check environment files
echo ""
echo "8. Checking environment configuration..."
if [ -f ".env" ]; then
    if grep -q "DATABASE_URL.*postgresql" .env; then
        print_success "Root .env file configured for PostgreSQL"
    elif grep -q "DATABASE_URL.*sqlite" .env; then
        print_warning "Root .env file is configured for SQLite"
        print_info "Update DATABASE_URL in .env to use PostgreSQL:"
        print_info "DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy"
    else
        print_warning "DATABASE_URL not found in .env"
        print_info "Add to .env: DATABASE_URL=postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy"
    fi
else
    print_warning ".env file not found"
    print_info "Copy .env.example to .env and configure DATABASE_URL"
fi

if [ -f "backend/.env" ]; then
    if grep -q "DATABASE_URL.*postgresql" backend/.env; then
        print_success "Backend .env file configured for PostgreSQL"
    else
        print_info "Backend .env file exists but may need PostgreSQL configuration"
    fi
else
    print_info "Backend .env file not found (optional)"
fi

# Test actual application connection
echo ""
echo "9. Testing application database connection..."
if [ -d "backend" ] && [ -f "backend/app/main.py" ]; then
    # Check if virtual environment exists
    if [ -d "backend/.venv" ]; then
        print_info "Testing Python database connection..."
        cd backend
        source .venv/bin/activate 2>/dev/null || true
        
        # Set DATABASE_URL for test
        export DATABASE_URL="postgresql+psycopg2://spy:pass@127.0.0.1:5433/spy"
        
        # Test connection with Python
        if python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    if result and result[0] == 1:
        print('✅ Python database connection successful')
    else:
        print('❌ Python database connection failed')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ Python database connection error: {e}')
" 2>/dev/null; then
            print_success "Python application can connect to PostgreSQL"
        else
            print_warning "Python application connection test failed"
            print_info "This may be normal if dependencies aren't installed yet"
        fi
        cd ..
    else
        print_info "Backend virtual environment not found - skipping Python test"
    fi
else
    print_info "Backend application not found - skipping application test"
fi

# Final summary and recommendations
echo ""
echo "=========================================="
echo "🎉 PostgreSQL Setup Check Complete"
echo "=========================================="

# Check if Adminer is available
if docker ps --format "table {{.Names}}" | grep -q "spy-adminer"; then
    print_success "Adminer is running at http://localhost:8080"
else
    print_info "To start Adminer (database admin): docker-compose --profile tools up -d"
fi

echo ""
print_info "Next steps:"
echo "  1. Ensure .env is configured with PostgreSQL URL"
echo "  2. Run: ./start.sh (will use PostgreSQL automatically)"
echo "  3. Access app at http://localhost:3000"
echo "  4. View API docs at http://localhost:8000/docs"

echo ""
print_info "Useful commands:"
echo "  • Start just database: docker-compose up -d db"
echo "  • Start with admin tools: docker-compose --profile tools up -d"
echo "  • View database logs: docker-compose logs db"
echo "  • Reset database: docker-compose down -v && docker-compose up -d db"
echo "  • Access database: docker-compose exec db psql -U spy -d spy"

echo ""
print_info "Documentation:"
echo "  • PostgreSQL Setup Guide: docs/POSTGRES_SETUP.md"
echo "  • Migration Guide: docs/DATABASE_MIGRATION_GUIDE.md"
echo "  • Docker Reference: docs/DOCKER_COMPOSE_REFERENCE.md"

echo ""
print_success "PostgreSQL setup verification complete!"