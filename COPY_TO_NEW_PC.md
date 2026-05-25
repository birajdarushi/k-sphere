> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# 📦 What to Copy to a New PC - K-Sphere Installation

## 🎯 Quick Answer

### For Windows Users (RECOMMENDED):
Copy these **2 files** to the new PC:
```
✅ install-k-sphere.bat          (Double-click to install!)
✅ install-standalone.ps1        (PowerShell installer)
```

**How to use:**
1. Copy both files to new Windows PC
2. Right-click `install-k-sphere.bat` → "Run as administrator"
3. Wait 5-10 minutes
4. Installation complete. Browser opens automatically

---

### For macOS/Linux Users:
Copy this **1 file** to the new PC:
```
✅ install-standalone.sh         (Double-click or run in terminal)
```

**How to use:**
1. Copy file to new Mac/Linux PC
2. Double-click the file (or run `bash install-standalone.sh`)
3. Wait 5-10 minutes
4. Installation complete. Browser opens automatically

---

## 📂 File Locations

All installer files are in:
```
/Users/rushiraj/Desktop/
```

### Windows Files:
- `install-k-sphere.bat` - Windows batch file (double-click friendly)
- `install-standalone.ps1` - PowerShell installer script

### macOS/Linux Files:
- `install-standalone.sh` - Bash installer script

### Documentation:
- `WINDOWS_INSTALLATION.md` - Complete Windows installation guide
- `DISTRIBUTION_GUIDE.md` - How to distribute K-Sphere
- `INSTALLATION.md` - Complete installation documentation
- `QUICK_REFERENCE.md` - Quick command reference

---

## 🚀 What Happens When User Runs It

### Windows (.bat file):
1. ✅ Checks if Docker is installed and running
2. ✅ Downloads K-Sphere from GitHub
3. ✅ Creates configuration files
4. ✅ Starts all services (backend, frontend, Ollama)
5. ✅ Downloads AI model (llama3.2:1b)
6. ✅ Opens browser to http://localhost:3000
7. ✅ **Installation complete.** User can start using K-Sphere

### macOS/Linux (.sh file):
Same steps as Windows, but uses bash instead of PowerShell.

**Total time:** 5-10 minutes (depending on internet speed)

**User interaction:** Zero! Just click and wait.

---

## 📋 Prerequisites (User Must Have)

### All Platforms:
- ✅ **Docker Desktop** installed and running
  - Download: https://www.docker.com/products/docker-desktop
- ✅ Internet connection (for downloading K-Sphere and AI model)

### Windows Only:
- ✅ Windows 10/11 (64-bit)
- ✅ Administrator privileges

### macOS Only:
- ✅ macOS 10.15+ (Catalina or newer)

### Linux Only:
- ✅ Docker and Docker Compose installed

---

## 🔄 Distribution Methods

### Method 1: Direct Download (Website)
Host the installer files on your website:
```
https://your-site.com/download/
├── install-k-sphere.bat         (for Windows)
├── install-standalone.ps1       (for Windows)
└── install-standalone.sh        (for Mac/Linux)
```

### Method 2: GitHub Releases
Upload to GitHub Releases:
```
https://github.com/your-username/k-sphere/releases/latest/
```

Users download the file for their platform.

### Method 3: Cloud Storage
Upload to Dropbox, Google Drive, OneDrive:
```
Share link → User downloads → Double-click to install
```

### Method 4: USB Drive
Copy installer files to USB drive and distribute physically.

---

## 📝 User Instructions (Give to Non-Technical Users)

### Windows Users:

**Step 1:** Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop
- Wait until it says "Engine running"

**Step 2:** Download K-Sphere Installer
- Download `install-k-sphere.bat` from [your download link]

**Step 3:** Run Installer
- Right-click `install-k-sphere.bat`
- Select "Run as administrator"
- Wait 5-10 minutes

**Step 4:** Start Using K-Sphere
- Browser opens automatically to http://localhost:3000
- Start chatting with your AI assistant!

---

### Mac/Linux Users:

**Step 1:** Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop

**Step 2:** Download K-Sphere Installer
- Download `install-standalone.sh` from [your download link]

**Step 3:** Run Installer
- Double-click `install-standalone.sh`
- Or open Terminal and run: `bash install-standalone.sh`
- Wait 5-10 minutes

**Step 4:** Start Using K-Sphere
- Browser opens automatically to http://localhost:3000
- Start chatting with your AI assistant!

---

## ❓ Where to Run the Installer

### Windows:
**Option 1 (Easiest):** 
- Just double-click `install-k-sphere.bat` (no terminal needed!)

**Option 2:** 
- Right-click in File Explorer → "Open in Terminal"
- Then: `.\install-k-sphere.bat`

**Option 3:** 
- PowerShell (Run as Administrator)
- Then: `.\install-k-sphere.bat`

### Docker Terminal (Not Recommended):
You CAN run it in Docker Desktop's terminal, but it's easier to just double-click the file!

---

## 🎨 Making It Even More User-Friendly

### Create an Icon:
1. Create a shortcut to `install-k-sphere.bat`
2. Right-click shortcut → Properties → Change Icon
3. Add a custom K-Sphere icon
4. Name it "Install K-Sphere"

### Create an Installer Package:
For even better UX, you could create:
- **Windows:** MSI installer using WiX or Inno Setup
- **macOS:** DMG installer with drag-to-Applications
- **Linux:** DEB/RPM packages

But the current .bat/.sh approach is already very simple!

---

## 🔐 Security Notes

### Code Signing:
For production distribution, consider signing your installers:
- **Windows:** Sign the .bat/.ps1 files with a code signing certificate
- **macOS:** Notarize the .sh file with Apple Developer certificate

This prevents security warnings when users run the files.

### Checksums:
Provide SHA256 checksums for verification:
```bash
# Generate checksums
sha256sum install-k-sphere.bat > checksums.txt
sha256sum install-standalone.ps1 >> checksums.txt
sha256sum install-standalone.sh >> checksums.txt
```

Users can verify integrity before running.

---

## ✅ Summary

**What to copy:** 
- Windows: `install-k-sphere.bat` + `install-standalone.ps1`
- Mac/Linux: `install-standalone.sh`

**Where to run:** 
- Windows: Just double-click the .bat file!
- Mac/Linux: Just double-click the .sh file!
- Alternative: Run in any terminal (PowerShell, bash, etc.)

**What it does:** 
- Downloads K-Sphere
- Installs everything
- Opens browser
- Ready to use!

**Time:** 5-10 minutes total

**User effort:** Just double-click and wait!

---

**This is as close to "click and install" as you can get without creating a full GUI installer app!** 🎉
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
