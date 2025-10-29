"""
System Indexer API Routes

API endpoints for managing system-wide file indexing.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from src.services.system_indexer import system_indexer
from src.services.fs_watcher import fs_watcher
from src.services.database_service import db_service
from src.services.vector_db_service import vector_db_service

router = APIRouter()
logger = logging.getLogger(__name__)


# Request/Response Models
class AddPathRequest(BaseModel):
    path: str


class RemovePathRequest(BaseModel):
    path: str


class AddExclusionRequest(BaseModel):
    pattern: str


class RemoveExclusionRequest(BaseModel):
    pattern: str


class StartIndexingRequest(BaseModel):
    max_files: Optional[int] = None


# Permission Management Endpoints

@router.get("/system-indexer/permitted-paths")
async def get_permitted_paths():
    """Get all permitted paths for system-wide indexing"""
    try:
        paths = system_indexer.get_permitted_paths()
        return {
            "success": True,
            "paths": paths,
            "count": len(paths)
        }
    except Exception as e:
        logger.error(f"Error getting permitted paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-indexer/permitted-paths")
async def add_permitted_path(request: AddPathRequest):
    """Add a path to permitted indexing paths"""
    try:
        result = system_indexer.add_permitted_path(request.path)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Update file system watcher if monitoring is active
        if fs_watcher.monitoring:
            fs_watcher.update_watched_paths()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding permitted path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/system-indexer/permitted-paths")
async def remove_permitted_path(request: RemovePathRequest):
    """Remove a path from permitted indexing paths"""
    try:
        result = system_indexer.remove_permitted_path(request.path)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Update file system watcher if monitoring is active
        if fs_watcher.monitoring:
            fs_watcher.update_watched_paths()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing permitted path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Exclusion Pattern Management

@router.get("/system-indexer/exclusions")
async def get_exclusion_patterns():
    """Get all exclusion patterns"""
    try:
        patterns = system_indexer.get_exclusion_patterns()
        return {
            "success": True,
            "patterns": patterns
        }
    except Exception as e:
        logger.error(f"Error getting exclusion patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-indexer/exclusions")
async def add_exclusion_pattern(request: AddExclusionRequest):
    """Add an exclusion pattern"""
    try:
        result = system_indexer.add_exclusion_pattern(request.pattern)
        return result
    except Exception as e:
        logger.error(f"Error adding exclusion pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/system-indexer/exclusions")
async def remove_exclusion_pattern(request: RemoveExclusionRequest):
    """Remove an exclusion pattern"""
    try:
        result = system_indexer.remove_exclusion_pattern(request.pattern)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing exclusion pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Indexing Control Endpoints

@router.post("/system-indexer/start")
async def start_system_indexing(request: StartIndexingRequest = Body(default=StartIndexingRequest())):
    """Start system-wide indexing of permitted paths"""
    try:
        result = await system_indexer.start_system_indexing(max_files=request.max_files)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting system indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-indexer/stop")
async def stop_system_indexing():
    """Stop ongoing system-wide indexing"""
    try:
        result = system_indexer.stop_indexing()
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping system indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-indexer/status")
async def get_indexing_status():
    """Get current indexing status and statistics"""
    try:
        status = system_indexer.get_indexing_status()
        return {
            "success": True,
            **status
        }
    except Exception as e:
        logger.error(f"Error getting indexing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# File System Monitoring Endpoints

@router.post("/system-indexer/monitoring/start")
async def start_file_monitoring():
    """Start real-time file system monitoring"""
    try:
        result = fs_watcher.start_monitoring()
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting file monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-indexer/monitoring/stop")
async def stop_file_monitoring():
    """Stop real-time file system monitoring"""
    try:
        result = fs_watcher.stop_monitoring()
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping file monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-indexer/monitoring/status")
async def get_monitoring_status():
    """Get file system monitoring status"""
    try:
        status = fs_watcher.get_monitoring_status()
        return {
            "success": True,
            **status
        }
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Information Endpoints

@router.get("/system-indexer/supported-extensions")
async def get_supported_extensions():
    """Get list of supported file extensions"""
    try:
        extensions = sorted(list(system_indexer.SUPPORTED_EXTENSIONS))
        return {
            "success": True,
            "extensions": extensions,
            "count": len(extensions)
        }
    except Exception as e:
        logger.error(f"Error getting supported extensions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system-indexer/cleanup")
async def cleanup_failed_files():
    """Clean up files stuck in processing or failed status"""
    try:
        from src.services.database_service import db_service
        
        # Get stuck files
        processing_files = db_service.get_all_files(status="processing")
        failed_files = db_service.get_all_files(status="failed")
        
        all_stuck_files = processing_files + failed_files
        deleted_count = 0
        
        # Delete all stuck files (processing + failed)
        for file in all_stuck_files:
            try:
                file_id = file["id"]
                
                # Delete from vector database
                vector_db_service.delete_by_file_id("files", file_id)
                
                # Delete from SQLite database
                if db_service.delete_file(file_id):
                    deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting file {file.get('name', file_id)}: {e}")
        
        logger.info(f"Deleted {deleted_count} stuck files ({len(processing_files)} processing, {len(failed_files)} failed)")
        
        return {
            "success": True,
            "deleted": deleted_count,
            "processing_count": len(processing_files),
            "failed_count": len(failed_files),
            "message": f"Deleted {deleted_count} stuck files"
        }
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")
        raise HTTPException(status_code=500, detail=str(e))
