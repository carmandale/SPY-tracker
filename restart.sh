#!/bin/bash

# SPY TA Tracker - Restart Script
# Safely restart the production server

PROJECT_DIR="/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/SPY-tracker"
cd "$PROJECT_DIR"

echo "🔄 Restarting SPY TA Tracker..."

# Stop existing server if running
if [ -f "server.pid" ]; then
    PID=$(cat server.pid)
    echo "🛑 Stopping existing server (PID: $PID)..."
    kill $PID 2>/dev/null || echo "   Process already stopped"
    sleep 2
    
    # Force kill if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "   Force killing process..."
        kill -9 $PID 2>/dev/null
    fi
    
    rm -f server.pid
fi

# Clean up any orphaned processes
pkill -f "uvicorn.*app.main:app" || true

echo "🚀 Starting fresh server..."
./start-production.sh