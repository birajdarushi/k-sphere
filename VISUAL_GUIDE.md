# 🎯 K-Sphere Installation - Quick Visual Guide

## For Windows Users 🪟

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Download These Files                               │
│  ─────────────────────────────                              │
│                                                              │
│  📄 install-k-sphere.bat          ⬅️ Double-click this!     │
│  📄 install-standalone.ps1        ⬅️ Supporting script      │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Step 2: Right-Click & Run                                  │
│  ─────────────────────────                                  │
│                                                              │
│  📄 install-k-sphere.bat                                    │
│        👆 Right-click                                        │
│        └─> "Run as administrator"  ✅                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Step 3: Wait for Magic ✨                                  │
│  ─────────────────────────                                  │
│                                                              │
│  ⏳ Downloading K-Sphere...                                 │
│  ⏳ Setting up Docker containers...                         │
│  ⏳ Downloading AI model...                                 │
│  ⏳ Starting services...                                    │
│                                                              │
│  ⏱️  Total time: 5-10 minutes                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Step 4: Browser Opens Automatically! 🎉                    │
│  ────────────────────────────────────                       │
│                                                              │
│  🌐 http://localhost:3000                                   │
│                                                              │
│  ✅ K-Sphere is ready to use!                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## For Mac/Linux Users 🍎🐧

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Download This File                                 │
│  ──────────────────────────                                 │
│                                                              │
│  📄 install-standalone.sh         ⬅️ Double-click this!     │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Step 2: Double-Click or Run in Terminal                    │
│  ────────────────────────────────────────                   │
│                                                              │
│  Option A: Double-click the file                            │
│  Option B: bash install-standalone.sh                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Step 3: Wait for Magic ✨                                  │
│  ─────────────────────────                                  │
│                                                              │
│  ⏳ Downloading K-Sphere...                                 │
│  ⏳ Setting up Docker containers...                         │
│  ⏳ Downloading AI model...                                 │
│  ⏳ Starting services...                                    │
│                                                              │
│  ⏱️  Total time: 5-10 minutes                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Step 4: Browser Opens Automatically! 🎉                    │
│  ────────────────────────────────────                       │
│                                                              │
│  🌐 http://localhost:3000                                   │
│                                                              │
│  ✅ K-Sphere is ready to use!                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 What Gets Installed

```
Your Computer
└── C:\Users\YourName\k-sphere\  (or ~/k-sphere on Mac/Linux)
    ├── k-sphere-backend/         ⬅️ AI Backend
    │   ├── data/                 ⬅️ Your uploaded files
    │   ├── vectordb/             ⬅️ AI knowledge base
    │   └── logs/                 ⬅️ System logs
    │
    ├── k-sphere-frontend/        ⬅️ Web Interface
    │
    └── docker-compose.yml        ⬅️ Configuration
```

---

## 🎮 Using K-Sphere After Installation

```
┌─────────────────────────────────────────────────────────────┐
│  Access K-Sphere                                            │
│  ───────────────                                            │
│                                                              │
│  🌐 Open browser to: http://localhost:3000                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Stop K-Sphere                                              │
│  ──────────────                                             │
│                                                              │
│  📁 Open Terminal/PowerShell                                │
│  📂 cd C:\Users\YourName\k-sphere  (or ~/k-sphere)          │
│  ⏹️  docker-compose stop                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Start K-Sphere Again                                       │
│  ─────────────────────                                      │
│                                                              │
│  📁 Open Terminal/PowerShell                                │
│  📂 cd C:\Users\YourName\k-sphere  (or ~/k-sphere)          │
│  ▶️  docker-compose start                                    │
│  🌐 Open: http://localhost:3000                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Uninstall K-Sphere                                         │
│  ───────────────────                                        │
│                                                              │
│  📁 Open Terminal/PowerShell                                │
│  📂 cd C:\Users\YourName\k-sphere  (or ~/k-sphere)          │
│  🗑️  docker-compose down -v                                 │
│  📂 cd ..                                                    │
│  🗑️  rmdir /s k-sphere  (or rm -rf k-sphere on Mac/Linux)   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🆘 Quick Troubleshooting

```
┌─────────────────────────────────────────────────────────────┐
│  Problem: "Docker is not running"                           │
│  ─────────────────────────────────                          │
│                                                              │
│  ✅ Solution:                                               │
│     1. Open Docker Desktop from Start Menu                  │
│     2. Wait for "Engine running" message                    │
│     3. Run installer again                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Problem: "Port already in use"                             │
│  ───────────────────────────                                │
│                                                              │
│  ✅ Solution:                                               │
│     Something else is using port 3000 or 8000               │
│     Stop that service and try again                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Problem: Installation very slow                            │
│  ────────────────────────────                               │
│                                                              │
│  ✅ This is normal:                                         │
│     - First time takes 5-10 minutes                         │
│     - Downloading 1-2 GB AI model                           │
│     - Building Docker containers                            │
│     - Be patient! ☕                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 System Requirements

```
┌─────────────────────────────────────────────────────────────┐
│  Minimum Requirements                                       │
│  ────────────────────                                       │
│                                                              │
│  💻 OS:       Windows 10/11, macOS 10.15+, Linux           │
│  🧠 RAM:      8 GB (16 GB recommended)                      │
│  💾 Storage:  10 GB free space                              │
│  🐳 Docker:   Docker Desktop installed                      │
│  🌐 Internet: Required for setup                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎉 That's It!

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     K-Sphere is now installed and ready to use! 🚀       ║
║                                                           ║
║     Open http://localhost:3000 and start chatting!       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**Need more help?** See:
- `WINDOWS_INSTALLATION.md` - Detailed Windows guide
- `INSTALLATION.md` - Complete documentation
- `QUICK_REFERENCE.md` - Command reference
- `COPY_TO_NEW_PC.md` - Distribution guide
