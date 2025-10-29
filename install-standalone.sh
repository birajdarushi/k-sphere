#!/bin/bash

###############################################################################
# K-Sphere Standalone Installer
# 
# This script downloads K-Sphere and runs the installation
# NO GIT REQUIRED!
###############################################################################

set -e

REPO_URL="https://github.com/your-username/k-sphere"
RELEASE_URL="https://github.com/your-username/k-sphere/archive/refs/heads/main.zip"
INSTALL_DIR="$HOME/K-Sphere"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

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
║               Standalone Installer (No Git!)              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_info "This installer will download and set up K-Sphere"
print_info "Installation directory: $INSTALL_DIR"
echo ""

# Check Docker
print_info "Checking Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    print_info "Please download Docker Desktop from:"
    echo "  https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker is not running"
    print_info "Please start Docker Desktop and run this installer again"
    exit 1
fi
print_success "Docker is ready"

# Download K-Sphere
print_info "Downloading K-Sphere..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if command -v curl &> /dev/null; then
    curl -L "$RELEASE_URL" -o k-sphere.zip
elif command -v wget &> /dev/null; then
    wget "$RELEASE_URL" -O k-sphere.zip
else
    print_error "Neither curl nor wget found. Cannot download K-Sphere"
    exit 1
fi

print_success "Downloaded K-Sphere"

# Extract
print_info "Extracting files..."
unzip -q k-sphere.zip
rm k-sphere.zip

# Find extracted directory (GitHub adds repo name)
EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "k-sphere-*" | head -n 1)
if [ -n "$EXTRACTED_DIR" ]; then
    mv "$EXTRACTED_DIR"/* .
    rm -rf "$EXTRACTED_DIR"
fi

print_success "Files extracted"

# Make install script executable
chmod +x install.sh

# Run main installer
print_info "Starting K-Sphere installation..."
echo ""
./install.sh

print_success "K-Sphere is installed at: $INSTALL_DIR"
print_info "To start K-Sphere later, run: cd $INSTALL_DIR && docker compose up -d"
