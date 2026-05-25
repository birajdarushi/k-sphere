> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# Docker Testing Guide

## Quick Test Commands

### 1. Test Backend Dockerfile
```bash
cd /Users/rushiraj/Desktop/k-sphere-backend
docker build -t k-sphere-backend:test .
```

### 2. Test Frontend Dockerfile
```bash
cd /Users/rushiraj/Desktop/k-sphere-frontend
docker build -t k-sphere-frontend:test .
```

### 3. Test Full Stack with Docker Compose
```bash
# From k-sphere-backend directory (where docker-compose.yml is)
cd /Users/rushiraj/Desktop/k-sphere-backend
docker-compose up --build
```

### 4. Test in Detached Mode
```bash
docker-compose up -d
docker-compose logs -f  # View logs
```

### 5. Test Services
Once running, test these URLs:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/health
- **Debug Server**: http://localhost:8001/ui
- **Ollama**: http://localhost:11434/api/tags

### 6. Pull Default Models
```bash
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text
```

### 7. Stop Everything
```bash
docker-compose down
```

### 8. Clean Up (Remove Volumes)
```bash
docker-compose down -v
```

## Troubleshooting

### Issue: Ollama not responding
```bash
# Check Ollama logs
docker logs k-sphere-ollama

# Restart Ollama
docker restart k-sphere-ollama
```

### Issue: Backend can't connect to Ollama
```bash
# Verify network
docker network inspect k-sphere-backend_default

# Test connection from backend
docker exec k-sphere-backend curl http://ollama:11434/api/tags
```

### Issue: Frontend can't reach backend
- Check `NEXT_PUBLIC_BACKEND_URL` environment variable
- Should be: `http://localhost:8000` (for browser)
- Backend internal URL: `http://backend:8000` (for server-side)

### Issue: GPU not detected
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# If fails, install NVIDIA Container Toolkit:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

## Production Deployment

### Build for Production
```bash
# Tag images
docker-compose build
docker tag k-sphere-backend:latest k-sphere-backend:v1.0
docker tag k-sphere-frontend:latest k-sphere-frontend:v1.0
```

### Save Images for Transfer
```bash
docker save k-sphere-backend:v1.0 k-sphere-frontend:v1.0 | gzip > k-sphere-v1.0.tar.gz
```

### Load on Another Machine
```bash
docker load < k-sphere-v1.0.tar.gz
```

## Windows GPU Setup

### Prerequisites
1. **Windows 10/11** (Build 19044 or higher)
2. **WSL 2** installed
3. **NVIDIA GPU** with latest drivers
4. **Docker Desktop** with WSL 2 backend

### Enable GPU in Docker Desktop
1. Open Docker Desktop
2. Settings → Resources → WSL Integration
3. Enable integration with WSL distro
4. Settings → Docker Engine
5. Add:
```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

### Test GPU
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Performance Tips

### 1. Use Build Cache
```bash
docker-compose build --parallel
```

### 2. Limit Resources
Edit `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### 3. Persistent Data
All data is stored in:
- `./data/uploads/` - User files
- `./data/vectordb/` - ChromaDB
- `./data/k-sphere.db` - SQLite
- `ollama_data` volume - Ollama models

Back these up regularly!

## Next Steps

Once Docker is working:
1. Test installer scripts (`install.sh` / `install.bat`)
2. Test on different machines
3. Create portable package
4. Add model pulling to Settings UI
5. Enhance debug server visualization

---

**Status**: Docker setup complete! Ready for testing. 🐳
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
