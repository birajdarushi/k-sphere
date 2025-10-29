from fastapi import APIRouter, HTTPException
import psutil
import logging
from datetime import datetime

from src.services.ollama_service import ollama_service
from src.services.vector_db_service import vector_db_service
from src.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/system-status")
async def get_system_status():
    """Get system health status"""
    try:
        # Check Ollama status
        ollama_health = await ollama_service.check_health()
        
        # Check if required models are available
        llm_available = await ollama_service.check_model_exists(settings.OLLAMA_LLM_MODEL)
        embedding_available = await ollama_service.check_model_exists(settings.OLLAMA_EMBEDDING_MODEL)
        
        ollama_status = {
            "status": ollama_health.get("status", "error"),
            "model": settings.OLLAMA_LLM_MODEL,
            "version": ollama_health.get("version", "unknown")
        }
        
        # Check vector database status
        try:
            total_chunks = vector_db_service.get_total_chunks()
            vector_db_status = {
                "status": "connected",
                "collections": len(vector_db_service.collections)
            }
        except Exception as e:
            logger.error(f"Vector DB check failed: {e}")
            vector_db_status = {
                "status": "disconnected",
                "collections": 0
            }
        
        # Check Whisper status (always available if imported)
        whisper_status = {
            "status": "available",
            "model": "base"
        }
        
        # Embeddings status
        embeddings_status = {
            "status": "available" if embedding_available else "unavailable",
            "model": settings.OLLAMA_EMBEDDING_MODEL
        }
        
        # Get system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            "cpuUsage": cpu_percent,
            "memoryUsage": memory.percent,
            "diskSpace": disk.percent
        }
        
        # Determine overall status
        if ollama_status["status"] == "running" and vector_db_status["status"] == "connected":
            overall_status = "online"
        elif ollama_status["status"] == "error" or vector_db_status["status"] == "disconnected":
            overall_status = "offline"
        else:
            overall_status = "partial"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "ollama": ollama_status,
                "vectorDb": vector_db_status,
                "whisper": whisper_status,
                "embeddings": embeddings_status
            },
            "resources": resources
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings")
async def get_settings():
    """Get current system settings"""
    try:
        return {
            "general": {
                "watchDirectory": settings.WATCH_DIRECTORY,
                "autoIndex": False  # Not implemented yet
            },
            "processing": {
                "chunkSize": settings.CHUNK_SIZE,
                "chunkOverlap": settings.CHUNK_OVERLAP
            },
            "retrieval": {
                "topK": settings.TOP_K,
                "similarityThreshold": settings.SIMILARITY_THRESHOLD
            },
            "models": {
                "llm": settings.OLLAMA_LLM_MODEL,
                "embedding": settings.OLLAMA_EMBEDDING_MODEL,
                "whisper": "base"
            }
        }
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings")
async def update_settings(settings_data: dict):
    """Update system settings"""
    try:
        # TODO: Implement settings persistence
        # For now, just return the current settings
        return {
            "success": True,
            "settings": await get_settings()
        }
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingestion/trigger")
async def trigger_ingestion():
    """Manually trigger ingestion from watch directory"""
    try:
        import os
        
        files_found = 0
        watch_dir = settings.WATCH_DIRECTORY
        
        if os.path.exists(watch_dir):
            for filename in os.listdir(watch_dir):
                if not filename.startswith('.'):
                    files_found += 1
        
        return {
            "success": True,
            "filesFound": files_found,
            "message": f"Found {files_found} files in watch directory"
        }
        
    except Exception as e:
        logger.error(f"Error triggering ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
