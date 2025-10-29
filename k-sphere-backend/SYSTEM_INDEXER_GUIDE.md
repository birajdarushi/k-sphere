# System-Wide Indexing Guide

## Overview

K-Sphere now includes a powerful **System-Wide Indexing** feature that allows you to index files across your entire computer with granular permission control. This feature transforms K-Sphere into a comprehensive personal knowledge management system that can search and retrieve information from any allowed directory on your system.

## Key Features

### 🔐 Permission-Based Access
- **Explicit User Control**: You must explicitly grant permission for each directory or file
- **Path-by-Path Management**: Add or remove paths at any time
- **Read-Only Access**: K-Sphere only reads files, never modifies them

### 🚫 Smart Exclusions
- **Default Exclusions**: System directories, hidden folders, and build artifacts are automatically excluded
- **Custom Patterns**: Add your own exclusion patterns for specific directories or file types
- **Performance Optimization**: Prevents indexing of unnecessary files

### 📁 Comprehensive File Support
- **Documents**: PDF, DOCX, DOC, TXT, MD, RTF, ODT
- **Code Files**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, and more
- **Config Files**: JSON, YAML, XML, TOML, INI
- **Images**: JPG, PNG, BMP (with OCR)
- **Audio**: MP3, WAV, M4A (with transcription)
- **And many more...**

### ⚡ Real-Time Monitoring
- **File System Watching**: Automatically detects file changes, additions, and deletions
- **Incremental Updates**: Only re-indexes changed files
- **Background Processing**: Operates without interrupting your work

### 📊 Progress Tracking
- **Live Statistics**: Monitor indexed, failed, and skipped files
- **Size Tracking**: See total storage indexed
- **Time Estimates**: Track indexing duration

## Installation & Setup

### 1. Install Dependencies

First, ensure the watchdog library is installed for real-time file monitoring:

```bash
cd k-sphere-backend
pip install watchdog
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Start the Backend

```bash
cd k-sphere-backend
python main.py
```

### 3. Access the System Indexer

Open your browser and navigate to:
```
http://localhost:3000/system-indexer
```

## Usage Guide

### Adding Permitted Paths

1. **Navigate to System Indexer** page in the K-Sphere UI
2. **Click "Add Path"** button in the Permitted Paths tab
3. **Enter the absolute path** to the directory or file you want to index
   - Examples:
     - macOS/Linux: `/Users/username/Documents`, `~/Desktop`
     - Windows: `C:\Users\username\Documents`
4. **Click "Add Path"** to confirm

**Tips:**
- Start with smaller directories to test the feature
- You can add individual files or entire directory trees
- Use `~` as a shortcut for your home directory on Unix systems

### Managing Exclusions

#### View Default Exclusions
K-Sphere automatically excludes common directories that shouldn't be indexed:
- System directories (`/System/`, `C:\Windows\`)
- Version control folders (`.git/`, `.svn/`)
- Dependencies (`node_modules/`, `__pycache__/`)
- Build artifacts (`build/`, `dist/`, `target/`)
- Temporary files

#### Add Custom Exclusions
1. Go to the **Exclusions** tab
2. Click **"Add Pattern"**
3. Enter a path pattern (e.g., `personal/`, `secret/`, `.env`)
4. Click **"Add Pattern"** to confirm

### Starting Indexing

#### One-Time Full Index

1. Ensure you have added at least one permitted path
2. Click the **"Start Indexing"** button
3. (Optional) Set a maximum number of files for testing
4. Monitor progress in real-time

#### Automatic Monitoring

For continuous, automatic indexing:

1. Toggle the **"Auto-Monitor"** switch
2. K-Sphere will now automatically:
   - Index new files as they're created
   - Re-index files when they're modified
   - Remove deleted files from the index
   - Handle file moves and renames

### Monitoring Progress

The System Indexer page shows:
- **Indexed Files**: Successfully processed files
- **Failed Files**: Files that couldn't be indexed
- **Skipped Files**: Files already indexed and unchanged
- **Total Size**: Combined size of indexed files
- **Current Path**: The directory currently being scanned
- **Timestamps**: Start and end times

## API Reference

### Permission Management

#### Get Permitted Paths
```http
GET /api/system-indexer/permitted-paths
```

#### Add Permitted Path
```http
POST /api/system-indexer/permitted-paths
Content-Type: application/json

{
  "path": "/Users/username/Documents"
}
```

#### Remove Permitted Path
```http
DELETE /api/system-indexer/permitted-paths
Content-Type: application/json

{
  "path": "/Users/username/Documents"
}
```

### Exclusion Management

#### Get Exclusion Patterns
```http
GET /api/system-indexer/exclusions
```

#### Add Exclusion Pattern
```http
POST /api/system-indexer/exclusions
Content-Type: application/json

{
  "pattern": "private/"
}
```

### Indexing Control

#### Start Indexing
```http
POST /api/system-indexer/start
Content-Type: application/json

{
  "max_files": 1000  // Optional
}
```

#### Stop Indexing
```http
POST /api/system-indexer/stop
```

#### Get Indexing Status
```http
GET /api/system-indexer/status
```

### File System Monitoring

#### Start Monitoring
```http
POST /api/system-indexer/monitoring/start
```

#### Stop Monitoring
```http
POST /api/system-indexer/monitoring/stop
```

#### Get Monitoring Status
```http
GET /api/system-indexer/monitoring/status
```

## Best Practices

### 🎯 Start Small
Begin with a single, small directory to understand how the system works before indexing your entire system.

### 🚫 Use Exclusions Wisely
Add exclusions for:
- Sensitive directories containing passwords or keys
- Large media libraries (unless you specifically need them)
- Virtual environments and dependencies
- System/application directories

### ⚡ Enable Auto-Monitoring
Once you're comfortable with the permitted paths, enable auto-monitoring to keep your index up-to-date automatically.

### 🔍 Regular Maintenance
Periodically review:
- Permitted paths (remove old or unnecessary paths)
- Exclusion patterns (update as needed)
- Failed files (investigate and fix issues)

### 💾 Consider Storage
Indexing creates:
- Vector embeddings (stored in ChromaDB)
- Metadata (stored in SQLite)
- Extracted text/transcriptions

Large-scale indexing can use significant disk space.

## Privacy & Security

### What K-Sphere Does
- ✅ Reads file contents with your explicit permission
- ✅ Stores processed data locally on your machine
- ✅ Uses local AI models (Ollama) for processing
- ✅ Operates completely offline

### What K-Sphere Does NOT Do
- ❌ Send your data to external servers
- ❌ Modify or delete your original files
- ❌ Access files outside permitted paths
- ❌ Share data with third parties

### Recommendations
1. **Review Permissions**: Regularly check which paths are permitted
2. **Use Exclusions**: Exclude sensitive directories explicitly
3. **Local Processing**: All AI processing happens on your machine
4. **Backup**: Keep backups of important files (standard practice)

## Troubleshooting

### Indexing is Slow
**Causes:**
- Large number of files
- Large file sizes (especially videos/audio)
- CPU-intensive OCR or transcription

**Solutions:**
- Use `max_files` parameter to index in batches
- Add exclusions for large media folders
- Increase `CHUNK_SIZE` in settings for faster processing
- Close other applications to free up CPU

### Files Not Being Indexed
**Check:**
1. File extension is supported (see Supported Files tab)
2. Path is not excluded by patterns
3. File is readable (check permissions)
4. Sufficient disk space for vector database

### Auto-Monitoring Not Working
**Requirements:**
- `watchdog` library must be installed
- Permitted paths must exist and be readable
- System must have file system access permissions

**macOS Specific:**
- Grant "Full Disk Access" to Terminal/Python in System Settings

### High Memory Usage
**Solutions:**
- Reduce concurrent file processing (modify `Semaphore(5)` in code)
- Index in smaller batches
- Increase system RAM
- Close unused applications

## Performance Tips

### Optimize Indexing Speed
1. **Exclude Large Directories**: Add exclusions for media libraries, archives
2. **Batch Processing**: Use `max_files` parameter for controlled indexing
3. **Storage Location**: Use SSD for vector database storage
4. **Concurrent Limits**: Adjust semaphore value for your CPU

### Optimize Query Performance
1. **Regular Indexing**: Keep index up-to-date with auto-monitoring
2. **Cleanup**: Remove old/unused paths
3. **Embeddings**: Use efficient embedding models (nomic-embed-text is optimized)

## Advanced Configuration

### Modify Chunk Sizes
Edit `src/config/settings.py`:
```python
CHUNK_SIZE = 512  # Increase for faster processing, decrease for accuracy
CHUNK_OVERLAP = 50  # Overlap between chunks
```

### Change Concurrency
Edit `src/services/system_indexer.py`:
```python
semaphore = asyncio.Semaphore(5)  # Increase for faster, decrease for lower CPU usage
```

### Adjust Monitoring Interval
Edit `src/services/fs_watcher.py`:
```python
await asyncio.sleep(5)  # Check for changes every 5 seconds
```

## Examples

### Example 1: Index Your Documents
```bash
# Add your Documents folder
POST /api/system-indexer/permitted-paths
{
  "path": "~/Documents"
}

# Exclude sensitive folders
POST /api/system-indexer/exclusions
{
  "pattern": "Documents/Taxes/"
}

# Start indexing
POST /api/system-indexer/start
```

### Example 2: Monitor Code Projects
```bash
# Add your projects folder
POST /api/system-indexer/permitted-paths
{
  "path": "~/Projects"
}

# Exclude dependencies
POST /api/system-indexer/exclusions
{
  "pattern": "node_modules/"
}

# Enable auto-monitoring
POST /api/system-indexer/monitoring/start
```

### Example 3: Index Specific Files
```bash
# Add individual files
POST /api/system-indexer/permitted-paths
{
  "path": "~/important-notes.md"
}

POST /api/system-indexer/permitted-paths
{
  "path": "~/research-paper.pdf"
}

# Start indexing
POST /api/system-indexer/start
```

## FAQ

**Q: Can I index external drives?**
A: Yes! Just add the drive's mount point as a permitted path.

**Q: How long does indexing take?**
A: Depends on file count and size. Expect ~1-10 files per second.

**Q: Can I pause and resume indexing?**
A: Currently, you can stop indexing, but resume will restart from the beginning. Files already indexed will be skipped if unchanged.

**Q: What happens if I delete a permitted path?**
A: The indexed data remains in the vector database until you manually delete it from Knowledge Base.

**Q: Can multiple users use system-wide indexing?**
A: Yes, but each user needs their own K-Sphere instance with separate permissions.

**Q: Is there a file size limit?**
A: Default is 100MB per file. Modify `MAX_FILE_SIZE` in settings.py if needed.

## Support

For issues, questions, or feature requests:
1. Check the logs: `logs/k-sphere.log`
2. Review this documentation
3. Check GitHub issues
4. Open a new issue with detailed information

## Future Enhancements

Planned features:
- [ ] Scheduling (index at specific times)
- [ ] Priority paths (index certain paths first)
- [ ] Bandwidth limiting
- [ ] Remote path support (network drives)
- [ ] Duplicate detection
- [ ] Advanced filtering (by date, size, type)
- [ ] Export/import configurations
- [ ] Cloud sync options (optional)

---

**Last Updated**: October 2025  
**Version**: 1.0.0
