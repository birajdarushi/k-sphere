> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# K-Sphere Deployment & Features Guide

## Overview
This guide covers three major enhancements:
1. **Dynamic Model Switching** - Change LLM models from Settings UI
2. **Docker Containerization** - Portable, plug-and-play deployment
3. **Vector DB Visualization** - GUI to explore your knowledge base

---

## 1. 🔧 Dynamic Model Selection

### Current State
- Models are hardcoded in `settings.py`
- No way to change models without editing code
- No way to pull new models from UI

### Desired State
- Settings page shows all available Ollama models
- Dropdown to select LLM and embedding models
- Button to pull new models (e.g., "Add ChatGPT")
- Dynamic model switching without restart

### Implementation Plan

#### Backend Changes

**1. Create Settings Service** (`src/services/settings_service.py`):
```python
import json
import os
from typing import Dict, Any, Optional

class SettingsService:
    def __init__(self, settings_file: str = "./data/settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create defaults"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        
        # Default settings
        return {
            "ollama_llm_model": "llama3.2:3b",
            "ollama_embedding_model": "nomic-embed-text",
            "chunk_size": 512,
            "chunk_overlap": 50,
            "top_k": 5
        }
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            self.settings = settings
            return True
        except Exception as e:
            return False
    
    def get_setting(self, key: str) -> Optional[Any]:
        """Get a specific setting"""
        return self.settings.get(key)
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a specific setting"""
        self.settings[key] = value
        return self.save_settings(self.settings)
```

**2. Add Settings Endpoints** (`src/routes/settings.py`):
```python
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import subprocess

router = APIRouter()

@router.get("/settings")
async def get_settings():
    """Get current settings"""
    return settings_service.settings

@router.post("/settings")
async def update_settings(new_settings: Dict[str, Any]):
    """Update settings"""
    success = settings_service.save_settings(new_settings)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save settings")
    
    # Reload ollama service with new models
    ollama_service.llm_model = new_settings.get("ollama_llm_model")
    ollama_service.embedding_model = new_settings.get("ollama_embedding_model")
    
    return {"success": True, "settings": settings_service.settings}

@router.get("/settings/models")
async def get_available_models():
    """Get all available Ollama models"""
    health = await ollama_service.check_health()
    return {
        "available": health.get("available_models", []),
        "current_llm": settings_service.get_setting("ollama_llm_model"),
        "current_embedding": settings_service.get_setting("ollama_embedding_model")
    }

@router.post("/settings/models/pull")
async def pull_model(model_name: str):
    """Pull a new model from Ollama"""
    try:
        # Run ollama pull command
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return {"success": True, "message": f"Model {model_name} pulled successfully"}
        else:
            raise HTTPException(status_code=500, detail=result.stderr)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Model pull timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings/models/switch")
async def switch_model(model_type: str, model_name: str):
    """Switch active LLM or embedding model"""
    if model_type not in ["llm", "embedding"]:
        raise HTTPException(status_code=400, detail="Invalid model type")
    
    # Verify model exists
    exists = await ollama_service.check_model_exists(model_name)
    if not exists:
        raise HTTPException(
            status_code=404, 
            detail=f"Model {model_name} not found. Pull it first."
        )
    
    # Update setting
    key = f"ollama_{model_type}_model"
    success = settings_service.update_setting(key, model_name)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update setting")
    
    # Reload ollama service
    if model_type == "llm":
        ollama_service.llm_model = model_name
    else:
        ollama_service.embedding_model = model_name
    
    return {"success": True, "model": model_name}
```

#### Frontend Changes

**Update Settings Page** (`app/settings/page.tsx`):
```tsx
"use client"

import { useState, useEffect } from "react"
import useSWR from "swr"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"

export default function SettingsPage() {
  const { toast } = useToast()
  const [selectedLLM, setSelectedLLM] = useState("")
  const [selectedEmbedding, setSelectedEmbedding] = useState("")
  const [newModelName, setNewModelName] = useState("")
  const [isPulling, setIsPulling] = useState(false)

  // Fetch available models
  const { data: modelsData, mutate } = useSWR("/api/settings/models", async (url) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}${url}`)
    return response.json()
  })

  useEffect(() => {
    if (modelsData) {
      setSelectedLLM(modelsData.current_llm)
      setSelectedEmbedding(modelsData.current_embedding)
    }
  }, [modelsData])

  const handleSwitchModel = async (type: "llm" | "embedding", modelName: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/settings/models/switch`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ model_type: type, model_name: modelName })
        }
      )

      if (response.ok) {
        toast({
          title: "Model Switched",
          description: `Now using ${modelName} for ${type === "llm" ? "chat" : "embeddings"}`
        })
        mutate()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to switch model",
        variant: "destructive"
      })
    }
  }

  const handlePullModel = async () => {
    if (!newModelName.trim()) return

    setIsPulling(true)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/settings/models/pull?model_name=${newModelName}`,
        { method: "POST" }
      )

      if (response.ok) {
        toast({
          title: "Model Pulled",
          description: `${newModelName} is now available`
        })
        setNewModelName("")
        mutate()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to pull model",
        variant: "destructive"
      })
    } finally {
      setIsPulling(false)
    }
  }

  return (
    <Card className="border-border bg-card p-6">
      <h3 className="font-semibold text-foreground mb-4">LLM Model</h3>
      
      <Label>Select Model</Label>
      <Select value={selectedLLM} onValueChange={(val) => {
        setSelectedLLM(val)
        handleSwitchModel("llm", val)
      }}>
        <SelectTrigger>
          <SelectValue placeholder="Select LLM model" />
        </SelectTrigger>
        <SelectContent>
          {modelsData?.available?.map((model: string) => (
            <SelectItem key={model} value={model}>
              {model}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div className="mt-4">
        <Label>Pull New Model</Label>
        <div className="flex gap-2">
          <Input
            placeholder="e.g., chatgpt, mistral, gemma"
            value={newModelName}
            onChange={(e) => setNewModelName(e.target.value)}
          />
          <Button onClick={handlePullModel} disabled={isPulling}>
            {isPulling ? "Pulling..." : "Pull"}
          </Button>
        </div>
      </div>
    </Card>
  )
}
```

---

## 2. 🐳 Docker Containerization (Plug & Play)

### Goals
- ✅ Run on any OS (Mac, Windows, Linux)
- ✅ Support both CPU and GPU (NVIDIA)
- ✅ One command installation
- ✅ Data persistence across restarts
- ✅ Portable (copy folder to USB, run anywhere)

### Docker Architecture

```
k-sphere/
├── docker-compose.yml          # Orchestrates all services
├── install.sh                  # Mac/Linux installer
├── install.bat                 # Windows installer
├── backend/
│   ├── Dockerfile             # Python + FastAPI
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile             # Next.js production build
│   └── package.json
└── data/                      # Persistent data (mounted volume)
    ├── uploads/               # User files
    ├── vectordb/              # ChromaDB
    ├── k-sphere.db            # SQLite
    └── settings.json          # Configuration
```

### Implementation

#### 1. Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start script
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

#### 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: k-sphere-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]  # Enable GPU if available

  backend:
    build: ./backend
    container_name: k-sphere-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - ollama
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: k-sphere-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  ollama_data:
```

#### 4. Install Scripts

**Mac/Linux** (`install.sh`):
```bash
#!/bin/bash
set -e

echo "🚀 Installing K-Sphere..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create data directory
mkdir -p data/uploads data/vectordb

# Pull and start containers
echo "🐳 Starting K-Sphere containers..."
docker-compose pull
docker-compose up -d

# Pull default models
echo "📥 Pulling default AI models..."
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text

echo "✅ K-Sphere installed successfully!"
echo "🌐 Access K-Sphere at: http://localhost:3000"
echo ""
echo "📝 Commands:"
echo "  Start:  docker-compose up -d"
echo "  Stop:   docker-compose down"
echo "  Logs:   docker-compose logs -f"
```

**Windows** (`install.bat`):
```batch
@echo off
echo 🚀 Installing K-Sphere...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not found. Please install Docker Desktop from:
    echo    https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Create data directory
if not exist "data\uploads" mkdir data\uploads
if not exist "data\vectordb" mkdir data\vectordb

REM Pull and start containers
echo 🐳 Starting K-Sphere containers...
docker-compose pull
docker-compose up -d

REM Pull default models
echo 📥 Pulling default AI models...
docker exec k-sphere-ollama ollama pull llama3.2:3b
docker exec k-sphere-ollama ollama pull nomic-embed-text

echo ✅ K-Sphere installed successfully!
echo 🌐 Access K-Sphere at: http://localhost:3000
echo.
echo 📝 Commands:
echo   Start:  docker-compose up -d
echo   Stop:   docker-compose down
echo   Logs:   docker-compose logs -f
pause
```

### GPU Support (Windows with NVIDIA)

**Requirements**:
- NVIDIA GPU
- NVIDIA drivers installed
- Docker Desktop with WSL2 backend
- NVIDIA Container Toolkit

**Setup**:
```bash
# Install NVIDIA Container Toolkit (WSL2)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Portable Deployment

To make it truly plug-and-play:

1. **Package everything**:
```bash
tar -czf k-sphere-portable.tar.gz \
  docker-compose.yml \
  backend/ \
  frontend/ \
  install.sh \
  install.bat \
  README.md
```

2. **USB/Cloud deployment**:
- Copy `k-sphere-portable.tar.gz` to USB
- Extract on any machine
- Run `./install.sh` or `install.bat`
- Everything works!

---

## 3. 📊 Vector DB Visualization

### Current State
- Vector DB is a black box
- No way to see what's indexed
- Can't visualize embeddings
- Hard to debug relevance issues

### Desired Features

1. **Collection Overview**
   - Show all collections (documents, images, audio)
   - Chunk counts per file
   - Total embeddings stored

2. **File-Level View**
   - List all indexed files
   - See chunks per file
   - View chunk content

3. **Embedding Visualization**
   - 2D/3D projection of embeddings (t-SNE or UMAP)
   - Similarity heatmaps
   - Query-to-result visualization

4. **Search Space View**
   - Show query embedding
   - Show matched chunks
   - Visualize distances/relevance

### Implementation

#### Backend Endpoint

```python
# src/routes/vector_db.py
from fastapi import APIRouter
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

router = APIRouter()

@router.get("/vector-db/stats")
async def get_vector_db_stats():
    """Get vector database statistics"""
    stats = {
        "collections": {},
        "total_chunks": 0
    }
    
    for name, collection in vector_db_service.collections.items():
        count = collection.count()
        stats["collections"][name] = {
            "count": count,
            "files": {}
        }
        stats["total_chunks"] += count
        
        # Get all documents with metadata
        results = collection.get(include=["metadatas"])
        
        # Group by file
        if results and results.get("metadatas"):
            for metadata in results["metadatas"]:
                file_name = metadata.get("file_name", "Unknown")
                if file_name not in stats["collections"][name]["files"]:
                    stats["collections"][name]["files"][file_name] = 0
                stats["collections"][name]["files"][file_name] += 1
    
    return stats

@router.get("/vector-db/embeddings")
async def get_embeddings_visualization(collection: str = "documents", limit: int = 100):
    """Get embeddings for visualization (reduced to 2D)"""
    if collection not in vector_db_service.collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    col = vector_db_service.collections[collection]
    
    # Get embeddings
    results = col.get(
        limit=limit,
        include=["embeddings", "metadatas", "documents"]
    )
    
    if not results or not results.get("embeddings"):
        return {"points": [], "labels": []}
    
    # Reduce dimensions to 2D using t-SNE
    embeddings = np.array(results["embeddings"])
    if len(embeddings) > 1:
        tsne = TSNE(n_components=2, random_state=42)
        embeddings_2d = tsne.fit_transform(embeddings)
    else:
        embeddings_2d = embeddings[:, :2]  # Just take first 2 dims
    
    # Prepare data for visualization
    points = []
    for i, (x, y) in enumerate(embeddings_2d):
        points.append({
            "x": float(x),
            "y": float(y),
            "file": results["metadatas"][i].get("file_name", "Unknown"),
            "content": results["documents"][i][:100] + "...",  # Preview
            "chunk_index": results["metadatas"][i].get("chunk_index", 0)
        })
    
    return {"points": points}

@router.post("/vector-db/search-visualization")
async def visualize_search(query: str):
    """Visualize a search query and its results"""
    # Generate query embedding
    query_embedding = await ollama_service.generate_embedding(query)
    
    # Search all collections
    results = vector_db_service.search_all_collections(
        query_embeddings=[query_embedding],
        n_results=10
    )
    
    # Format for visualization
    return {
        "query": query,
        "results": [
            {
                "file": r["metadata"].get("file_name"),
                "content": r["document"][:200],
                "distance": r["distance"],
                "relevance": max(0, 100 - (r["distance"] / 10))
            }
            for r in results
        ]
    }
```

#### Frontend Visualization Page

```tsx
// app/vector-db/page.tsx
"use client"

import { useState, useEffect } from "react"
import useSWR from "swr"
import { Scatter } from "react-chartjs-2"
import { Card } from "@/components/ui/card"

export default function VectorDBPage() {
  const { data: stats } = useSWR("/api/vector-db/stats")
  const { data: embeddings } = useSWR("/api/vector-db/embeddings?collection=documents&limit=200")

  // Prepare chart data
  const chartData = {
    datasets: embeddings?.points?.reduce((acc: any, point: any) => {
      const fileName = point.file
      if (!acc.find((d: any) => d.label === fileName)) {
        acc.push({
          label: fileName,
          data: [],
          backgroundColor: `hsl(${Math.random() * 360}, 70%, 50%)`,
        })
      }
      const dataset = acc.find((d: any) => d.label === fileName)
      dataset.data.push({ x: point.x, y: point.y, content: point.content })
      return acc
    }, []) || []
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Vector Database Visualization</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {stats && Object.entries(stats.collections).map(([name, data]: any) => (
          <Card key={name} className="p-6">
            <h3 className="text-lg font-semibold capitalize">{name}</h3>
            <p className="text-3xl font-bold mt-2">{data.count}</p>
            <p className="text-sm text-muted-foreground">chunks</p>
          </Card>
        ))}
      </div>

      {/* Embedding Scatter Plot */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Embedding Space (t-SNE)</h2>
        <div className="h-[600px]">
          <Scatter
            data={chartData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                tooltip: {
                  callbacks: {
                    label: (context: any) => {
                      const point = context.raw
                      return point.content || ""
                    }
                  }
                }
              }
            }}
          />
        </div>
      </Card>

      {/* File List */}
      <Card className="p-6 mt-8">
        <h2 className="text-xl font-semibold mb-4">Indexed Files</h2>
        {stats && Object.entries(stats.collections).map(([collName, collData]: any) => (
          <div key={collName} className="mb-4">
            <h3 className="font-semibold capitalize mb-2">{collName}</h3>
            <div className="space-y-2">
              {Object.entries(collData.files).map(([fileName, count]: any) => (
                <div key={fileName} className="flex justify-between items-center p-2 bg-muted rounded">
                  <span>{fileName}</span>
                  <Badge>{count} chunks</Badge>
                </div>
              ))}
            </div>
          </div>
        ))}
      </Card>
    </div>
  )
}
```

**Required Dependencies**:
```bash
# Backend
pip install scikit-learn  # For t-SNE/PCA

# Frontend
npm install react-chartjs-2 chart.js
```

---

## Summary & Next Steps

### 1. ✅ Dynamic Model Selection
- **Complexity**: Medium
- **Time**: 2-3 hours
- **Priority**: High
- **Next**: Implement backend endpoints first, then frontend UI

### 2. ✅ Docker Deployment
- **Complexity**: High
- **Time**: 4-6 hours
- **Priority**: High
- **Next**: Start with docker-compose.yml, test locally

### 3. ✅ Vector DB Visualization
- **Complexity**: Medium-High
- **Time**: 3-4 hours
- **Priority**: Medium
- **Next**: Backend stats endpoint, then visualization page

Would you like me to start implementing any of these features? I'd recommend this order:

1. **Start with Docker** (most impactful for portability)
2. **Add Model Selection** (great UX improvement)
3. **Add DB Visualization** (useful for debugging)

Let me know which one you'd like me to tackle first!
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
