#!/bin/bash

# K-Sphere Quick Deployment Script
# This script deploys K-Sphere on any machine with Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 K-Sphere Quick Deployment${NC}"
echo "================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed.${NC}"
    echo -e "${YELLOW}Please install Docker first:${NC}"
    echo "• macOS: https://docs.docker.com/desktop/mac/install/"
    echo "• Windows: https://docs.docker.com/desktop/windows/install/"
    echo "• Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running.${NC}"
    echo -e "${YELLOW}Please start Docker Desktop and try again.${NC}"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed.${NC}"
    echo -e "${YELLOW}Please install Docker Compose: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is ready!${NC}"
echo ""

# Create deployment directory
DEPLOY_DIR="k-sphere-deployment"
echo -e "${BLUE}📁 Creating deployment directory: ${DEPLOY_DIR}${NC}"
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# Download the production configuration
echo -e "${BLUE}📥 Downloading configuration...${NC}"
curl -s -O https://raw.githubusercontent.com/birajdarushi/k-sphere/main/docker-compose.production.yml

if [ ! -f "docker-compose.production.yml" ]; then
    echo -e "${RED}❌ Failed to download configuration file.${NC}"
    exit 1
fi

# Rename for convenience
mv docker-compose.production.yml docker-compose.yml

echo -e "${GREEN}✅ Configuration downloaded!${NC}"
echo ""

# Check system resources
echo -e "${BLUE}🔍 Checking system resources...${NC}"
TOTAL_MEM=$(docker system info --format "{{.MemTotal}}" 2>/dev/null || echo "0")
if [ "$TOTAL_MEM" -lt 4000000000 ]; then
    echo -e "${YELLOW}⚠️  Warning: Less than 4GB RAM detected. Performance may be limited.${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Starting K-Sphere...${NC}"
echo "This may take a few minutes on first run as Docker downloads the images."
echo ""

# Pull images first (faster feedback)
echo -e "${BLUE}📥 Pulling Docker images...${NC}"
docker-compose pull

# Start services
echo -e "${BLUE}🔄 Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo ""
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 10

# Check service status
echo -e "${BLUE}📊 Checking service status...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}🎉 K-Sphere is starting up!${NC}"
echo ""
echo -e "${YELLOW}📋 Service URLs:${NC}"
echo "• Frontend (Main App): ${BLUE}http://localhost:3000${NC}"
echo "• Backend API: ${BLUE}http://localhost:8000${NC}"
echo "• API Documentation: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}📝 Useful Commands:${NC}"
echo "• View logs: ${BLUE}docker-compose logs${NC}"
echo "• Stop services: ${BLUE}docker-compose down${NC}"
echo "• Restart services: ${BLUE}docker-compose restart${NC}"
echo "• Check status: ${BLUE}docker-compose ps${NC}"
echo ""
echo -e "${YELLOW}⏱️  Note: AI models are downloading in background.${NC}"
echo -e "${YELLOW}   The first chat may take 2-3 minutes to respond.${NC}"
echo ""
echo -e "${GREEN}✨ Installation complete! Visit http://localhost:3000 to get started.${NC}"