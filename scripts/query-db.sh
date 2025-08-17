#!/bin/bash

# Wrapper script for database queries
# Ensures proper Python environment is used

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "🔍 SPY TA Tracker - Database Query Tool"
echo "========================================"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend directory not found: $BACKEND_DIR"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo "❌ Virtual environment not found: $BACKEND_DIR/.venv"
    echo "Please set up the backend environment first:"
    echo "  cd backend && uv venv && uv pip sync pyproject.toml"
    exit 1
fi

# Activate virtual environment and run queries
cd "$BACKEND_DIR"
echo "ℹ️ Activating virtual environment..."

if source .venv/bin/activate; then
    echo "✅ Virtual environment activated"
    echo "ℹ️ Running database query tool..."
    python "$SCRIPT_DIR/query-production-db.py" "$@"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi