# 🚀 K-Sphere Docker Deployment Guide

## Overview

K-Sphere is now fully containerized and portable! Run it on any machine with Docker - Mac, Windows, or Linux. All your data persists, and you can even copy the entire folder to a USB drive and run it anywhere.

## 🎯 Quick Start

### Prerequisites
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **4GB RAM minimum** (8GB recommended)
- **5GB disk space** for images and models
- **Optional**: NVIDIA GPU with drivers for accelerated inference

### One-Command Installation

#### **Mac/Linux**
```bash
chmod +x install.sh
./install.sh
```

#### **Windows**
```batch
install.bat
```

That's it! The script will:
1. ✅ Check/install Docker and Docker Compose
2. ✅ Create data directories for persistence
3. ✅ Detect GPU and configure if available
4. ✅ Build and start all containers
5. ✅ Pull default AI models (Llama 3.2 & nomic-embed-text)
6. ✅ Open K-Sphere in your browser

## 📍 Access Points

After installation, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:3000 | Full K-Sphere UI |
| **Backend API** | http://localhost:8000 | FastAPI server |
| **API Docs** | http://localhost:8000/docs | Swagger documentation |
| **Vector DB Visualization** | http://localhost:8001/ui | Debug/explore vector database |
| **Ollama API** | http://localhost:11434 | AI model server |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   K-Sphere Stack                     │
├─────────────────────────────────────────────────────┤
│  Frontend (Next.js)        → Port 3000              │
│  Backend API (FastAPI)     → Port 8000              │
│  Vector DB Viz Server      → Port 8001              │
│  Ollama (AI Models)        → Port 11434             │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│              Persistent Storage                      │
├─────────────────────────────────────────────────────┤
│  ./data/uploads/          → Uploaded files          │
│  ./data/vectordb/         → ChromaDB embeddings     │
│  ./data/k-sphere.db       → SQLite database         │
│  ./data/settings.json     → Configuration           │
│  ollama_data volume       → AI models               │
└─────────────────────────────────────────────────────┘
```

## 🔧 Management Commands

### Start K-Sphere
```bash
docker compose up -d
```

### Stop K-Sphere
```bash
docker compose down
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f ollama
```

### Check Status
```bash
docker ps
```

### Restart Services
```bash
docker compose restart
```

### Update K-Sphere
```bash
git pull
docker compose build
docker compose up -d
```

## 🎮 GPU Support (NVIDIA)

### Windows with NVIDIA GPU

1. **Install NVIDIA Drivers**
   - Download from: https://www.nvidia.com/download/index.aspx

2. **Enable WSL2 in Docker Desktop**
   - Settings → General → Use WSL2 based engine

3. **Install NVIDIA Container Toolkit in WSL2**
   ```bash
   wsl
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

4. **Enable GPU in docker-compose.yml**
   - Uncomment the GPU sections in `docker-compose.yml`
   - Or run `install.bat` which will prompt you

5. **Verify GPU Access**
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```

### Linux with NVIDIA GPU

The `install.sh` script automatically detects and configures GPU support on Linux.

## 💾 Portable Deployment

### Copy to USB/External Drive

1. **Stop K-Sphere**
   ```bash
   docker compose down
   ```

2. **Export Docker images**
   ```bash
   docker save -o k-sphere-images.tar \
     k-sphere-backend \
     k-sphere-frontend \
     ollama/ollama:latest
   ```

3. **Copy these files to USB**
   - `docker-compose.yml`
   - `k-sphere-backend/` folder
   - `k-sphere-frontend/` folder
   - `data/` folder (your persistent data)
   - `k-sphere-images.tar`
   - `install.sh` / `install.bat`

4. **On new machine**
   ```bash
   # Load images
   docker load -i k-sphere-images.tar
   
   # Start K-Sphere
   docker compose up -d
   ```

### Cloud Deployment (AWS/Azure/GCP)

1. **Push images to registry**
   ```bash
   docker tag k-sphere-backend your-registry/k-sphere-backend:latest
   docker tag k-sphere-frontend your-registry/k-sphere-frontend:latest
   docker push your-registry/k-sphere-backend:latest
   docker push your-registry/k-sphere-frontend:latest
   ```

2. **Update docker-compose.yml** to use registry images

3. **Deploy** using your cloud provider's container service

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Common issues:
# - Port 8000 already in use
# - Ollama not ready (wait 30s and restart)
```

### Frontend won't start
```bash
# Check logs
docker compose logs frontend

# Common issues:
# - Port 3000 already in use
# - Backend not accessible (check NEXT_PUBLIC_BACKEND_URL)
```

### Ollama models not loading
```bash
# Pull models manually
docker exec -it k-sphere-ollama ollama pull llama3.2:3b
docker exec -it k-sphere-ollama ollama pull nomic-embed-text

# List available models
docker exec -it k-sphere-ollama ollama list
```

### Permission errors (Linux)
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER ./data
```

### GPU not detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Verify docker-compose.yml has GPU config uncommented
```

## 🔒 Security Notes

- **Default ports**: Change ports in `docker-compose.yml` if needed
- **Production deployment**: 
  - Use environment variables for secrets
  - Set up reverse proxy (nginx/traefik)
  - Enable HTTPS
  - Restrict network access

## 📦 What Gets Persisted?

| Data | Location | Description |
|------|----------|-------------|
| Uploaded files | `./data/uploads/` | PDFs, images, audio files |
| Vector embeddings | `./data/vectordb/` | ChromaDB data |
| Chat history | `./data/k-sphere.db` | SQLite database |
| Settings | `./data/settings.json` | Model configs |
| AI models | `ollama_data` volume | Downloaded Ollama models |

## 🚀 Performance Tips

### CPU Mode
- Use smaller models: `llama3.2:1b` instead of `llama3.2:3b`
- Reduce chunk size in settings
- Limit concurrent requests

### GPU Mode
- Use larger models for better quality
- Enable GPU in docker-compose.yml
- Monitor GPU usage: `nvidia-smi -l 1`

### Storage
- Clean old uploads regularly
- Use `.gitignore` for `data/` folder
- Backup `data/` folder periodically

## 📚 Additional Resources

- [Ollama Models](https://ollama.com/library) - Browse available AI models
- [ChromaDB Docs](https://docs.trychroma.com/) - Vector database documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Backend API framework
- [Next.js Docs](https://nextjs.org/docs) - Frontend framework

## 🤝 Support

If you encounter issues:
1. Check logs: `docker compose logs -f`
2. Verify all containers are running: `docker ps`
3. Check resource usage: `docker stats`
4. Review this troubleshooting guide

## 🎉 Success!

Once everything is running, you should see:
- ✅ Main app at http://localhost:3000
- ✅ Backend API at http://localhost:8000
- ✅ Vector DB visualization at http://localhost:8001/ui

Enjoy your portable AI knowledge management system! 🚀
