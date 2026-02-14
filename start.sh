#!/bin/bash
# Start YoLink Temperature Monitor Web Server

cd "$(dirname "$0")"

echo "YoLink Temperature Monitor - Startup Script"
echo "==========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if port is already in use
PORT=$(grep "^PORT" config.py | cut -d'=' -f2 | tr -d ' ')
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use!"
    echo "Edit config.py to change the PORT setting."
    exit 1
fi

echo "✓ Starting web server..."
echo ""

# Start the server
./venv/bin/python web_server.py
