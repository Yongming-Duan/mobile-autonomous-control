#!/bin/sh
# Start sensor server in background

echo "Starting Sensor HTTP Server..."

# Kill any existing server
killall python 2>/dev/null

# Wait a moment
sleep 2

# Start server in background
cd /sdcard
nohup python sensor_server.py > /sdcard/server.log 2>&1 &

# Wait for server to start
sleep 3

# Check if server is running
if ps | grep -v grep | grep python > /dev/null; then
    echo "✓ Server started successfully"
    echo ""
    echo "Server log:"
    cat /sdcard/server.log
    echo ""
    echo "Testing server..."
    curl -s http://127.0.0.1:9999/health
    echo ""
else
    echo "✗ Failed to start server"
    cat /sdcard/server.log
fi
