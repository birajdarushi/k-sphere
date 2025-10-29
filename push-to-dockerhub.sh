#!/bin/bash

# K-Sphere Docker Hub Push Script
# This script tags and pushes your K-Sphere images to Docker Hub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}K-Sphere Docker Hub Push Script${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Get Docker Hub username
echo -e "${YELLOW}Enter your Docker Hub username:${NC}"
read -r DOCKERHUB_USERNAME

if [ -z "$DOCKERHUB_USERNAME" ]; then
    echo -e "${RED}Error: Docker Hub username cannot be empty${NC}"
    exit 1
fi

# Login to Docker Hub
echo -e "${YELLOW}Logging into Docker Hub...${NC}"
docker login

# Tag the images
echo -e "${YELLOW}Tagging images...${NC}"
docker tag k-sphere-backend:latest $DOCKERHUB_USERNAME/k-sphere-backend:latest
docker tag k-sphere-frontend:latest $DOCKERHUB_USERNAME/k-sphere-frontend:latest

# Also tag with version
VERSION="v1.0.0"
docker tag k-sphere-backend:latest $DOCKERHUB_USERNAME/k-sphere-backend:$VERSION
docker tag k-sphere-frontend:latest $DOCKERHUB_USERNAME/k-sphere-frontend:$VERSION

# Push the images
echo -e "${YELLOW}Pushing backend image...${NC}"
docker push $DOCKERHUB_USERNAME/k-sphere-backend:latest
docker push $DOCKERHUB_USERNAME/k-sphere-backend:$VERSION

echo -e "${YELLOW}Pushing frontend image...${NC}"
docker push $DOCKERHUB_USERNAME/k-sphere-frontend:latest
docker push $DOCKERHUB_USERNAME/k-sphere-frontend:$VERSION

# Update the production docker-compose file
echo -e "${YELLOW}Updating production docker-compose file...${NC}"
sed -i.bak "s/YOUR_DOCKERHUB_USERNAME/$DOCKERHUB_USERNAME/g" docker-compose.production.yml

echo -e "${GREEN}✅ Images successfully pushed to Docker Hub!${NC}"
echo ""
echo "Your images are now available at:"
echo "- https://hub.docker.com/r/$DOCKERHUB_USERNAME/k-sphere-backend"
echo "- https://hub.docker.com/r/$DOCKERHUB_USERNAME/k-sphere-frontend"
echo ""
echo "To use these images on any machine:"
echo "1. Copy the docker-compose.production.yml file"
echo "2. Run: docker-compose -f docker-compose.production.yml up -d"
echo ""
echo -e "${YELLOW}Don't forget to update your Git repository with the new docker-compose.production.yml file!${NC}"