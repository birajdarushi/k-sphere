> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# K-Sphere Docker - Quick Reference

## 🚀 One Command Start

```bash
# Mac/Linux
cd k-sphere-backend && ./install.sh

# Windows
cd k-sphere-backend
install.bat
```

## 📦 What Gets Installed

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Main UI (Chat, Knowledge Base, Settings) |
| Backend | 8000 | API Server |
| Debug Server | 8001 | Vector DB Visualization |
| Ollama | 11434 | AI Models |

## 🎯 Access Points

- **App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Debug UI**: http://localhost:8001/ui
- **Health Check**: http://localhost:8000/health

## 🔧 Common Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f ollama

# Rebuild after code changes
docker-compose up -d --build

# Check status
docker-compose ps
```

## 🤖 Ollama Commands

```bash
# List models
docker exec k-sphere-ollama ollama list

# Pull a model
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull mistral
docker exec k-sphere-ollama ollama pull nomic-embed-text

# Remove a model
docker exec k-sphere-ollama ollama rm modelname

# Check model info
docker exec k-sphere-ollama ollama show llama3.2:3b
```

## 🐛 Debug Commands

```bash
# Enter backend container
docker exec -it k-sphere-backend bash

# Enter frontend container
docker exec -it k-sphere-frontend sh

# Check backend health
curl http://localhost:8000/health

# Test Ollama connection
curl http://localhost:11434/api/tags

# Check Vector DB
curl http://localhost:8001/stats
```

## 📊 Data Locations

All data persists in:
```
k-sphere-backend/data/
├── uploads/          # User uploaded files
├── vectordb/         # ChromaDB embeddings
├── k-sphere.db       # SQLite database
└── settings.json     # Configuration
```

## 🔄 Backup & Restore

### Backup
```bash
# Stop containers
docker-compose down

# Backup data
tar -czf k-sphere-backup-$(date +%Y%m%d).tar.gz data/

# Backup models (optional, large!)
docker run --rm -v k-sphere-backend_ollama_data:/data -v $(pwd):/backup alpine tar -czf /backup/ollama-models.tar.gz /data
```

### Restore
```bash
# Extract data
tar -xzf k-sphere-backup-20251006.tar.gz

# Restore models
docker run --rm -v k-sphere-backend_ollama_data:/data -v $(pwd):/backup alpine tar -xzf /backup/ollama-models.tar.gz -C /
```

## 🎮 GPU Usage (NVIDIA)

### Check GPU availability
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

### Monitor GPU usage
```bash
# On host
nvidia-smi -l 1

# In Ollama container
docker exec k-sphere-ollama nvidia-smi
```

## 🔐 Environment Variables

Create `.env` file in `k-sphere-backend/`:

```env
# Ollama
OLLAMA_HOST=http://ollama:11434

# Backend
BACKEND_PORT=8000
DEBUG_PORT=8001

# Frontend
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Optional: Custom models
OLLAMA_LLM_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

## 🚨 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Check if ports are in use
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :8001  # Debug
lsof -i :11434 # Ollama
```

### Ollama not responding
```bash
# Restart Ollama
docker restart k-sphere-ollama

# Check logs
docker logs k-sphere-ollama

# Test manually
curl http://localhost:11434/api/tags
```

### Out of disk space
```bash
# Clean unused Docker resources
docker system prune -a

# Remove old volumes
docker volume prune
```

### Network issues
```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

## 📝 Updates

### Update K-Sphere
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Update base images
```bash
docker-compose pull
docker-compose up -d --build
```

## 🎯 Performance Tuning

### Limit memory
Edit `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
```

### Use faster storage
Mount data to SSD:
```yaml
volumes:
  - /path/to/fast/ssd/data:/app/data
```

## 🔄 Portability

### Save for USB/Transfer
```bash
# Save images
docker save k-sphere-backend k-sphere-frontend ollama/ollama | gzip > k-sphere-portable.tar.gz

# Copy entire folder
cp -r k-sphere-backend /path/to/usb/
```

### Load on new machine
```bash
# Load images
docker load < k-sphere-portable.tar.gz

# Start
cd k-sphere-backend
docker-compose up -d
```

---

**Quick Start**: `./install.sh` → http://localhost:3000 🚀
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
