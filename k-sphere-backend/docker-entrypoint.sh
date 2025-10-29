#!/bin/bash
set -e

# Start main backend server in background
echo "Starting main backend server on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Wait a moment for main server to initialize
sleep 2

# Start debug server in background
echo "Starting debug/visualization server on port 8001..."
python debug_server.py &

# Wait for all background processes
wait -n

# Exit with status of process that exited first
exit $?
