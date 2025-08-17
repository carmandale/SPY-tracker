#!/bin/bash

# Wrapper script for production health check
# Ensures proper Python environment is used

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

print_info "SPY TA Tracker - Production Health Check"
print_info "========================================"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    print_error "Virtual environment not found: $BACKEND_DIR/.venv"
    print_info "Please set up the backend environment first:"
    print_info "  cd backend && uv venv && uv pip sync pyproject.toml"
    exit 1
fi

# Activate virtual environment and run health check
cd "$BACKEND_DIR"
print_info "Activating virtual environment..."

if source .venv/bin/activate; then
    print_success "Virtual environment activated"
    
    # Run the health check with the provided arguments
    print_info "Running production health check..."
    python "$SCRIPT_DIR/production-health-check.py" "$@"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi