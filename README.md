# K-Sphere AI 🌐

An offline-first, multimodal **Retrieval-Augmented Generation (RAG)** system designed to run entirely on your local machine. Process documents, images, and audio files with local AI models—no cloud required, no API keys needed.

---

## 🎯 What is K-Sphere?

K-Sphere AI is a private, intelligent knowledge management system that:
- **Indexes** your documents, images, and audio files
- **Understands** your content using local AI models
- **Answers** your questions with source citations
- **Remains private** — everything runs on your machine

Perfect for researchers, developers, and professionals who need intelligent document processing without uploading data to the cloud.

---

## ✨ Key Features

### 📄 Multimodal Ingestion
- **Documents**: PDF, DOCX, and text files
- **Images**: JPEG, PNG with OCR text extraction
- **Audio**: MP3, WAV with automatic transcription
- **Code**: Extract context from source files

### 💬 Intelligent Chat
- Ask questions about your knowledge base
- Get answers with source citations
- Context-aware responses using RAG
- Multimodal queries (text + images/audio)

### 🗂️ Knowledge Management
- Upload and organize files
- System Indexer for batch processing
- Folder-grouped knowledge base view
- Real-time processing status
- Preview and download capabilities

### 🔒 Privacy First
✅ 100% Local Processing  
✅ No Cloud Upload  
✅ No API Keys Required  
✅ Offline Capable  
✅ Open Source (MIT Licensed)

### ⚡ Optimized for Mac M1
- Designed for 8GB RAM systems
- Efficient quantized models
- Low resource consumption
- Smooth real-time performance

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Frontend (Next.js + React)            │
│          http://localhost:3000                  │
├─────────────────────────────────────────────────┤
│   API Layer (FastAPI)                           │
│   http://localhost:8000                         │
├─────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────┐ │
│  │ Ollama (LLM) │  │ ChromaDB     │  │ SQLite│ │
│  │   Models    │  │  Vector DB   │  │ Cache │ │
│  └──────────────┘  └──────────────┘  └───────┘ │
└─────────────────────────────────────────────────┘
         ↓
  Local File Storage & Embeddings
```

### Technology Stack

**Frontend:**
- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS v4
- shadcn/ui components
- SWR for data fetching

**Backend:**
- FastAPI
- Ollama (local LLM inference)
- ChromaDB (vector database)
- Whisper (speech-to-text)
- Python 3.10+

**AI Models:**
- **LLM**: `llama3.2:3b` or `mistral:7b` (optimized for 8GB RAM)
- **Embeddings**: `nomic-embed-text` (efficient & accurate)
- **Speech**: Whisper-based transcription

---

## 🚀 Quick Start (3 Steps)

### Prerequisites
- Git
- Docker & Docker Compose (or local Python 3.10+)
- 8GB+ RAM recommended

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/birajdarushi/k-sphere.git
cd k-sphere

# 2. Run the installer
chmod +x install.sh
./install.sh

# 3. Wait 15-30 minutes for models to download
# The system will open at http://localhost:3000
```

**For Windows:**
```bash
./install.bat
```

**For detailed installation guides**, see:
- [INSTALLATION.md](./INSTALLATION.md) - Complete setup guide
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Command reference

---

## 📖 Usage

### Web Interface

**Access at:** `http://localhost:3000`

#### 1. Upload Files (Knowledge Base)
- Click "Upload" in the sidebar
- Select documents, images, or audio files
- Files are automatically indexed
- View processing status in real-time

#### 2. Ask Questions (Chat)
- Type your question in the chat box
- Get instant answers with source citations
- Click sources to preview document content
- Ask follow-up questions in the same conversation

#### 3. Search Knowledge Base
- Use the search bar to find specific content
- Filter by file type
- View file previews and metadata

#### 4. System Indexer (Batch Processing)
- Index entire directories automatically
- Monitor progress in real-time
- Perfect for large-scale document ingestion

---

## 🐳 Docker Commands

### Daily Operations

```bash
# Start K-Sphere
docker compose up -d

# Stop K-Sphere
docker compose down

# View logs
docker compose logs -f

# Restart services
docker compose restart
```

### System Checks

```bash
# Check all services
docker compose ps

# Backend health check
curl http://localhost:8000/health

# Available models
docker exec k-sphere-ollama ollama list
```

---

## ⚙️ Configuration

### Environment Variables

Create/edit `.env` file in the project root:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Vector Database
VECTOR_DB_PATH=./k-sphere-backend/data/vectordb

# File Storage
WATCH_DIRECTORY=./k-sphere-backend/data/uploads
MAX_FILE_SIZE=100MB

# Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
```

### Change Models

Edit `docker-compose.yml`:

```yaml
environment:
  - LLM_MODEL=mistral  # Change to mistral, llama2, or other Ollama models
```

Then restart:
```bash
docker compose down
docker compose up -d
```

### Change Ports

Edit `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "8080:3000"  # Access at http://localhost:8080

  backend:
    ports:
      - "5000:8000"  # API at http://localhost:5000
```

---

## 📊 Resource Requirements

| Component | RAM | Disk | CPU |
|-----------|-----|------|-----|
| Ollama (LLM) | 2-4GB | 5GB | 1-2 cores |
| Backend (FastAPI) | 1-2GB | 2GB+ | 1-2 cores |
| Frontend (Next.js) | 512MB | 300MB | 1 core |
| ChromaDB (Vector DB) | 1-2GB | Variable | 1 core |
| **Total** | **4-8GB** | **10GB+** | **2-4 cores** |

### Recommended Hardware
- **CPU**: Apple M1/M2 or modern Intel/AMD multi-core
- **RAM**: 8GB minimum, 16GB+ recommended for large datasets
- **Storage**: SSD with 20GB+ free space
- **Network**: Broadband (for initial model downloads)

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Verify API is accessible
curl http://localhost:8000/health

# Restart backend
docker compose restart backend
```

### Models not downloading
```bash
# Manually pull models
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text

# List available models
docker exec k-sphere-ollama ollama list
```

### High memory usage
- Reduce chunk size in settings (CHUNK_SIZE env var)
- Use smaller model: `llama3.2:3b` instead of `7b`
- Close other applications

### Slow indexing
- Check CPU usage: `docker stats`
- Reduce concurrent file processing
- Increase chunk size (fewer chunks = faster)
- Check disk I/O performance

### Frontend connection errors
```bash
# Check frontend logs
docker compose logs frontend

# Clear browser cache
# Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

# Verify backend is running
docker compose ps
```

---

## 📚 API Documentation

### Interactive Docs
Access Swagger UI: `http://localhost:8000/docs`

### Key Endpoints

```
GET  /health                    - System health check
POST /api/chat                  - Send query, get answer
GET  /api/knowledge-base        - List indexed files
POST /api/knowledge-base        - Upload new files
GET  /api/search                - Search knowledge base
GET  /api/settings              - Get current settings
PUT  /api/settings              - Update settings
```

Full API specification available in [k-sphere-frontend/PRD.md](./k-sphere-frontend/PRD.md)

---

## 📖 Documentation

- **[INSTALLATION.md](./INSTALLATION.md)** - Step-by-step installation guide
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Command reference card
- **[DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md)** - Docker setup
- **[DEPLOYMENT_GUIDE.md](./k-sphere-backend/DEPLOYMENT_GUIDE.md)** - Backend deployment
- **[ARCHITECTURE_DIAGRAMS.md](./k-sphere-backend/ARCHITECTURE_DIAGRAMS.md)** - System architecture
- **[SYSTEM_INDEXER_GUIDE.md](./k-sphere-backend/SYSTEM_INDEXER_GUIDE.md)** - Batch processing

---

## 🛠️ Development

### Frontend Development

```bash
cd k-sphere-frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

### Backend Development

```bash
cd k-sphere-backend

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py

# Run with auto-reload
python debug_server.py
```

---

## 🤝 Contributing

We welcome contributions! Please feel free to:
- Report bugs and issues
- Suggest features
- Submit pull requests
- Improve documentation

**Steps:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🔐 Privacy & Security

- **Data Privacy**: All data stays on your machine. No telemetry, no tracking.
- **Security**: Use HTTPS in production. Consider network isolation for sensitive data.
- **Model Safety**: Models are open-source and can be audited.
- **No External Calls**: System operates completely offline after initial setup.

---

## 💡 Use Cases

- **Research**: Analyze academic papers and research documents
- **Development**: Index codebases and quickly find solutions
- **Knowledge Management**: Build private knowledge bases
- **Content Analysis**: Understand document collections
- **Compliance**: Process sensitive documents without cloud exposure
- **Accessibility**: Audio processing for accessibility features

---

## 🚀 Performance Tips

1. **Optimize Chunk Size**: Smaller chunks = faster retrieval, more tokens
2. **Use Appropriate Model**: Smaller models for speed, larger for accuracy
3. **Batch Processing**: Use System Indexer for bulk uploads
4. **Regular Cleanup**: Remove old/irrelevant files to free resources
5. **Monitor Resources**: Watch CPU/RAM with `docker stats`

---

## 📞 Support & Help

- **Documentation**: Check [INSTALLATION.md](./INSTALLATION.md) and [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **Issues**: Open a GitHub issue with details and logs
- **Discussions**: Use GitHub Discussions for questions
- **Logs**: Find logs in `docker compose logs -f`

---

## 🎓 Learning Resources

- [Retrieval-Augmented Generation (RAG) Explained](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js App Router](https://nextjs.org/docs/app)

---

## 🗺️ Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Multi-user authentication
- [ ] Cloud sync option (optional)
- [ ] Advanced search filters
- [ ] Export conversations and results
- [ ] Mobile app (iOS/Android)
- [ ] Plugin system for custom processors
- [ ] Advanced RAG techniques (re-ranking, etc.)

---

## ⭐ Show Your Support

If you find K-Sphere helpful, please:
- ⭐ Star this repository
- 📢 Share with others
- 💬 Provide feedback
- 🐛 Report issues
- 🤝 Contribute improvements

---

**K-Sphere AI** - Your private, intelligent knowledge assistant.

Built with ❤️ for privacy-conscious users and developers.

---

**Last Updated:** May 2026

For the latest updates and detailed guides, visit the [documentation](./QUICK_REFERENCE.md).
