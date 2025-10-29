# 🚀 K-Sphere - Quick Deployment Guide

Deploy K-Sphere AI knowledge base system on any laptop in under 5 minutes!

## 🏃‍♂️ Super Quick Start

### Option 1: One-Command Deploy (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/birajdarushi/k-sphere/main/quick-deploy.sh | bash
```

### Option 2: Manual Deploy
```bash
# Create directory and download config
mkdir k-sphere-deployment && cd k-sphere-deployment
curl -O https://raw.githubusercontent.com/birajdarushi/k-sphere/main/docker-compose.production.yml

# Start the application
docker-compose -f docker-compose.production.yml up -d
```

### Option 3: Clone Repository (For Development)
```bash
git clone https://github.com/birajdarushi/k-sphere.git
cd k-sphere
docker-compose -f docker-compose.production.yml up -d
```

## 📋 Prerequisites

- **Docker Desktop** installed and running
  - [Mac](https://docs.docker.com/desktop/mac/install/)
  - [Windows](https://docs.docker.com/desktop/windows/install/)
  - [Linux](https://docs.docker.com/engine/install/)
- **4GB+ RAM** recommended
- **Internet connection** for downloading images

## 🎯 Access Points

After deployment (takes 2-3 minutes):

- **🌐 Main Application**: http://localhost:3000
- **🔧 API Backend**: http://localhost:8000
- **📚 API Docs**: http://localhost:8000/docs

## 🛠️ Management Commands

```bash
# View logs
docker-compose logs

# Stop application
docker-compose down

# Restart services
docker-compose restart

# Check status
docker-compose ps

# Update to latest version
docker-compose pull && docker-compose up -d
```

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 3GB | 8GB+ |
| Storage | 5GB | 10GB+ |
| CPU | 2 cores | 4+ cores |

## 🔧 Troubleshooting

### Services won't start?
```bash
# Check Docker is running
docker info

# View detailed logs
docker-compose logs

# Restart everything
docker-compose down && docker-compose up -d
```

### Out of memory errors?
The system automatically uses a lightweight AI model (phi3.5) that requires only ~2.5GB RAM.

### Chat not responding?
Wait 2-3 minutes on first startup for AI models to download and initialize.

## 🚀 Features

- **🤖 AI Chat Interface** - Interactive knowledge base queries
- **📄 Document Upload** - PDF, TXT, DOCX support
- **🔍 Smart Search** - Vector-based semantic search
- **💾 Persistent Storage** - Your data is saved between restarts
- **🐳 Containerized** - Runs consistently everywhere

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/birajdarushi/k-sphere/issues)
- **Documentation**: [Full Docs](https://github.com/birajdarushi/k-sphere)

---

**⚡ Ready in under 5 minutes!** Just run the one-command deploy above.