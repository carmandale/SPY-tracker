#!/bin/bash

# SPY TA Tracker - Production Monitor Script
# Use this to check server status and restart if needed

PROJECT_DIR="/Users/dalecarman/Groove Jones Dropbox/Dale Carman/Projects/dev/SPY-tracker"
cd "$PROJECT_DIR"

echo "🔍 SPY TA Tracker - Production Status Check"
echo "=========================================="

# Check if server.pid exists
if [ -f "server.pid" ]; then
    PID=$(cat server.pid)
    echo "📝 Stored PID: $PID"
    
    # Check if process is running
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Server is running (PID: $PID)"
        echo "🌐 Frontend: http://localhost:8000"
        echo "📊 API Docs: http://localhost:8000/docs"
        
        # Test health endpoint
        echo ""
        echo "🏥 Health Check:"
        if curl -s http://localhost:8000/healthz | grep -q "ok"; then
            echo "✅ Health check passed"
        else
            echo "❌ Health check failed"
        fi
        
        # Check scheduler
        echo ""
        echo "⏰ Scheduler Status:"
        SCHEDULER_STATUS=$(curl -s http://localhost:8000/scheduler/status | grep -o '"scheduler_running":[^,]*')
        if echo "$SCHEDULER_STATUS" | grep -q "true"; then
            echo "✅ Scheduler is running"
            
            # Get next AI prediction time
            NEXT_AI=$(curl -s http://localhost:8000/scheduler/status | grep -o '"next_run_time":"[^"]*' | grep ai_predict | head -1 | cut -d'"' -f4)
            echo "🤖 Next AI prediction: $NEXT_AI"
        else
            echo "❌ Scheduler not running"
        fi
        
        # Show recent log entries
        echo ""
        echo "📋 Recent Logs (last 5 lines):"
        tail -5 server.log 2>/dev/null || echo "No log file found"
        
    else
        echo "❌ Server process not running (PID $PID not found)"
        echo "🔄 Attempting restart..."
        rm -f server.pid
        ./start-production.sh
    fi
else
    echo "❌ No server.pid file found"
    echo "🔄 Starting server..."
    ./start-production.sh
fi

echo ""
echo "💡 Management Commands:"
echo "   • Monitor: ./monitor.sh"
echo "   • Restart: ./start-production.sh" 
echo "   • Stop: kill \$(cat server.pid)"
echo "   • Logs: tail -f server.log"