"""
K-Sphere Debug Server
Separate server for vector database visualization and diagnostics
Runs on port 8001 (separate from main app on 8000)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import numpy as np
import logging

# Import services from main app
from src.services.vector_db_service import vector_db_service
from src.services.ollama_service import ollama_service
from src.services.database_service import db_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create debug app
app = FastAPI(
    title="K-Sphere Debug Server",
    description="Vector Database Visualization and Diagnostics",
    version="1.0.0"
)

# Configure CORS (allow access from anywhere for debug purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    """Model for search visualization request"""
    query: str
    limit: int = 10


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "K-Sphere Debug Server",
        "version": "1.0.0",
        "description": "Vector DB Visualization and Diagnostics",
        "endpoints": {
            "stats": "/stats",
            "collections": "/collections",
            "embeddings": "/embeddings?collection=documents&limit=100",
            "search_viz": "/search-viz (POST)",
            "ui": "/ui"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check vector DB
        collections_status = {}
        for name, collection in vector_db_service.collections.items():
            try:
                count = collection.count()
                collections_status[name] = {"status": "ok", "count": count}
            except Exception as e:
                collections_status[name] = {"status": "error", "error": str(e)}
        
        # Check Ollama
        ollama_health = await ollama_service.check_health()
        
        return {
            "status": "healthy",
            "vector_db": collections_status,
            "ollama": ollama_health.get("status", "unknown")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/stats")
async def get_vector_db_stats():
    """
    Get comprehensive vector database statistics
    
    Returns:
    - Collection names and counts
    - Files per collection
    - Chunks per file
    - Total embeddings
    """
    try:
        stats = {
            "collections": {},
            "total_chunks": 0,
            "total_files": 0
        }
        
        for name, collection in vector_db_service.collections.items():
            try:
                count = collection.count()
                stats["total_chunks"] += count
                
                stats["collections"][name] = {
                    "count": count,
                    "files": {}
                }
                
                # Get all documents with metadata
                if count > 0:
                    results = collection.get(include=["metadatas"])
                    
                    # Group by file
                    if results and results.get("metadatas"):
                        file_map = {}
                        for metadata in results["metadatas"]:
                            file_name = metadata.get("file_name", "Unknown")
                            file_id = metadata.get("file_id", "unknown")
                            
                            if file_name not in file_map:
                                file_map[file_name] = {
                                    "file_id": file_id,
                                    "chunks": 0,
                                    "type": metadata.get("file_type", "unknown")
                                }
                            file_map[file_name]["chunks"] += 1
                        
                        stats["collections"][name]["files"] = file_map
                        stats["total_files"] += len(file_map)
            
            except Exception as e:
                logger.error(f"Error getting stats for collection {name}: {e}")
                stats["collections"][name] = {
                    "error": str(e),
                    "count": 0,
                    "files": {}
                }
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collections")
async def get_collections():
    """
    List all collections with basic info
    """
    try:
        collections = []
        
        for name, collection in vector_db_service.collections.items():
            try:
                count = collection.count()
                collections.append({
                    "name": name,
                    "count": count,
                    "status": "ok"
                })
            except Exception as e:
                collections.append({
                    "name": name,
                    "count": 0,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "collections": collections
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/embeddings")
async def get_embeddings_for_visualization(
    collection: str = "documents",
    limit: int = 100,
    projection: str = "none"  # "none", "pca", "tsne" - can add later
):
    """
    Get embeddings from a collection
    
    Args:
    - collection: Collection name (documents, images, audio)
    - limit: Max number of embeddings to return
    - projection: Dimensionality reduction method (future use)
    
    Returns raw embeddings with metadata for client-side visualization
    """
    try:
        if collection not in vector_db_service.collections:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection}' not found"
            )
        
        col = vector_db_service.collections[collection]
        
        # Get embeddings with metadata
        results = col.get(
            limit=limit,
            include=["embeddings", "metadatas", "documents"]
        )
        
        if not results or not results.get("embeddings"):
            return {
                "success": True,
                "collection": collection,
                "points": [],
                "count": 0
            }
        
        # Format for client
        points = []
        for i, embedding in enumerate(results["embeddings"]):
            metadata = results["metadatas"][i] if results.get("metadatas") else {}
            document = results["documents"][i] if results.get("documents") else ""
            
            points.append({
                "embedding": embedding,  # Full embedding vector
                "dimensions": len(embedding),
                "file": metadata.get("file_name", "Unknown"),
                "file_id": metadata.get("file_id", "unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "content_preview": document[:200] + "..." if len(document) > 200 else document,
                "type": metadata.get("file_type", "unknown")
            })
        
        return {
            "success": True,
            "collection": collection,
            "points": points,
            "count": len(points),
            "dimensions": len(results["embeddings"][0]) if results["embeddings"] else 0
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search-viz")
async def visualize_search(request: SearchRequest):
    """
    Visualize a search query and its results
    
    Args:
    - query: Search query text
    - limit: Number of results to return
    
    Returns:
    - Query embedding
    - Search results with distances
    - Relevance scores
    """
    try:
        # Generate query embedding
        query_embedding = await ollama_service.generate_embedding(request.query)
        
        # Search all collections
        results = vector_db_service.search_all_collections(
            query_embeddings=[query_embedding],
            n_results=request.limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            metadata = result.get("metadata", {})
            
            # Calculate relevance score (inverse of distance, normalized to 0-100)
            distance = result.get("distance", 999)
            relevance = max(0, 100 - (distance * 10))  # Adjust multiplier as needed
            
            formatted_results.append({
                "file": metadata.get("file_name", "Unknown"),
                "file_id": metadata.get("file_id", "unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "content": result.get("document", "")[:300],
                "distance": round(distance, 4),
                "relevance": round(relevance, 2),
                "collection": result.get("collection", "unknown"),
                "type": metadata.get("file_type", "unknown")
            })
        
        return {
            "success": True,
            "query": request.query,
            "query_embedding_dims": len(query_embedding),
            "results": formatted_results,
            "result_count": len(formatted_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def get_indexed_files():
    """
    Get list of all indexed files across collections
    """
    try:
        all_files = db_service.get_all_sources()
        
        # Format for response
        files = []
        for file in all_files:
            files.append({
                "id": file.get("id"),
                "name": file.get("file_name"),
                "type": file.get("file_type"),
                "size": file.get("file_size"),
                "path": file.get("file_path"),
                "chunks": file.get("chunk_count", 0),
                "uploaded_at": file.get("uploaded_at"),
                "processed_at": file.get("processed_at")
            })
        
        return {
            "success": True,
            "files": files,
            "total": len(files)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ui", response_class=HTMLResponse)
async def serve_ui():
    """
    Serve a simple HTML UI for vector DB visualization
    This is a basic dashboard - can be replaced with a full React app
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>K-Sphere Debug Console</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #0f0f0f;
                color: #e0e0e0;
                padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 {
                font-size: 2rem;
                margin-bottom: 10px;
                background: linear-gradient(90deg, #60a5fa, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .subtitle { color: #999; margin-bottom: 30px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card {
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 20px;
            }
            .card h3 { color: #60a5fa; margin-bottom: 15px; font-size: 1.1rem; }
            .stat { font-size: 2.5rem; font-weight: bold; color: #fff; }
            .label { color: #999; font-size: 0.9rem; margin-top: 5px; }
            .file-list {
                max-height: 400px;
                overflow-y: auto;
                background: #0a0a0a;
                border-radius: 6px;
                padding: 10px;
            }
            .file-item {
                background: #1a1a1a;
                padding: 12px;
                margin-bottom: 8px;
                border-radius: 6px;
                border-left: 3px solid #60a5fa;
            }
            .file-name { font-weight: 600; color: #fff; margin-bottom: 4px; }
            .file-meta { font-size: 0.85rem; color: #999; }
            button {
                background: #60a5fa;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                margin-right: 10px;
            }
            button:hover { background: #3b82f6; }
            .search-section {
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
            }
            input {
                background: #0a0a0a;
                border: 1px solid #333;
                color: #fff;
                padding: 10px;
                border-radius: 6px;
                width: 100%;
                max-width: 500px;
                margin-right: 10px;
            }
            .result-item {
                background: #0a0a0a;
                padding: 12px;
                margin-top: 10px;
                border-radius: 6px;
                border-left: 3px solid #a78bfa;
            }
            .loading { color: #60a5fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 K-Sphere Debug Console</h1>
            <p class="subtitle">Vector Database Visualization & Diagnostics</p>
            
            <div class="grid">
                <div class="card">
                    <h3>Total Chunks</h3>
                    <div class="stat" id="total-chunks">-</div>
                    <div class="label">Indexed embeddings</div>
                </div>
                <div class="card">
                    <h3>Total Files</h3>
                    <div class="stat" id="total-files">-</div>
                    <div class="label">Processed documents</div>
                </div>
                <div class="card">
                    <h3>Collections</h3>
                    <div class="stat" id="total-collections">-</div>
                    <div class="label">Active collections</div>
                </div>
            </div>

            <div class="card">
                <h3>Collections Overview</h3>
                <div id="collections-list"></div>
            </div>

            <div class="card" style="margin-top: 20px;">
                <h3>Indexed Files</h3>
                <div class="file-list" id="files-list"></div>
            </div>

            <div class="search-section">
                <h3 style="color: #a78bfa; margin-bottom: 15px;">Search Visualization</h3>
                <input type="text" id="search-query" placeholder="Enter search query...">
                <button onclick="searchViz()">Search</button>
                <div id="search-results"></div>
            </div>
        </div>

        <script>
            async function loadStats() {
                try {
                    const response = await fetch('/stats');
                    const data = await response.json();
                    
                    document.getElementById('total-chunks').textContent = data.stats.total_chunks;
                    document.getElementById('total-files').textContent = data.stats.total_files;
                    document.getElementById('total-collections').textContent = Object.keys(data.stats.collections).length;
                    
                    // Show collections
                    const collectionsHtml = Object.entries(data.stats.collections).map(([name, info]) => `
                        <div class="file-item">
                            <div class="file-name">${name}</div>
                            <div class="file-meta">${info.count} chunks | ${Object.keys(info.files).length} files</div>
                        </div>
                    `).join('');
                    document.getElementById('collections-list').innerHTML = collectionsHtml;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            async function loadFiles() {
                try {
                    const response = await fetch('/files');
                    const data = await response.json();
                    
                    const filesHtml = data.files.map(file => `
                        <div class="file-item">
                            <div class="file-name">${file.name}</div>
                            <div class="file-meta">
                                ${file.type} | ${(file.size / 1024).toFixed(2)} KB | ${file.chunks} chunks
                            </div>
                        </div>
                    `).join('');
                    document.getElementById('files-list').innerHTML = filesHtml;
                } catch (error) {
                    console.error('Error loading files:', error);
                }
            }

            async function searchViz() {
                const query = document.getElementById('search-query').value;
                if (!query) return;
                
                const resultsDiv = document.getElementById('search-results');
                resultsDiv.innerHTML = '<p class="loading">Searching...</p>';
                
                try {
                    const response = await fetch('/search-viz', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query, limit: 5 })
                    });
                    const data = await response.json();
                    
                    const resultsHtml = data.results.map(result => `
                        <div class="result-item">
                            <div class="file-name">${result.file}</div>
                            <div class="file-meta">
                                Relevance: ${result.relevance}% | Distance: ${result.distance} | ${result.type}
                            </div>
                            <div style="color: #ccc; margin-top: 8px; font-size: 0.9rem;">
                                ${result.content}
                            </div>
                        </div>
                    `).join('');
                    resultsDiv.innerHTML = resultsHtml;
                } catch (error) {
                    resultsDiv.innerHTML = '<p style="color: #f87171;">Error: ' + error.message + '</p>';
                }
            }

            // Load data on page load
            loadStats();
            loadFiles();

            // Refresh every 10 seconds
            setInterval(() => {
                loadStats();
                loadFiles();
            }, 10000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting K-Sphere Debug Server on port 8001")
    logger.info("Access UI at: http://localhost:8001/ui")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
