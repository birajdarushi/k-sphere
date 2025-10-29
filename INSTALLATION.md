# K-Sphere One-Click Installation Guide

## 🚀 Quick Start (One Command!)

```bash
./install.sh
```

That's it! The script will:
1. ✓ Check system requirements
2. ✓ Build Docker images
3. ✓ Start all services
4. ✓ Download AI models
5. ✓ Open K-Sphere in your browser

**Installation Time**: 15-30 minutes (mostly downloading AI models)

---

## 📋 Prerequisites

### Required
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
- **10GB+ free disk space** - For AI models and data
- **8GB+ RAM** - Recommended for smooth operation

### Operating Systems
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)
- ✅ Windows (with WSL2)

---

## 🎯 Installation Methods

### Method 1: One-Click Install (Recommended)

1. **Download K-Sphere**
   ```bash
   git clone https://github.com/your-repo/k-sphere.git
   cd k-sphere
   ```

2. **Run Installer**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Wait for completion** (~15-30 minutes)
   - Building images: 5-10 minutes
   - Downloading models: 10-20 minutes

4. **Access K-Sphere**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Ollama: http://localhost:11434

### Method 2: Manual Docker Compose

If you prefer manual control:

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Download AI models
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Method 3: Development Setup

For development with hot reload:

```bash
# Backend
cd k-sphere-backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend (in new terminal)
cd k-sphere-frontend
pnpm install
pnpm dev

# Ollama (in new terminal)
ollama serve
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

---

## 🐳 Docker Architecture

```
┌─────────────────────────────────────────────┐
│                                             │
│  Frontend (Next.js)                         │
│  Port: 3000                                 │
│  Container: k-sphere-frontend               │
│                                             │
└─────────────┬───────────────────────────────┘
              │
              │ HTTP Requests
              ▼
┌─────────────────────────────────────────────┐
│                                             │
│  Backend (FastAPI)                          │
│  Port: 8000                                 │
│  Container: k-sphere-backend                │
│  Volumes: data/, logs/                      │
│                                             │
└─────────────┬───────────────────────────────┘
              │
              │ AI Requests
              ▼
┌─────────────────────────────────────────────┐
│                                             │
│  Ollama (AI Models)                         │
│  Port: 11434                                │
│  Container: k-sphere-ollama                 │
│  Volume: ollama_data (~5GB)                 │
│                                             │
└─────────────────────────────────────────────┘
```

### Services

| Service | Container Name | Port | Purpose |
|---------|---------------|------|---------|
| Frontend | k-sphere-frontend | 3000 | Web UI (Next.js) |
| Backend | k-sphere-backend | 8000 | REST API (FastAPI) |
| Ollama | k-sphere-ollama | 11434 | AI Model Server |

### Volumes

| Volume | Purpose | Size |
|--------|---------|------|
| ollama_data | AI model storage | ~5GB |
| backend_data | Vector DB & uploads | Grows with usage |
| backend_logs | Application logs | ~100MB |

---

## 🎮 Managing K-Sphere

### Common Commands

```bash
# Start K-Sphere
docker compose up -d

# Stop K-Sphere
docker compose down

# Restart services
docker compose restart

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f ollama

# Check status
docker compose ps

# Update K-Sphere
git pull
docker compose build
docker compose up -d
```

### System Indexer

Enable system-wide file indexing:

1. Go to **System Indexer** page
2. Click **"Add Path"**
3. Select folders to index
4. Click **"Start Indexing"**

Files will be processed and added to your knowledge base automatically!

### Cleanup

Remove all data and start fresh:

```bash
# Stop services
docker compose down

# Remove volumes (WARNING: deletes all data!)
docker volume rm $(docker volume ls -q | grep k-sphere)

# Restart fresh
./install.sh
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in root:

```bash
# Backend Configuration
OLLAMA_HOST=http://ollama:11434
LLM_MODEL=llama3.2:3b
EMBEDDING_MODEL=nomic-embed-text

# Frontend Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Optional: GPU Support (NVIDIA only)
# Uncomment in docker-compose.yml:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: all
#           capabilities: [gpu]
```

### Change AI Models

```bash
# List available models
docker exec k-sphere-ollama ollama list

# Pull different model
docker exec k-sphere-ollama ollama pull mistral

# Update backend environment
# In docker-compose.yml, change:
# LLM_MODEL=mistral

# Restart backend
docker compose restart backend
```

### Port Configuration

Change ports in `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "8080:3000"  # Access at http://localhost:8080
  
  backend:
    ports:
      - "5000:8000"  # Access at http://localhost:5000
```

---

## 🐛 Troubleshooting

### Issue: "Docker is not running"

**Solution:**
1. Open Docker Desktop
2. Wait for Docker icon in system tray
3. Run `docker info` to verify
4. Try installation again

### Issue: "Port already in use"

**Solution:**
```bash
# Find process using port
lsof -i :3000  # or :8000, :11434

# Kill process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Issue: "Build failed" / "Container won't start"

**Solution:**
```bash
# View detailed logs
docker compose logs

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Issue: "Models not downloading"

**Solution:**
```bash
# Check Ollama logs
docker compose logs ollama

# Manually pull models
docker exec -it k-sphere-ollama bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
exit
```

### Issue: "Frontend shows connection error"

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check backend logs: `docker compose logs backend`
3. Restart backend: `docker compose restart backend`

### Issue: "Out of disk space"

**Solution:**
```bash
# Check Docker disk usage
docker system df

# Clean up unused images
docker system prune -a

# Remove old volumes
docker volume prune
```

---

## 🚀 Performance Optimization

### For MacBook/Laptops

1. **Resource Limits** (Docker Desktop → Settings → Resources):
   - CPU: 4-6 cores
   - Memory: 6-8 GB
   - Disk: 50 GB+

2. **Disable File Sync** for better performance:
   ```yaml
   # In docker-compose.yml, remove volume mounts during development
   ```

### For GPU Acceleration (Linux + NVIDIA)

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. Uncomment GPU section in `docker-compose.yml`:
   ```yaml
   ollama:
     deploy:
       resources:
         reservations:
           devices:
             - driver: nvidia
               count: all
               capabilities: [gpu]
   ```

3. Restart: `docker compose up -d`

---

## 📊 System Requirements

### Minimum
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 10 GB free
- **OS**: macOS 10.15+, Ubuntu 20.04+, Windows 10+

### Recommended
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 50+ GB free
- **OS**: Latest stable version

### Optimal (for heavy usage)
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 100+ GB SSD
- **GPU**: NVIDIA RTX series (optional)

---

## 🎓 Next Steps

After installation:

1. **Upload Documents**
   - Go to Knowledge Base
   - Drag & drop PDFs, images, audio files

2. **Enable System Indexer**
   - Go to System Indexer
   - Add folders to index
   - Start indexing

3. **Start Chatting**
   - Go to Chat
   - Ask questions about your documents
   - Get AI-powered answers with citations!

---

## 📚 Additional Resources

- **Documentation**: See `FOLDER_GROUPING.md` for folder features
- **API Docs**: http://localhost:8000/docs (when running)
- **GitHub Issues**: Report bugs and request features
- **Discord/Community**: Join our community for support

---

## 🔐 Security Notes

- K-Sphere runs **100% locally** - no data leaves your machine
- All processing happens on your hardware
- No API keys or external services required
- Perfect for sensitive/confidential documents

---

## 📝 License

[Your License Here]

---

## 🤝 Contributing

We welcome contributions! See `CONTRIBUTING.md` for guidelines.

---

**Need help?** Open an issue on GitHub or join our community chat!
