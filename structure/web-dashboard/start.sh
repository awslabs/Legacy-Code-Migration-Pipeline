#!/bin/bash

# Migration Dashboard Startup Script
# Usage: ./start.sh [PORT]
# Default port: 5001

# Get port from argument or use default
PORT=${1:-5001}

echo "🚀 Starting Migration Dashboard..."
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the web-dashboard directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if output directory exists
OUTPUT_DIR="../output"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "⚠️  Warning: Output directory not found at $OUTPUT_DIR"
    echo "   The dashboard will still start but may not show data until migration is run."
fi

# Start the dashboard
echo "🌐 Starting dashboard server..."
echo "   URL: http://localhost:$PORT"
echo "   Press Ctrl+C to stop"
echo ""

export FLASK_PORT=$PORT
python3 app.py