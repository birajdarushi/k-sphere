# System-Wide Indexing - Quick Reference Card

## 🚀 Quick Start (30 seconds)

```bash
# 1. Install dependency
pip install watchdog

# 2. Start backend
python main.py

# 3. Open UI
http://localhost:3000/system-indexer

# 4. Add a path
Click "Add Path" → Enter ~/Documents → Add

# 5. Start indexing
Click "Start Indexing"

# 6. Enable monitoring
Toggle "Auto-Monitor" switch
```

## 📍 Key URLs

| Purpose | URL |
|---------|-----|
| System Indexer UI | `http://localhost:3000/system-indexer` |
| API Base | `http://localhost:8000/api/system-indexer` |
| API Docs | `http://localhost:8000/docs` |

## 🔑 Essential API Endpoints

### Add Path
```bash
curl -X POST http://localhost:8000/api/system-indexer/permitted-paths \
  -H "Content-Type: application/json" \
  -d '{"path": "/Users/username/Documents"}'
```

### Start Indexing
```bash
curl -X POST http://localhost:8000/api/system-indexer/start \
  -H "Content-Type: application/json" \
  -d '{"max_files": 100}'
```

### Get Status
```bash
curl http://localhost:8000/api/system-indexer/status
```

### Start Monitoring
```bash
curl -X POST http://localhost:8000/api/system-indexer/monitoring/start
```

## 📁 Supported File Types

### Documents (9 types)
`.pdf` `.docx` `.doc` `.txt` `.md` `.rtf` `.odt`

### Code (20+ types)
`.py` `.js` `.ts` `.jsx` `.tsx` `.java` `.cpp` `.c` `.h` `.cs` `.php` `.rb` `.go` `.rs` `.swift` `.kt`

### Config (6 types)
`.json` `.yaml` `.yml` `.xml` `.toml` `.ini` `.conf`

### Web (5 types)
`.html` `.htm` `.css` `.scss` `.less`

### Data (3 types)
`.csv` `.tsv` `.sql`

### Images (6 types)
`.jpg` `.jpeg` `.png` `.bmp` `.gif` `.tiff`

### Audio (5 types)
`.mp3` `.wav` `.m4a` `.flac` `.ogg`

## 🚫 Default Exclusions

### System Directories
- `/System/`, `/private/`, `/dev/`, `/proc/`, `/sys/`
- `C:\Windows\`, `C:\Program Files\`

### Hidden/Build
- `.git/`, `.svn/`, `.hg/`
- `node_modules/`, `__pycache__/`, `.venv/`
- `build/`, `dist/`, `target/`

### Temp/Cache
- `/tmp/`, `/var/cache/`
- `AppData\Local\Temp\`

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid path, already exists, etc.) |
| 500 | Server error (check logs) |

## 🔍 Troubleshooting

### Problem: Indexing is slow
**Solutions:**
- Use `max_files` parameter
- Add exclusions for large folders
- Check CPU usage

### Problem: Files not indexed
**Checks:**
1. Extension supported?
2. Path not excluded?
3. File readable?
4. Sufficient disk space?

### Problem: Monitoring not working
**Requirements:**
- `watchdog` installed
- Path exists and readable
- On macOS: Full Disk Access granted

### Problem: High memory usage
**Solutions:**
- Index in smaller batches
- Reduce concurrent processing
- Close other applications

## 📈 Statistics Explained

| Metric | Description |
|--------|-------------|
| **Indexed Files** | Successfully processed files |
| **Failed Files** | Files that encountered errors |
| **Skipped Files** | Already indexed, no changes |
| **Total Size** | Combined size of all indexed files |

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| `src/config/settings.py` | Backend configuration |
| `data/k-sphere.db` | SQLite database |
| `data/vectordb/` | ChromaDB vector storage |
| `logs/k-sphere.log` | Application logs |

## 🔐 Security Checklist

- [ ] Review permitted paths regularly
- [ ] Add exclusions for sensitive directories
- [ ] Check that Ollama runs locally
- [ ] Verify no external network calls
- [ ] Backup important files (standard practice)

## 📋 Common Commands

### Backend
```bash
# Start server
python main.py

# Check logs
tail -f logs/k-sphere.log

# Install dependencies
pip install -r requirements.txt
```

### Frontend
```bash
# Start dev server
npm run dev

# Build production
npm run build

# Start production
npm start
```

## 💡 Pro Tips

1. **Start Small**: Begin with one directory to test
2. **Use Exclusions**: Add patterns for folders you don't need
3. **Enable Monitoring**: Keep index up-to-date automatically
4. **Check Logs**: Use logs for debugging issues
5. **Batch Processing**: Use `max_files` for large directories
6. **Regular Cleanup**: Remove old/unused permitted paths

## 🆘 Getting Help

1. **Check Logs**: `logs/k-sphere.log`
2. **Read Docs**: `SYSTEM_INDEXER_GUIDE.md`
3. **View Architecture**: `ARCHITECTURE_DIAGRAMS.md`
4. **API Docs**: `http://localhost:8000/docs`

## 📞 Support Resources

| Resource | Location |
|----------|----------|
| Full Guide | `SYSTEM_INDEXER_GUIDE.md` |
| Architecture | `ARCHITECTURE_DIAGRAMS.md` |
| Implementation Details | `SYSTEM_INDEXER_IMPLEMENTATION.md` |
| API Documentation | `/docs` endpoint |
| Source Code | `src/services/system_indexer.py` |

## 🎯 Best Practices

### ✅ Do
- Add specific paths you need
- Use custom exclusions
- Enable auto-monitoring
- Monitor progress
- Review logs regularly

### ❌ Don't
- Index entire system at once
- Ignore exclusions
- Skip testing with small paths
- Forget to check disk space
- Add sensitive directories

## 📊 Expected Performance

| Operation | Speed | Notes |
|-----------|-------|-------|
| Text files | 5-10/sec | Fast processing |
| PDFs | 2-5/sec | Depends on size |
| Images | 2-3/sec | OCR is slow |
| Audio | 0.5-1/sec | Transcription is slow |
| Code files | 5-10/sec | Fast like text |

## 🔄 Update & Maintenance

### Daily
- Check indexing status
- Review any failed files

### Weekly
- Check permitted paths
- Review exclusions
- Clean up logs if large

### Monthly
- Review disk usage
- Update exclusion patterns
- Test with new file types

---

**Version**: 1.0.0  
**Last Updated**: October 6, 2025  
**Quick Start Time**: < 1 minute  
**Full Setup Time**: < 5 minutes
