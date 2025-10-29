from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
import os
import uuid
from datetime import datetime
import logging
import shutil

from src.models.schemas import FileMetadata, FileDetailResponse
from src.services.database_service import db_service
from src.services.vector_db_service import vector_db_service
from src.services.file_processor import file_processor
from src.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/knowledge-base/stats")
async def get_stats():
    """Get knowledge base statistics"""
    try:
        stats = db_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base")
async def get_knowledge_base(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get all files in knowledge base"""
    try:
        files = db_service.get_all_files(file_type=type, status=status)
        
        # Filter by search term if provided
        if search:
            files = [f for f in files if search.lower() in f["name"].lower()]
        
        return {
            "files": files,
            "total": len(files)
        }
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-base")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and process files"""
    try:
        uploaded_files = []
        
        for file in files:
            # Generate unique ID
            file_id = str(uuid.uuid4())
            
            # Determine file type
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.pdf', '.docx', '.txt']:
                file_type = "document"
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                file_type = "image"
            elif ext in ['.mp3', '.wav', '.m4a', '.flac']:
                file_type = "audio"
            else:
                continue  # Skip unsupported files
            
            # Save file
            file_path = os.path.join(settings.WATCH_DIRECTORY, f"{file_id}_{file.filename}")
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Add to database
            file_data = {
                "id": file_id,
                "name": file.filename,
                "type": file_type,
                "size": file_size,
                "path": file_path,
                "uploaded_at": datetime.now().isoformat(),
                "status": "processing",
                "chunks": 0,
                "metadata": {}
            }
            
            db_service.add_file(file_data)
            
            uploaded_files.append({
                "id": file_id,
                "name": file.filename,
                "status": "processing"
            })
            
            # Process file asynchronously (in background)
            try:
                result = await file_processor.process_file(file_path, file_id, file_type)
                
                if result["success"]:
                    db_service.update_file_status(
                        file_id, 
                        "indexed", 
                        result["chunks"]
                    )
                    
                    # Update metadata if available
                    if result.get("metadata"):
                        file_record = db_service.get_file(file_id)
                        if file_record:
                            file_record["metadata"].update(result["metadata"])
                else:
                    db_service.update_file_status(file_id, "error", 0)
                    logger.error(f"Error processing file {file_id}: {result.get('error')}")
                    
            except Exception as e:
                db_service.update_file_status(file_id, "error", 0)
                logger.error(f"Error processing file {file_id}: {e}")
        
        return {
            "success": True,
            "files": uploaded_files
        }
        
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/{file_id}")
async def get_file_detail(file_id: str):
    """Get detailed information about a specific file"""
    try:
        file = db_service.get_file(file_id)
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get chunks from vector database
        # TODO: Implement chunk retrieval from vector database
        
        return {
            **file,
            "preview": None,
            "chunks_detail": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge-base/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its embeddings"""
    try:
        file = db_service.get_file(file_id)
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine collection based on file type
        collection_map = {
            "document": "documents",
            "image": "images",
            "audio": "audio"
        }
        
        collection_name = collection_map.get(file["type"])
        
        # Delete from vector database
        if collection_name:
            vector_db_service.delete_by_file_id(collection_name, file_id)
        
        # Delete file from disk
        if os.path.exists(file["path"]):
            os.remove(file["path"])
        
        # Delete from database
        db_service.delete_file(file_id)
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/stats")
async def get_stats():
    """Get knowledge base statistics"""
    try:
        stats = db_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/{file_id}/download")
async def download_file(file_id: str):
    """Download a file"""
    try:
        from fastapi.responses import FileResponse
        
        file = db_service.get_file(file_id)
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if not os.path.exists(file["path"]):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=file["path"],
            filename=file["name"],
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/{file_id}/view")
async def view_file(file_id: str):
    """View a file inline (no download)"""
    try:
        from fastapi.responses import FileResponse
        import mimetypes
        
        file = db_service.get_file(file_id)
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if not os.path.exists(file["path"]):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Guess MIME type from file extension
        mime_type, _ = mimetypes.guess_type(file["path"])
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        return FileResponse(
            path=file["path"],
            filename=file["name"],
            media_type=mime_type,
            headers={"Content-Disposition": f"inline; filename={file['name']}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
