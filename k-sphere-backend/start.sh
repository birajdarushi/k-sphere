#!/bin/bash

# K-Sphere Backend Startup Script

echo "========================================"
echo "   K-Sphere AI Backend Startup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}✗ Ollama is not installed.${NC}"
    echo "Please install Ollama: brew install ollama"
    exit 1
fi

echo -e "${GREEN}✓ Ollama found${NC}"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo -e "${YELLOW}⚠ Ollama is not running. Starting Ollama...${NC}"
    ollama serve &
    sleep 3
fi

echo -e "${GREEN}✓ Ollama is running${NC}"

# Check if required models are installed
echo ""
echo "Checking Ollama models..."

MODELS=$(ollama list 2>/dev/null | awk '{print $1}' | tail -n +2)

if ! echo "$MODELS" | grep -q "llama3.2:3b"; then
    echo -e "${YELLOW}⚠ LLM model 'llama3.2:3b' not found${NC}"
    echo "Pulling llama3.2:3b model (this may take a few minutes)..."
    ollama pull llama3.2:3b
fi

if ! echo "$MODELS" | grep -q "nomic-embed-text"; then
    echo -e "${YELLOW}⚠ Embedding model 'nomic-embed-text' not found${NC}"
    echo "Pulling nomic-embed-text model..."
    ollama pull nomic-embed-text
fi

echo -e "${GREEN}✓ All required models are available${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
if [ -f "requirements.txt" ]; then
    echo ""
    echo "Installing Python dependencies (this may take a few minutes)..."
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Ensure data directories exist
mkdir -p data/uploads data/vectordb logs

echo ""
echo "========================================"
echo "   Starting K-Sphere AI Backend"
echo "========================================"
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend should be running on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
python main.py
