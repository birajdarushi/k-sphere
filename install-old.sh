#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════╗"
echo "║         K-Sphere Installation Script         ║"
echo "║      Portable AI Knowledge Management        ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker is installed
echo -e "${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found.${NC}"
    echo -e "${YELLOW}Installing Docker...${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${BLUE}ℹ️  On macOS, please install Docker Desktop from:${NC}"
        echo "   https://www.docker.com/products/docker-desktop"
        echo ""
        echo "After installation, run this script again."
        exit 1
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Install Docker on Linux
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        echo -e "${GREEN}✅ Docker installed successfully${NC}"
        echo -e "${YELLOW}⚠️  Please log out and log back in for group changes to take effect${NC}"
        echo "Then run this script again."
        exit 0
    fi
else
    echo -e "${GREEN}✅ Docker is installed${NC}"
fi

# Check if Docker Compose is available
echo -e "${YELLOW}Checking Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose not found.${NC}"
        echo -e "${YELLOW}Installing Docker Compose...${NC}"
        
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo -e "${GREEN}✅ Docker Compose installed${NC}"
    else
        COMPOSE_CMD="docker-compose"
    fi
else
    COMPOSE_CMD="docker compose"
fi

# Create data directory for persistence
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p data/uploads data/vectordb data/logs

# Check for GPU support (NVIDIA)
echo -e "${YELLOW}Checking for GPU support...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ NVIDIA GPU detected${NC}"
    
    # Check if nvidia-container-toolkit is installed
    if ! docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
        echo -e "${YELLOW}⚠️  NVIDIA Container Toolkit not found${NC}"
        echo -e "${BLUE}ℹ️  Install it with:${NC}"
        echo "   distribution=\$(. /etc/os-release;echo \$ID\$VERSION_ID)"
        echo "   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -"
        echo "   curl -s -L https://nvidia.github.io/nvidia-docker/\$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list"
        echo "   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit"
        echo "   sudo systemctl restart docker"
        echo ""
        read -p "Do you want to enable GPU support in docker-compose.yml? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Uncomment GPU lines in docker-compose.yml
            sed -i.bak 's/# \(deploy:\)/\1/' docker-compose.yml
            sed -i.bak 's/#   \(resources:\)/  \1/' docker-compose.yml
            sed -i.bak 's/#     \(reservations:\)/    \1/' docker-compose.yml
            sed -i.bak 's/#       \(devices:\)/      \1/' docker-compose.yml
            sed -i.bak 's/#         \(- driver: nvidia\)/        \1/' docker-compose.yml
            sed -i.bak 's/#           \(count: all\)/          \1/' docker-compose.yml
            sed -i.bak 's/#           \(capabilities: \[gpu\]\)/          \1/' docker-compose.yml
            echo -e "${GREEN}✅ GPU support enabled${NC}"
        fi
    else
        echo -e "${GREEN}✅ NVIDIA Container Toolkit is ready${NC}"
    fi
else
    echo -e "${BLUE}ℹ️  No NVIDIA GPU detected. Running in CPU mode.${NC}"
fi

# Pull and build Docker images
echo -e "${YELLOW}Building Docker images...${NC}"
echo -e "${BLUE}This may take 5-10 minutes on first run...${NC}"
$COMPOSE_CMD build

# Start containers
echo -e "${YELLOW}Starting K-Sphere containers...${NC}"
$COMPOSE_CMD up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Check if services are running
if docker ps | grep -q "k-sphere-backend"; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check logs with: $COMPOSE_CMD logs backend"
fi

if docker ps | grep -q "k-sphere-frontend"; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo "Check logs with: $COMPOSE_CMD logs frontend"
fi

if docker ps | grep -q "k-sphere-ollama"; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${RED}❌ Ollama failed to start${NC}"
    echo "Check logs with: $COMPOSE_CMD logs ollama"
fi

# Pull default AI models
echo -e "${YELLOW}Pulling default AI models...${NC}"
echo -e "${BLUE}ℹ️  This will download ~2GB of data. Please wait...${NC}"

docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ K-Sphere installed successfully!        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Access K-Sphere at:${NC}"
echo -e "   🌐 Main App:      ${GREEN}http://localhost:3000${NC}"
echo -e "   🔧 Backend API:   ${GREEN}http://localhost:8000${NC}"
echo -e "   📊 Vector DB Viz: ${GREEN}http://localhost:8001/ui${NC}"
echo ""
echo -e "${BLUE}📝 Useful commands:${NC}"
echo "   Start:   $COMPOSE_CMD up -d"
echo "   Stop:    $COMPOSE_CMD down"
echo "   Logs:    $COMPOSE_CMD logs -f"
echo "   Status:  docker ps"
echo ""
echo -e "${YELLOW}💡 Tip: All your data is stored in ./data/ directory${NC}"
echo ""
