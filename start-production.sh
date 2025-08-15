#!/bin/bash

# Production Startup Script for SPY TA Tracker
# This script starts the backend in production mode and ensures it stays running

set -e  # Exit on error

echo "🚀 Starting SPY TA Tracker - PRODUCTION MODE"
echo "============================================="

# Change to project directory
cd "$(dirname "$0")"

# Load environment variables from backend/.env
if [ -f backend/.env ]; then
    echo "📋 Loading backend environment from backend/.env"
    set -a  # automatically export all variables
    source backend/.env
    set +a  # turn off auto-export
fi

# Ensure OpenAI API key is available
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ Warning: OPENAI_API_KEY not set - AI predictions will not work"
else
    echo "✅ OpenAI API key configured"
fi

# Set timezone for scheduler
export TZ="America/Chicago"
echo "⏰ Timezone set to: $TZ"

# Set production environment
export ENVIRONMENT=production

# Use the configured database URL from .env (should point to port 5433)
echo "🗄️ Database: $DATABASE_URL"

# Check database connectivity
echo "🔍 Checking database connectivity..."
cd backend
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run 'uv venv' first."
    exit 1
fi

# Test database connection
python -c "
import psycopg2
import os
try:
    # Remove the postgresql+ prefix if present for psycopg2
    db_url = os.environ['DATABASE_URL'].replace('postgresql+psycopg2://', 'postgresql://')
    conn = psycopg2.connect(db_url)
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" || exit 1

cd ..

echo ""
echo "📡 Starting Backend Server in Production Mode..."

# Start backend in production mode
cd backend

# Ensure dependencies are installed
echo "   Installing/updating Python dependencies..."
uv pip install -r requirements.txt

# Start the server with production settings
echo "   Starting FastAPI server on port 8000..."

# Use nohup to keep the process running even if terminal is closed
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 > ../server.log 2>&1 &
SERVER_PID=$!

# Store the PID for later management
echo $SERVER_PID > ../server.pid

cd ..

echo ""
echo "✅ Production server started!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:8000 (served by backend)"
echo "   API Docs: http://localhost:8000/docs"
echo "   Process ID: $SERVER_PID"
echo "   Log file: server.log"
echo ""
echo "🤖 AI Features Active:"
echo "   • 8:00 AM CST - AI predictions generation"
echo "   • Automated price capture at market checkpoints"
echo "   • GPT-5 powered market analysis"
echo ""
echo "📊 Scheduler Jobs Active:"
echo "   • Pre-market: 8:00 AM CST"
echo "   • Open: 8:30 AM CST"
echo "   • Noon: 12:00 PM CST" 
echo "   • 2PM: 2:00 PM CST"
echo "   • Close: 3:00 PM CST"
echo ""
echo "💡 Management Commands:"
echo "   • Check status: ps aux | grep uvicorn"
echo "   • View logs: tail -f server.log"
echo "   • Stop server: kill $SERVER_PID"
echo "   • Restart: ./start-production.sh"

# Wait a moment and check if the server started successfully
sleep 3
if ps -p $SERVER_PID > /dev/null; then
    echo ""
    echo "🎉 Server is running successfully!"
    echo "Ready for 8:00 AM CST automated predictions"
else
    echo ""
    echo "❌ Server failed to start. Check server.log for details:"
    echo "   tail server.log"
    exit 1
fi