> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# K-Sphere Quick Reference Card

## 🚀 Installation (3 Steps)

```bash
# 1. Download
git clone <repo-url> && cd k-sphere

# 2. Install
chmod +x install.sh && ./install.sh

# 3. Wait 15-30 minutes → Opens at http://localhost:3000
```

---

## 🎮 Daily Commands

```bash
# Start K-Sphere
docker compose up -d

# Stop K-Sphere
docker compose down

# View logs
docker compose logs -f

# Restart
docker compose restart
```

---

## 🔍 Quick Checks

```bash
# Is everything running?
docker compose ps

# Backend healthy?
curl http://localhost:8000/health

# Check models
docker exec k-sphere-ollama ollama list
```

---

## 📍 URLs

- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## 🐛 Quick Fixes

```bash
# Rebuild everything
docker compose down
docker compose build --no-cache
docker compose up -d

# Clean Docker
docker system prune -a

# Redownload models
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text
```

---

## 💾 Backup & Restore

```bash
# Backup
tar -czf k-sphere-backup-$(date +%Y%m%d).tar.gz \
  k-sphere-backend/data \
  k-sphere-backend/logs

# Restore
tar -xzf k-sphere-backup-*.tar.gz
```

---

## ⚙️ Configuration

Edit `docker-compose.yml`:

```yaml
# Change AI model
environment:
  - LLM_MODEL=mistral

# Change ports
ports:
  - "8080:3000"  # Frontend
  - "5000:8000"  # Backend
```

---

## 📊 Resource Usage

| Component | RAM | Disk | CPU |
|-----------|-----|------|-----|
| Ollama | 2-4GB | 5GB | 1-2 cores |
| Backend | 1-2GB | 2GB+ | 1-2 cores |
| Frontend | 512MB | 300MB | 1 core |
| **Total** | **4-8GB** | **10GB+** | **2-4 cores** |

---

## 🎯 Feature Checklist

- [ ] Upload files (PDF, images, audio, code)
- [ ] Index entire directories (System Indexer)
- [ ] Ask questions in Chat
- [ ] Get answers with citations
- [ ] View folder-grouped Knowledge Base
- [ ] Preview files
- [ ] Download files
- [ ] Delete files
- [ ] Clean up stuck files

---

## 🆘 Support

- **Logs**: `docker compose logs -f`
- **Docs**: See `INSTALLATION.md`
- **Issues**: GitHub Issues
- **Status**: `docker compose ps`

---

## 🔐 Privacy

✅ 100% Local  
✅ No Cloud  
✅ No API Keys  
✅ Offline Capable  
✅ Open Source

---

**Quick Start**: Run `./install.sh` and you're done! 🎉
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
