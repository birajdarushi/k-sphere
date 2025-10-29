# 🚚 Transfer K-Sphere from Mac to Windows

## Quick Transfer Options

### Option 1: USB Drive / External Storage (Fastest)

**On Mac:**
```bash
cd /Users/rushiraj/Desktop

# Create compressed archive (includes both backend and frontend)
tar -czf k-sphere-complete.tar.gz k-sphere-backend k-sphere-frontend

# Copy k-sphere-complete.tar.gz to USB drive
cp k-sphere-complete.tar.gz /Volumes/YOUR_USB_NAME/
```

**On Windows:**
```powershell
# Copy from USB to C:\Projects (or any location)
Copy-Item E:\k-sphere-complete.tar.gz -Destination C:\Projects\

# Extract (Windows 10/11 has native tar support)
cd C:\Projects
tar -xzf k-sphere-complete.tar.gz

# Or use 7-Zip/WinRAR if tar doesn't work
```

---

### Option 2: Cloud Storage (Google Drive, OneDrive, Dropbox)

**On Mac:**
```bash
cd /Users/rushiraj/Desktop

# Create archive
tar -czf k-sphere-complete.tar.gz k-sphere-backend k-sphere-frontend

# Upload to Google Drive / OneDrive / Dropbox
# (Use their desktop app or web interface)
```

**On Windows:**
```powershell
# Download from cloud
# Extract to desired location
cd C:\Projects
tar -xzf k-sphere-complete.tar.gz
```

---

### Option 3: GitHub (Best for version control)

**On Mac:**
```bash
cd /Users/rushiraj/Desktop/k-sphere-backend

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial K-Sphere setup with Docker"

# Create GitHub repo at: https://github.com/new
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/k-sphere.git
git branch -M main
git push -u origin main

# Do the same for frontend
cd /Users/rushiraj/Desktop/k-sphere-frontend
git init
git add .
git commit -m "Initial frontend setup"
git remote add origin https://github.com/YOUR_USERNAME/k-sphere-frontend.git
git branch -M main
git push -u origin main
```

**On Windows:**
```powershell
# Install Git: https://git-scm.com/download/win

# Clone backend
cd C:\Projects
git clone https://github.com/YOUR_USERNAME/k-sphere.git k-sphere-backend

# Clone frontend
git clone https://github.com/YOUR_USERNAME/k-sphere-frontend.git k-sphere-frontend
```

---

### Option 4: Network Share / AirDrop

**On Mac:**
```bash
# Use AirDrop to Windows (if both have Wi-Fi)
# Or use network file sharing

cd /Users/rushiraj/Desktop
tar -czf k-sphere-complete.tar.gz k-sphere-backend k-sphere-frontend

# Share via your local network
```

---

## What Gets Transferred

### ✅ Included (Code & Config)
- All source code (backend + frontend)
- Docker configuration (Dockerfile, docker-compose.yml)
- Install scripts (install.sh, install.bat)
- Documentation (all .md files)
- Requirements files (requirements.txt, package.json)

### ❌ NOT Included (Data - Intentionally)
- User uploads (`data/uploads/`)
- Vector database (`data/vectordb/`)
- SQLite database (`data/k-sphere.db`)
- Ollama models (will be downloaded fresh)
- Python venv (will be recreated by Docker)
- node_modules (will be installed by Docker)

This keeps the transfer size small (< 50 MB vs multiple GB)!

---

## After Transfer - Windows Setup

### 1. Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop

### 2. Start K-Sphere
```powershell
cd C:\Projects\k-sphere-backend
.\install.bat
```

### 3. Wait for Setup
- Docker will download base images (~2-3 GB)
- Ollama models will be pulled (~2-3 GB)
- Total: ~5-6 GB download on Windows

### 4. Access
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Debug Server: http://localhost:8001/ui

---

## File Size Estimates

| Item | Size |
|------|------|
| K-Sphere Code (compressed) | ~10-20 MB |
| Docker Base Images | ~2-3 GB |
| Ollama Models (llama3.2:3b + nomic-embed-text) | ~2-3 GB |
| **Total fresh install on Windows** | **~5-6 GB** |

---

## Recommended Transfer Method

**For your case (storage issues on Mac):**

1. ✅ **USB Drive** - Fast, no internet needed
2. ✅ **GitHub** - Best for updates later, version control
3. ⚠️ Cloud - Slower upload/download
4. ⚠️ Network - Only if both machines on same network

---

## Quick Commands Summary

**Mac (Prepare):**
```bash
cd /Users/rushiraj/Desktop
tar -czf k-sphere-complete.tar.gz k-sphere-backend k-sphere-frontend
# Copy to USB or upload to cloud
```

**Windows (Setup):**
```powershell
# Extract archive
cd C:\Projects
tar -xzf k-sphere-complete.tar.gz

# Install Docker Desktop first!

# Run K-Sphere
cd k-sphere-backend
.\install.bat
```

---

## GPU Support on Windows

If your Windows PC has NVIDIA GPU:
1. Install NVIDIA drivers: https://www.nvidia.com/Download/index.aspx
2. Follow GPU setup in `WINDOWS_SETUP.md`
3. K-Sphere will automatically use GPU if available

---

## Need Help?

See `WINDOWS_SETUP.md` for detailed Windows installation guide!

🚀 **Total time on Windows: ~15-20 minutes** (including downloads)
