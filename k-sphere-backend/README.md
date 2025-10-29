# K-Sphere AI Backend

Offline-first multimodal RAG (Retrieval-Augmented Generation) system powered by Ollama. This backend processes documents, images, and audio files, stores them in a vector database, and provides intelligent chat capabilities with source citations.

## 🚀 Features

- **Multimodal File Processing**: PDF, DOCX, TXT, Images (JPG, PNG), Audio (MP3, WAV, M4A)
- **Local AI**: Uses Ollama for embeddings and LLM (runs completely offline)
- **Vector Database**: ChromaDB for efficient similarity search
- **RAG Pipeline**: Retrieves context from ONLY uploaded files (not model's training data)
- **Chat Interface**: Conversational AI with source citations
- **RESTful API**: FastAPI-based backend
- **Metadata Storage**: SQLite for file metadata and chat history

## 📋 Prerequisites

- **Python 3.8+**
- **Ollama** (installed and running)
- **Tesseract OCR** (for image text extraction)
- **FFmpeg** (for audio processing)

### macOS Installation

```bash
# Install Ollama
brew install ollama

# Install Tesseract
brew install tesseract

# Install FFmpeg
brew install ffmpeg

# Start Ollama service
ollama serve
```

## 🛠️ Setup

### 1. Clone/Navigate to Backend Directory

```bash
cd /Users/rushiraj/Desktop/k-sphere-backend
```

### 2. Pull Required Ollama Models

```bash
# Pull LLM model (for chat responses)
ollama pull llama3.2:3b

# Pull embedding model (for vector search)
ollama pull nomic-embed-text
```

### 3. Run the Startup Script

```bash
chmod +x start.sh
./start.sh
```

The script will:
- Create a virtual environment
- Install Python dependencies
- Set up the database and directories
- Start the FastAPI server on `http://localhost:8000`

### Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run the server
python main.py
```

## 📁 Project Structure

```
k-sphere-backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── start.sh               # Startup script
├── .env.example           # Environment variables template
├── src/
│   ├── config/
│   │   └── settings.py    # Configuration management
│   ├── models/
│   │   └── schemas.py     # Pydantic models
│   ├── routes/
│   │   ├── knowledge_base.py  # File upload/management endpoints
│   │   ├── chat.py            # Chat and search endpoints
│   │   └── system.py          # System status and settings
│   ├── services/
│   │   ├── ollama_service.py      # Ollama API integration
│   │   ├── vector_db_service.py   # ChromaDB operations
│   │   ├── database_service.py    # SQLite operations
│   │   └── file_processor.py      # File processing pipeline
│   └── utils/
├── data/
│   ├── uploads/           # Uploaded files storage
│   ├── vectordb/          # ChromaDB persistent storage
│   └── k-sphere.db        # SQLite database
└── logs/
    └── k-sphere.log       # Application logs
```

## 🔌 API Endpoints

### System Status

```bash
GET /api/system-status
```

Returns health status of all services (Ollama, Vector DB, Whisper)

### Knowledge Base

```bash
# Get all files
GET /api/knowledge-base

# Upload files
POST /api/knowledge-base
Content-Type: multipart/form-data

# Get file details
GET /api/knowledge-base/{file_id}

# Delete file
DELETE /api/knowledge-base/{file_id}

# Get statistics
GET /api/knowledge-base/stats
```

### Chat

```bash
# Send chat message
POST /api/chat
{
  "query": "What is this document about?",
  "conversationId": "optional-uuid",
  "topK": 5
}

# Get chat history
GET /api/chat/history?conversationId=uuid

# Search knowledge base
POST /api/search
{
  "query": "search term",
  "type": "all|document|image|audio",
  "limit": 5
}
```

### Settings

```bash
# Get settings
GET /api/settings

# Update settings
PUT /api/settings

# Trigger manual ingestion
POST /api/ingestion/trigger
```

## 🎯 How It Works

### RAG Pipeline (Critical!)

The system is designed to answer questions ONLY from uploaded content:

1. **User uploads files** → Files are processed and chunked
2. **Embeddings generated** → Using `nomic-embed-text` model
3. **Stored in ChromaDB** → For fast similarity search
4. **User asks question** → Query is embedded
5. **Vector search** → Finds most relevant chunks from uploaded files
6. **Context built** → From retrieved chunks ONLY
7. **LLM generates answer** → Using ONLY the provided context (not training data)

### File Processing

#### Documents (PDF, DOCX, TXT)
- Text extraction
- Chunking (512 words with 50-word overlap)
- Embedding generation
- Storage in `documents` collection

#### Images (JPG, PNG)
- OCR text extraction (Tesseract)
- Embedding generation
- Storage in `images` collection

#### Audio (MP3, WAV, M4A)
- Transcription (Whisper)
- Chunking of transcript
- Embedding generation
- Storage in `audio` collection

## ⚙️ Configuration

Edit `.env` file to customize:

```bash
# Ollama Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Processing Settings
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5

# Paths
VECTOR_DB_PATH=./data/vectordb
WATCH_DIRECTORY=./data/uploads
DATABASE_PATH=./data/k-sphere.db
```

## 🧪 Testing the Backend

### 1. Check System Status

```bash
curl http://localhost:8000/api/system-status
```

### 2. Upload a Test File

```bash
curl -X POST http://localhost:8000/api/knowledge-base \
  -F "files=@test.pdf"
```

### 3. Ask a Question

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is in the uploaded document?",
    "topK": 5
  }'
```

## 📊 Monitoring

### Logs

```bash
# View logs
tail -f logs/k-sphere.log

# Check Ollama logs
tail -f ~/.ollama/logs/server.log
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### Ollama Not Running

```bash
# Start Ollama
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### Models Not Found

```bash
# List installed models
ollama list

# Pull missing models
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### Import Errors

```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Port Already in Use

```bash
# Change port in .env
PORT=8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

### Tesseract Not Found (Image Processing)

```bash
# Install Tesseract
brew install tesseract

# Verify installation
tesseract --version
```

## 🔒 Security Notes

- This is a local-only system (no external API calls)
- All data stays on your machine
- No authentication required (for local use)

## 🚧 Limitations

- Max file size: 100MB (configurable)
- Optimized for Mac M1 with 8GB RAM
- Audio transcription uses Whisper base model (balance of speed/accuracy)
- Image OCR quality depends on image clarity

## 📝 Development

### Adding New File Types

1. Add processor method in `src/services/file_processor.py`
2. Update file type detection in upload endpoint
3. Add new collection in `vector_db_service.py` if needed

### Changing Models

Edit `.env`:
```bash
OLLAMA_LLM_MODEL=mistral:7b
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
```

Then pull the new models:
```bash
ollama pull mistral:7b
ollama pull mxbai-embed-large
```

## 📄 License

MIT License

## 🤝 Contributing

This is a local development project. Feel free to modify and extend!

## 📞 Support

Check logs at `logs/k-sphere.log` for debugging.

## 🎉 Success!

Your backend is ready! Make sure:
- ✓ Ollama is running
- ✓ Models are downloaded
- ✓ Backend is running on port 8000
- ✓ Frontend is running on port 3000

Now you can upload files and start chatting! 🚀
