> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# K-Sphere Dynamic Model Selection & Debug Server Setup

## ✅ What's Been Implemented

### 1. **Backend Settings API** (Port 8000)
All settings endpoints are now live:

- **GET /api/settings** - Get current configuration
- **POST /api/settings** - Update settings
- **GET /api/settings/models** - List all available Ollama models
- **POST /api/settings/models/pull** - Pull new models from Ollama
- **POST /api/settings/models/switch** - Switch active LLM or embedding model
- **GET /api/settings/models/pull-status/{model}** - Check if model is ready

### 2. **Debug Server** (Port 8001)
Separate server for vector DB visualization:

- **GET /stats** - Collection statistics and file counts
- **GET /collections** - List all collections
- **GET /embeddings** - Get embeddings with metadata
- **POST /search-viz** - Visualize search queries and results
- **GET /files** - List all indexed files
- **GET /ui** - Built-in HTML dashboard

### 3. **Frontend Settings Page**
Dynamic model selection interface:

- **Dropdown selectors** for LLM and embedding models
- **Pull new models** button with dialog
- **Live model switching** without restart
- **Pull status polling** to check when models are ready
- **Toast notifications** for all actions

---

## 🚀 How to Use

### Start the Main Backend (Port 8000)
```bash
cd /Users/rushiraj/Desktop/k-sphere-backend
./venv/bin/python main.py
```

### Start the Debug Server (Port 8001)
```bash
cd /Users/rushiraj/Desktop/k-sphere-backend
./venv/bin/python debug_server.py
```

### Start the Frontend (Port 3000)
```bash
cd /Users/rushiraj/Desktop/k-sphere-frontend
npm run dev
```

### Access the Interfaces
- **Main App**: http://localhost:3000
- **Settings Page**: http://localhost:3000/settings
- **Debug Console**: http://localhost:8001/ui
- **Backend API Docs**: http://localhost:8000/docs

---

## 📝 Using Dynamic Model Selection

### 1. Switch Between Existing Models
1. Go to **Settings** page
2. Find the **LLM Model** or **Embedding Model** card
3. Click the dropdown
4. Select a different model
5. Model switches instantly! ✨

### 2. Pull a New Model
1. Click **Pull New Model** button
2. Enter model name (examples below)
3. Click **Pull Model**
4. Wait for download to complete (progress shown at top)
5. Model appears in dropdown when ready

### Popular Models to Try:
```bash
# Fast & Lightweight
llama3.2:1b
mistral:7b
gemma:2b

# Powerful
llama3.2:3b          # Default
mixtral:8x7b
codellama:13b

# Specialized
phi3                 # Math/reasoning
vicuna:13b          # Chat optimized
deepseek-coder      # Code generation
```

### 3. Monitor Pull Status
The UI automatically polls the backend every 3 seconds to check if the model is ready. You'll see:
- 🔵 Blue banner while pulling
- 🟢 Green toast when complete

---

## 🔍 Using the Debug Console

### Access: http://localhost:8001/ui

### Features:

1. **Overview Cards**
   - Total chunks indexed
   - Total files processed
   - Number of collections

2. **Collections View**
   - See documents, images, audio collections
   - Chunk counts per collection
   - Files per collection

3. **Indexed Files**
   - List all uploaded files
   - See chunk count per file
   - File type and size

4. **Search Visualization**
   - Enter a search query
   - See top 5 results
   - View relevance scores (0-100%)
   - See distance metrics

### Example Queries:
```
"machine learning algorithms"
"how to deploy kubernetes"
"python data structures"
```

---

## 🔧 API Examples

### Pull a Model (Backend)
```bash
curl -X POST http://localhost:8000/api/settings/models/pull \
  -H "Content-Type: application/json" \
  -d '{"model_name": "mistral"}'
```

### Switch LLM Model
```bash
curl -X POST http://localhost:8000/api/settings/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_type": "llm", "model_name": "mistral"}'
```

### Get Vector DB Stats
```bash
curl http://localhost:8001/stats | jq
```

### Search Visualization
```bash
curl -X POST http://localhost:8001/search-viz \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "limit": 5}' | jq
```

---

## 📂 File Structure

### Backend
```
k-sphere-backend/
├── main.py                           # Main app (port 8000)
├── debug_server.py                   # Debug server (port 8001)
├── src/
│   ├── services/
│   │   └── settings_service.py       # Settings persistence
│   └── routes/
│       └── settings.py               # Settings endpoints
└── data/
    └── settings.json                 # Saved configuration
```

### Frontend
```
k-sphere-frontend/
├── app/
│   ├── settings/
│   │   └── page.tsx                  # Dynamic settings UI
│   └── api/
│       └── settings/
│           ├── route.ts              # Settings proxy
│           └── models/
│               ├── route.ts          # Models list/pull
│               ├── switch/
│               │   └── route.ts      # Model switch
│               └── pull-status/
│                   └── [model]/
│                       └── route.ts  # Pull status check
```

---

## 🎯 What's Next?

### Remaining Tasks:
1. ⏳ **Docker Deployment** - Create Dockerfiles and docker-compose
2. ⏳ **Installer Scripts** - One-click installation
3. ⏳ **Enhanced Visualization** - Add more charts and graphs

### Want to Test?

1. **Start all servers** (backend, debug, frontend)
2. **Go to Settings** and try switching models
3. **Pull a new model** (e.g., `mistral`)
4. **Open Debug Console** to see your vector DB
5. **Try search visualization** with different queries

---

## 🐛 Troubleshooting

### Models not loading?
- Make sure Ollama is running: `ollama list`
- Check backend logs for errors
- Verify `http://localhost:8000/docs` is accessible

### Pull taking too long?
- Large models can take 5-10 minutes
- Check Ollama logs: `docker logs ollama` (if using Docker)
- Monitor with: `ollama ps`

### Debug server not starting?
- Port 8001 must be free
- Check if main backend is running first
- Ensure vector DB is initialized

---

## 📊 Settings Storage

All settings are saved to: `/Users/rushiraj/Desktop/k-sphere-backend/data/settings.json`

Example:
```json
{
  "ollama_llm_model": "llama3.2:3b",
  "ollama_embedding_model": "nomic-embed-text",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "top_k": 5,
  "watch_directory": "./data/uploads",
  "database_path": "./data/k-sphere.db",
  "vector_db_path": "./data/vectordb"
}
```

Settings persist across restarts! 🎉
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
