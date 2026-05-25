> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# K-Sphere Installation Guide for Windows

## 🎯 One-Click Installation

### Prerequisites
1. **Docker Desktop** (required)
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop
   - Wait until Docker Desktop shows "Engine running"

### Installation Steps

#### Method 1: Double-Click Install (Easiest)

1. **Download** `install-k-sphere.bat` from:
   - Your website: `https://your-site.com/download/install-k-sphere.bat`
   - GitHub Releases: `https://github.com/you/k-sphere/releases/latest`

2. **Right-click** `install-k-sphere.bat` → **"Run as administrator"**

3. **Wait** for installation to complete (5-10 minutes on first run)

4. **Installation complete.** Browser opens automatically to http://localhost:3000

#### Method 2: PowerShell Install

1. **Download both files:**
   - `install-standalone.ps1`
   - `install-k-sphere.bat`

2. **Right-click** `install-k-sphere.bat` → **"Run as administrator"**

3. **Wait** for installation

4. **Installation complete.**

#### Method 3: Manual PowerShell (for advanced users)

1. **Download** `install-standalone.ps1`

2. **Open PowerShell as Administrator**
   - Press `Win + X` → Select "Windows PowerShell (Admin)"

3. **Navigate to download folder:**
   ```powershell
   cd Downloads
   ```

4. **Run installer:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install-standalone.ps1
   ```

5. **Wait** for installation

6. **Installation complete.**

---

## 📁 Files to Copy to New PC

For a fresh Windows installation, copy these files:

### Minimal Installation (Recommended)
```
install-k-sphere.bat          ← Double-click this!
install-standalone.ps1        ← PowerShell installer
```

### Offline Installation (if you have slow internet)
```
k-sphere-complete.zip         ← Full project archive
install-k-sphere.bat          ← Double-click installer
```

---

## 🚀 Using K-Sphere

### Starting K-Sphere
If you closed K-Sphere, restart it:

```powershell
cd %USERPROFILE%\k-sphere
docker-compose start
```

### Stopping K-Sphere
```powershell
cd %USERPROFILE%\k-sphere
docker-compose stop
```

### Accessing K-Sphere
Open your browser at **http://localhost:3000**.

### View Logs
```powershell
cd %USERPROFILE%\k-sphere
docker-compose logs -f
```

### Uninstall K-Sphere
```powershell
cd %USERPROFILE%\k-sphere
docker-compose down -v
cd ..
rmdir /s k-sphere
```

---

## 🆘 Troubleshooting

### Docker Desktop Not Running
**Error:** "Docker is installed but not running"

**Solution:**
1. Open Docker Desktop from Start Menu
2. Wait for "Engine running" message
3. Run installer again

### Port Already in Use
**Error:** "Port 3000 is already allocated"

**Solution:**
1. Check what's using the port:
   ```powershell
   netstat -ano | findstr :3000
   ```
2. Stop the conflicting service or change K-Sphere port in `docker-compose.yml`

### Installation Directory Already Exists
**Error:** "Directory already exists"

**Solution:**
The installer will clean up automatically. If it fails:
```powershell
rmdir /s %USERPROFILE%\k-sphere
```
Then run installer again.

### PowerShell Execution Policy Error
**Error:** "Cannot be loaded because running scripts is disabled"

**Solution:**
Run PowerShell as Administrator and enable scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Download Failed
**Error:** "Failed to download K-Sphere"

**Solution:**
1. Check internet connection
2. If behind a firewall, ask IT to allow access to GitHub
3. Alternative: Use offline installation with ZIP file

---

## 💡 Tips for Windows Users

### Windows Defender
Windows Defender may scan downloaded files. This is normal and safe.

### Firewall
First time running Docker, Windows Firewall will ask for permission. Click "Allow".

### WSL2 (Windows Subsystem for Linux)
Docker Desktop uses WSL2. If prompted to install WSL2, allow it.

### Performance
- Docker Desktop works best with at least 8GB RAM
- Allocate 4GB RAM to Docker in Docker Desktop settings
- Use SSD storage for better performance

### Updates
To update K-Sphere:
1. Stop services: `docker-compose down`
2. Run installer again (it will download latest version)
3. Start services: `docker-compose up -d`

---

## 📋 System Requirements

- **OS:** Windows 10/11 (64-bit)
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 10GB free space
- **Docker Desktop:** Latest version
- **Internet:** Required for initial setup

---

## 🎓 Additional Resources

- **Full Documentation:** See `INSTALLATION.md`
- **Quick Reference:** See `QUICK_REFERENCE.md`
- **Troubleshooting:** See `README.md`
- **Support:** Open an issue on GitHub

---

## 🔒 Security Notes

### Administrator Privileges
The installer needs admin rights to:
- Install Docker Desktop (if not present)
- Create directories
- Configure Windows Firewall

### Data Storage
K-Sphere stores data in:
- `%USERPROFILE%\k-sphere\k-sphere-backend\data\`

This includes:
- Uploaded files
- Vector database
- Settings

**Backup this folder** to preserve your data!

---

## ✅ Post-Installation Checklist

After installation completes:

- [ ] Browser opens to http://localhost:3000
- [ ] K-Sphere login page appears
- [ ] Docker Desktop shows 3 running containers
- [ ] Can upload and index files
- [ ] Can chat with AI

If any step fails, see **Troubleshooting** section above.

---

**Need Help?** Open an issue on GitHub or contact support!
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
