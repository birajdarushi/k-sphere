#!/bin/bash

# K-Sphere Stop Script
# Stops all K-Sphere services

echo "🛑 Stopping K-Sphere services..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Stop backend
if [ -f "$DIR/.backend.pid" ]; then
    PID=$(cat "$DIR/.backend.pid")
    if ps -p $PID > /dev/null; then
        kill $PID
        echo -e "${GREEN}✓${NC} Stopped backend (PID: $PID)"
    fi
    rm "$DIR/.backend.pid"
fi

# Stop debug server
if [ -f "$DIR/.debug.pid" ]; then
    PID=$(cat "$DIR/.debug.pid")
    if ps -p $PID > /dev/null; then
        kill $PID
        echo -e "${GREEN}✓${NC} Stopped debug server (PID: $PID)"
    fi
    rm "$DIR/.debug.pid"
fi

# Stop any remaining processes on ports
for port in 8000 8001; do
    PID=$(lsof -ti:$port)
    if [ ! -z "$PID" ]; then
        kill $PID 2>/dev/null
        echo -e "${GREEN}✓${NC} Stopped process on port $port"
    fi
done

echo ""
echo -e "${GREEN}✨ All K-Sphere services stopped${NC}"
echo ""
echo "Note: Ollama is still running. Stop it with: pkill ollama"
