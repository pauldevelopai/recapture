#!/bin/bash

# Project Directory
PROJECT_DIR="/Users/paulmcnally/Developai Dropbox/Paul McNally/Mac/Documents/ONMAC/PYTHON 2025/recapture"

cd "$PROJECT_DIR" || exit

echo "🚀 Starting Recapture..."

# Function to cleanup background processes
cleanup() {
    echo "Shutting down..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Kill existing processes on ports
echo "🧹 Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start Backend
echo "Starting Backend (Port 8000)..."
# Check if virtual environment exists and activate it if so
if [ -d "venv" ]; then
    source venv/bin/activate
fi
uvicorn backend.main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend (Port 5173)..."
cd frontend || exit
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ App is running!"
echo "👉 Access at http://localhost:5173"
echo "📝 Logs: backend.log, frontend.log"
echo "Press Ctrl+C to stop."

# Wait for processes
wait
