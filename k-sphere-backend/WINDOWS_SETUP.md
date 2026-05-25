> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# Windows Deployment Guide for K-Sphere

## Prerequisites

1. **Windows 10/11** (Build 19044 or higher)
2. **Windows Subsystem for Linux (WSL 2)**
3. **Docker Desktop for Windows**
4. **NVIDIA GPU + Latest Drivers** (optional, for GPU support)

---

## Step 1: Install Docker Desktop

1. Download from: https://www.docker.com/products/docker-desktop
2. Run installer
3. During installation, ensure **"Use WSL 2 instead of Hyper-V"** is checked
4. Restart computer after installation

---

## Step 2: Enable WSL 2

Open **PowerShell as Administrator** and run:

```powershell
# Enable WSL
wsl --install

# Set WSL 2 as default
wsl --set-default-version 2

# Install Ubuntu (recommended)
wsl --install -d Ubuntu

# Restart computer
```

---

## Step 3: Transfer K-Sphere Files

### Option A: From USB Drive
1. Copy `k-sphere-complete.tar.gz` to Windows
2. Extract using 7-Zip or WinRAR
3. Or use PowerShell:
```powershell
tar -xzf k-sphere-complete.tar.gz
```

### Option B: From GitHub
```powershell
# Install Git for Windows if needed
git clone https://github.com/YOUR_USERNAME/k-sphere.git
cd k-sphere
```

### Option C: From Cloud
1. Download from Google Drive/OneDrive
2. Extract to `C:\Projects\k-sphere` (or any location)

---

## Step 4: Start K-Sphere

### Using Installer (Recommended)
```powershell
# Open PowerShell in k-sphere-backend folder
cd k-sphere-backend
.\install.bat
```

### Using Docker Compose Manually
```powershell
cd k-sphere-backend
docker-compose up -d
```

---

## Step 5: Pull AI Models

```powershell
# Wait for Ollama to start (check with: docker ps)
Start-Sleep -Seconds 30

# Pull default models
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text
```

---

## Step 6: Access K-Sphere

Open browser and go to:
- **Main App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Debug Server**: http://localhost:8001/ui

---

## GPU Setup (NVIDIA)

### 1. Install NVIDIA Container Toolkit in WSL

```powershell
# Open WSL Ubuntu
wsl

# Inside WSL, run:
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Enable GPU in Docker Desktop

1. Open Docker Desktop
2. Go to **Settings** → **Resources** → **WSL Integration**
3. Enable integration with your WSL distro (Ubuntu)
4. Go to **Settings** → **Docker Engine**
5. Add this configuration:

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

6. Click **Apply & Restart**

### 3. Test GPU

```powershell
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

If you see your GPU info, it's working! 🎉

---

## Troubleshooting

### Docker Desktop won't start
- Ensure Virtualization is enabled in BIOS
- Check Windows Features: Hyper-V and Windows Subsystem for Linux must be enabled
- Run: `wsl --update`

### Port already in use
```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID <process_id> /F
```

### Ollama not responding
```powershell
# Check logs
docker logs k-sphere-ollama

# Restart container
docker restart k-sphere-ollama
```

### Out of disk space
```powershell
# Clean Docker
docker system prune -a

# Increase WSL disk size (if needed)
# Edit: %UserProfile%\.wslconfig
[wsl2]
memory=8GB
processors=4
swap=4GB
```

### Can't access from browser
- Check Windows Firewall - allow ports 3000, 8000, 8001
- Try: http://127.0.0.1:3000 instead of localhost

---

## Common Commands (PowerShell)

```powershell
# Start K-Sphere
docker-compose up -d

# Stop K-Sphere
docker-compose down

# View logs
docker-compose logs -f

# Restart everything
docker-compose restart

# Check status
docker-compose ps

# Pull a new model
docker exec k-sphere-ollama ollama pull mistral

# List models
docker exec k-sphere-ollama ollama list

# Enter backend container
docker exec -it k-sphere-backend bash
```

---

## Performance Tips for Windows

1. **Move Docker data to faster drive**
   - Docker Desktop → Settings → Resources → Advanced
   - Change "Disk image location" to SSD

2. **Allocate more resources**
   - Docker Desktop → Settings → Resources → Advanced
   - Increase CPU, Memory, and Disk

3. **Use WSL 2 backend** (faster than Hyper-V)
   - Already default in new installations

4. **Disable unnecessary startup services**
   - Docker Desktop → Settings → General
   - Uncheck "Start Docker Desktop when you log in" (if not needed)

---

## Backup Your Data

Your data is stored in:
```
k-sphere-backend\data\
├── uploads\        # User files
├── vectordb\       # ChromaDB
├── k-sphere.db     # Database
└── settings.json   # Config
```

**Backup command:**
```powershell
# Compress data folder
Compress-Archive -Path .\data -DestinationPath "k-sphere-backup-$(Get-Date -Format 'yyyy-MM-dd').zip"
```

---

## Uninstall

```powershell
# Stop and remove containers
docker-compose down -v

# Remove images
docker rmi k-sphere-backend k-sphere-frontend ollama/ollama

# Clean everything
docker system prune -a --volumes
```

---

## Next Steps

Once running on Windows:
1. Test all features (chat, knowledge base, voice, file upload)
2. Upload documents and test RAG
3. Try different Ollama models
4. Check debug server at http://localhost:8001/ui
5. Configure GPU if available

---

**Need help?** Check the logs:
```powershell
docker-compose logs -f
```

**Ready to start?** Run:
```powershell
.\install.bat
```

🚀 **K-Sphere will be available at: http://localhost:3000**
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
