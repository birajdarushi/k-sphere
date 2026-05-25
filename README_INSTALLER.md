> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# K-Sphere: One-Click AI Knowledge Management System

<div align="center">

![K-Sphere Logo](https://via.placeholder.com/200x200?text=K-Sphere)

**Your Personal AI Assistant that indexes, understands, and answers questions about all your documents**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)

</div>

---

## 🌟 What is K-Sphere?

K-Sphere is a **100% local, privacy-first AI knowledge management system** that:

- 📚 **Indexes all your documents** (PDFs, images, audio, code files)
- 🤖 **Understands content** using advanced AI (Ollama + LLaMA 3.2)
- 💬 **Answers questions** with citations from your documents
- 🔒 **Runs entirely offline** - no data leaves your machine
- 🚀 **One-click installation** - no technical knowledge required!

---

## ✨ Key Features

### 🎯 Universal File Support
- **Documents**: PDF, DOCX, TXT, MD, RTF
- **Code**: Python, JavaScript, TypeScript, Java, C++, and 40+ languages
- **Images**: PNG, JPG, GIF (with OCR text extraction)
- **Audio**: MP3, WAV, M4A (transcription via Whisper)
- **Config Files**: JSON, YAML, XML, TOML

### 🔍 System-Wide Indexing
- **Index entire directories** on your computer
- **Real-time file watching** - new files are indexed automatically
- **Smart exclusions** - skips node_modules, .git, build artifacts
- **Folder grouping** - organize 1000s of files by source path

### 💡 Intelligent Chat
- **RAG (Retrieval Augmented Generation)** - answers backed by your documents
- **Source citations** - see exactly which files were used
- **Context-aware** - remembers conversation history
- **Streaming responses** - see answers as they're generated

### 📊 Knowledge Base Management
- **Visual file browser** with folder grouping
- **File preview** for documents, images, audio
- **Search & filter** by type, status, name
- **Bulk operations** - delete, download, export

---

## 🚀 One-Click Installation

### Prerequisites

1. **Install Docker Desktop**
   - **Mac**: [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - **Windows**: [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - **Linux**: [Install Docker Engine](https://docs.docker.com/engine/install/)

2. **System Requirements**
   - **RAM**: 8GB+ recommended
   - **Disk**: 10GB+ free space
   - **CPU**: 4+ cores recommended

### Install K-Sphere (3 Steps)

#### Step 1: Download K-Sphere

```bash
git clone https://github.com/your-repo/k-sphere.git
cd k-sphere
```

**Or download ZIP**: [Download](https://github.com/your-repo/k-sphere/archive/refs/heads/main.zip)

#### Step 2: Run Installer

```bash
chmod +x install.sh
./install.sh
```

#### Step 3: Wait (~15-30 minutes)

The installer will:
- ✓ Check system requirements
- ✓ Build Docker images (5-10 min)
- ✓ Start all services
- ✓ Download AI models (10-20 min)
- ✓ Open K-Sphere in your browser

**That's it!** 🎉

---

## 📖 Quick Start Guide

### 1. Access K-Sphere

After installation, open your browser to:
- **Web UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### 2. Upload Documents

Two ways to add content:

**A. Manual Upload** (Knowledge Base page)
- Drag & drop files
- Or click "Upload Files"
- Supported: PDF, DOCX, images, audio, code

**B. System Indexer** (System Indexer page)
- Click "Add Path"
- Select folders on your computer
- Click "Start Indexing"
- K-Sphere indexes entire directories!

### 3. Ask Questions

Go to Chat page and ask questions like:
- "What are the main points in my research papers?"
- "Summarize the meeting notes from last week"
- "What does the config file say about database settings?"
- "Find all mentions of 'authentication' in the codebase"

K-Sphere will:
- ✓ Search your documents
- ✓ Find relevant information
- ✓ Generate an answer
- ✓ Show which files were used

---

## 🎮 Usage Examples

### Example 1: Research Assistant

```
You: What are the key findings about neural networks in my papers?

K-Sphere: Based on your research papers, the key findings about neural 
networks are:

1. Deep learning architectures with residual connections improve accuracy 
   by 15-20% (Source: neural_networks_2024.pdf, page 12)

2. Attention mechanisms significantly reduce training time while 
   maintaining accuracy (Source: attention_paper.pdf, page 8)

3. Transfer learning from pre-trained models reduces data requirements 
   by 60% (Source: transfer_learning_study.pdf, page 5)

Sources: neural_networks_2024.pdf, attention_paper.pdf, 
transfer_learning_study.pdf
```

### Example 2: Code Documentation

```
You: How is authentication implemented in the backend?

K-Sphere: The authentication system is implemented using JWT tokens:

1. User login endpoint: /api/auth/login validates credentials and 
   returns a JWT token (Source: auth.py, lines 45-67)

2. Token validation middleware checks the Authorization header on 
   protected routes (Source: middleware.py, lines 23-41)

3. Tokens expire after 24 hours and use RS256 algorithm 
   (Source: config.json)

Sources: auth.py, middleware.py, config.json
```

### Example 3: Meeting Notes

```
You: What action items came out of the Q3 planning meeting?

K-Sphere: The Q3 planning meeting resulted in these action items:

1. Sarah to complete user research by Aug 15th (Source: 
   Q3_planning_notes.docx)

2. Dev team to prototype new dashboard by Aug 30th (Source: 
   Q3_planning_notes.docx)

3. Marketing to finalize campaign materials by Sept 1st (Source: 
   Q3_planning_notes.docx)

All items tracked in project management system.

Source: Q3_planning_notes.docx
```

---

## 🛠️ Management Commands

### Start/Stop K-Sphere

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart
docker compose restart

# View logs
docker compose logs -f
```

### Update K-Sphere

```bash
git pull
docker compose build
docker compose up -d
```

### Backup Your Data

```bash
# Backup everything
tar -czf k-sphere-backup.tar.gz \
  k-sphere-backend/data \
  k-sphere-backend/logs

# Restore
tar -xzf k-sphere-backup.tar.gz
```

---

## 🔧 Configuration

### Change AI Models

Edit `docker-compose.yml`:

```yaml
environment:
  - LLM_MODEL=llama3.2:3b  # Change to: mistral, codellama, etc.
  - EMBEDDING_MODEL=nomic-embed-text
```

Available models: https://ollama.com/library

### Change Ports

Edit `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "8080:3000"  # Access at http://localhost:8080

backend:
  ports:
    - "5000:8000"  # Access at http://localhost:5000
```

### GPU Acceleration (Linux + NVIDIA)

Uncomment in `docker-compose.yml`:

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

---

## 📊 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  Frontend   │────▶│   Backend   │────▶│   Ollama    │
│  (Next.js)  │     │  (FastAPI)  │     │ (AI Models) │
│             │     │             │     │             │
│  Port 3000  │     │  Port 8000  │     │ Port 11434  │
│             │     │             │     │             │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │             │
                    │  ChromaDB   │
                    │  (Vectors)  │
                    │             │
                    └─────────────┘
```

**Technology Stack:**
- **Frontend**: Next.js 15, React, TailwindCSS, shadcn/ui
- **Backend**: Python 3.11, FastAPI, ChromaDB
- **AI**: Ollama, LLaMA 3.2, Nomic Embeddings
- **Processing**: PyPDF, Whisper, Tesseract OCR
- **Deployment**: Docker, Docker Compose

---

## 🐛 Troubleshooting

### Docker Not Running

```bash
# Start Docker Desktop
open -a Docker  # macOS

# Verify Docker is running
docker info
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :3000

# Kill the process
kill -9 <PID>
```

### Services Won't Start

```bash
# View detailed logs
docker compose logs

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Models Not Downloading

```bash
# Check Ollama logs
docker compose logs ollama

# Manually download
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text
```

**More help**: See [INSTALLATION.md](./INSTALLATION.md)

---

## 🔐 Privacy & Security

- ✅ **100% Local** - All processing happens on your machine
- ✅ **No Cloud** - No data sent to external servers
- ✅ **No API Keys** - No subscriptions or accounts required
- ✅ **Offline Capable** - Works without internet (after initial setup)
- ✅ **Open Source** - Inspect the code yourself

Perfect for:
- Personal documents
- Confidential business data
- Medical records
- Legal documents
- Research papers
- Source code

---

## 📚 Documentation

- [Installation Guide](./INSTALLATION.md) - Detailed setup instructions
- [Folder Grouping](./k-sphere-backend/FOLDER_GROUPING.md) - File organization features
- [API Documentation](http://localhost:8000/docs) - REST API reference (when running)
- [System Indexer Guide](./k-sphere-backend/SYSTEM_INDEXER.md) - Index entire directories

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repo
git clone https://github.com/your-repo/k-sphere.git
cd k-sphere

# Open in VS Code with Dev Container
code .
# Click "Reopen in Container"

# Or run locally
cd k-sphere-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd k-sphere-frontend
npm install
npm run dev
```

---

## 📝 License

[MIT License](LICENSE) - Free to use for personal and commercial projects

---

## 🌟 Star History

If K-Sphere helped you, please star the repo! ⭐

---

## 🙏 Acknowledgments

Built with amazing open-source projects:
- [Ollama](https://ollama.com/) - Local AI models
- [LLaMA](https://ai.meta.com/llama/) - Meta's language models
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components

---

<div align="center">

**Made with ❤️ by [Your Name]**

[Website](https://your-website.com) • [Twitter](https://twitter.com/yourhandle) • [Email](mailto:you@example.com)

</div>
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
