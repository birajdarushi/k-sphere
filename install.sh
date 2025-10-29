#!/bin/bash

###############################################################################
# K-Sphere One-Click Installer
# 
# This script sets up and runs the complete K-Sphere AI system
# Requirements: Docker and Docker Compose
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██╗  ██╗      ███████╗██████╗ ██╗  ██╗███████╗██████╗  ║
║   ██║ ██╔╝      ██╔════╝██╔══██╗██║  ██║██╔════╝██╔══██╗ ║
║   █████╔╝ █████╗███████╗██████╔╝███████║█████╗  ██████╔╝ ║
║   ██╔═██╗ ╚════╝╚════██║██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗ ║
║   ██║  ██╗      ███████║██║     ██║  ██║███████╗██║  ██║ ║
║   ╚═╝  ╚═╝      ╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ║
║                                                           ║
║           AI-Powered Knowledge Management System          ║
║                      One-Click Installer                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_success() {
    print_message "$GREEN" "✓ $1"
}

print_error() {
    print_message "$RED" "✗ $1"
}

print_warning() {
    print_message "$YELLOW" "⚠ $1"
}

print_info() {
    print_message "$BLUE" "ℹ $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker
check_docker() {
    print_info "Checking Docker installation..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        print_info "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running"
        print_info "Please start Docker Desktop and try again"
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Function to check Docker Compose
check_docker_compose() {
    print_info "Checking Docker Compose..."
    
    if ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not available"
        print_info "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Function to check system resources
check_system_resources() {
    print_info "Checking system resources..."
    
    # Check available disk space (require at least 10GB)
    if command_exists df; then
        available_space=$(df -k . | awk 'NR==2 {print $4}')
        required_space=$((10 * 1024 * 1024))  # 10GB in KB
        
        if [ "$available_space" -lt "$required_space" ]; then
            print_warning "Low disk space detected (< 10GB free)"
            print_info "K-Sphere requires at least 10GB of free space for AI models and data"
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
    
    print_success "System resources check passed"
}

# Function to create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    mkdir -p k-sphere-backend/data/uploads
    mkdir -p k-sphere-backend/data/vectordb
    mkdir -p k-sphere-backend/logs
    
    print_success "Directories created"
}

# Function to check if ports are available
check_ports() {
    print_info "Checking if required ports are available..."
    
    ports=(3000 8000 11434)
    occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep -q ":$port.*LISTEN"; then
            occupied_ports+=($port)
        fi
    done
    
    if [ ${#occupied_ports[@]} -gt 0 ]; then
        print_warning "The following ports are already in use: ${occupied_ports[*]}"
        print_info "Ports needed: 3000 (Frontend), 8000 (Backend), 11434 (Ollama)"
        read -p "Stop services on these ports and continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "All required ports are available"
    fi
}

# Function to pull/build Docker images
build_images() {
    print_info "Building Docker images (this may take 5-10 minutes)..."
    
    if ! docker compose build --parallel; then
        print_error "Failed to build Docker images"
        exit 1
    fi
    
    print_success "Docker images built successfully"
}

# Function to start services
start_services() {
    print_info "Starting K-Sphere services..."
    
    if ! docker compose up -d; then
        print_error "Failed to start services"
        exit 1
    fi
    
    print_success "Services started"
}

# Function to wait for services to be healthy
wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    echo -n "  Ollama: "
    max_attempts=60
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker exec k-sphere-ollama ollama list >/dev/null 2>&1; then
            print_success "Ready"
            break
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Ollama failed to start"
        exit 1
    fi
    
    echo -n "  Backend: "
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Ready"
            break
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Backend failed to start"
        docker compose logs backend
        exit 1
    fi
    
    echo -n "  Frontend: "
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:3000 >/dev/null 2>&1; then
            print_success "Ready"
            break
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Frontend failed to start"
        docker compose logs frontend
        exit 1
    fi
}

# Function to download AI models
download_models() {
    print_info "Downloading AI models (this may take 10-20 minutes)..."
    
    print_info "  Downloading llama3.2:3b (2GB)..."
    if ! docker exec k-sphere-ollama ollama pull llama3.2:3b; then
        print_error "Failed to download llama3.2:3b"
        exit 1
    fi
    print_success "  llama3.2:3b downloaded"
    
    print_info "  Downloading nomic-embed-text (274MB)..."
    if ! docker exec k-sphere-ollama ollama pull nomic-embed-text; then
        print_error "Failed to download nomic-embed-text"
        exit 1
    fi
    print_success "  nomic-embed-text downloaded"
    
    print_success "All AI models downloaded"
}

# Function to print final instructions
print_final_instructions() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║   🎉  K-Sphere is now running!                            ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_success "Frontend:  http://localhost:3000"
    print_success "Backend:   http://localhost:8000"
    print_success "Ollama:    http://localhost:11434"
    echo ""
    print_info "Useful commands:"
    echo "  • View logs:      docker compose logs -f"
    echo "  • Stop K-Sphere:  docker compose down"
    echo "  • Restart:        docker compose restart"
    echo "  • Update:         docker compose pull && docker compose up -d"
    echo ""
    print_info "Opening K-Sphere in your browser..."
    
    # Try to open browser
    if command_exists open; then
        open http://localhost:3000  # macOS
    elif command_exists xdg-open; then
        xdg-open http://localhost:3000  # Linux
    elif command_exists start; then
        start http://localhost:3000  # Windows
    fi
}

# Main installation flow
main() {
    print_info "Starting K-Sphere installation..."
    echo ""
    
    # Pre-installation checks
    check_docker
    check_docker_compose
    check_system_resources
    check_ports
    create_directories
    
    echo ""
    print_info "All pre-installation checks passed!"
    echo ""
    
    # Installation
    build_images
    start_services
    wait_for_services
    download_models
    
    # Success!
    print_final_instructions
}

# Error handler
trap 'print_error "Installation failed. Run: docker compose logs for details"' ERR

# Run main installation
main
