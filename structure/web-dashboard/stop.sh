#!/bin/bash

# Stop the Migration Dashboard
# Usage: ./stop.sh [PORT]
# Default port: 5001

# Get port from argument or use default
PORT=${1:-5001}

echo "============================================================"
echo "🛑 Stopping Migration Dashboard (Port $PORT)"
echo "============================================================"

# Find processes using the specified port
PIDS=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "❌ No process found running on port $PORT"
    
    # Also try to find Python processes running run.py or app.py as fallback
    PIDS=$(ps aux | grep -E "python.*run\.py|python.*app\.py" | grep -v grep | awk '{print $2}')
    
    if [ -z "$PIDS" ]; then
        echo "❌ No dashboard process found running"
        exit 0
    else
        echo "Found dashboard process(es) by name: $PIDS"
    fi
else
    echo "Found process(es) on port $PORT: $PIDS"
fi

# Kill the processes
for PID in $PIDS; do
    echo "Stopping process $PID..."
    kill -9 $PID 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ Process $PID stopped"
    else
        echo "⚠ Failed to stop process $PID (may have already stopped)"
    fi
done

echo "============================================================"
echo "✓ Dashboard stopped"
echo "============================================================"
