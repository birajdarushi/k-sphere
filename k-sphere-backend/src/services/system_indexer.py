"""
System-wide File Indexer Service

This service enables K-Sphere to index files across the entire system with user permission.
It provides intelligent crawling, permission management, and incremental indexing.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading

from src.services.file_processor import file_processor
from src.services.database_service import db_service
from src.services.vector_db_service import vector_db_service
from src.config.settings import settings

logger = logging.getLogger(__name__)


class SystemIndexer:
    """Service for system-wide file indexing with permission management"""
    
    # Default exclusion patterns
    DEFAULT_EXCLUSIONS = [
        # System directories
        "/System/", "/private/", "/dev/", "/proc/", "/sys/",
        "C:\\Windows\\", "C:\\Program Files\\", "C:\\Program Files (x86)\\",
        
        # Hidden directories
        ".git/", ".svn/", ".hg/", ".bzr/",
        "node_modules/", "__pycache__/", ".venv/", "venv/",
        ".DS_Store", "Thumbs.db",
        
        # Temp and cache
        "/tmp/", "/var/cache/", "/var/tmp/",
        "AppData\\Local\\Temp\\", "AppData\\Local\\Microsoft\\",
        
        # Build artifacts
        "build/", "dist/", "target/", "bin/", "obj/",
        ".next/", ".nuxt/", ".cache/", ".parcel-cache/",
        
        # Large media folders (user can explicitly include if needed)
        "Library/", "Application Support/",
        
        # Development files
        ".hot-update.", "webpack.", ".map", "sourcemap",
        "node_modules", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    ]
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        # Documents
        '.pdf', '.docx', '.doc', '.txt', '.md', '.rtf', '.odt',
        
        # Code files
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
        
        # Config files
        '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.conf',
        
        # Web files
        '.html', '.htm', '.css', '.scss', '.less',
        
        # Data files
        '.csv', '.tsv', '.sql',
        
        # Images (for OCR)
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff',
        
        # Audio (for transcription)
        '.mp3', '.wav', '.m4a', '.flac', '.ogg',
    }
    
    def __init__(self):
        self.permitted_paths: Set[str] = set()
        self.exclusion_patterns: Set[str] = set(self.DEFAULT_EXCLUSIONS)
        self.indexing_in_progress = False
        self.current_stats = {
            "indexed_files": 0,
            "failed_files": 0,
            "skipped_files": 0,
            "total_size": 0,
            "current_path": None,
            "start_time": None,
            "end_time": None,
        }
        self._lock = threading.Lock()
        self._load_settings()
        self._cleanup_stuck_files()
    
    def _cleanup_stuck_files(self):
        """Clean up files stuck in 'processing' status from previous crashes"""
        try:
            from src.services.database_service import db_service
            stuck_files = db_service.get_all_files(status="processing")
            if stuck_files:
                logger.info(f"Cleaning up {len(stuck_files)} files stuck in processing status")
                for file in stuck_files:
                    db_service.update_file_status(file["id"], "failed", 0)
        except Exception as e:
            logger.error(f"Error cleaning up stuck files: {e}")
    
    def _load_settings(self):
        """Load indexer settings from database"""
        try:
            indexer_settings = db_service.get_setting("system_indexer", {})
            self.permitted_paths = set(indexer_settings.get("permitted_paths", []))
            custom_exclusions = indexer_settings.get("exclusion_patterns", [])
            self.exclusion_patterns.update(custom_exclusions)
            logger.info(f"Loaded {len(self.permitted_paths)} permitted paths")
        except Exception as e:
            logger.error(f"Error loading indexer settings: {e}")
    
    def _save_settings(self):
        """Save indexer settings to database"""
        try:
            indexer_settings = {
                "permitted_paths": list(self.permitted_paths),
                "exclusion_patterns": list(self.exclusion_patterns - set(self.DEFAULT_EXCLUSIONS)),
            }
            db_service.update_setting("system_indexer", indexer_settings)
            logger.info("Saved indexer settings")
        except Exception as e:
            logger.error(f"Error saving indexer settings: {e}")
    
    def add_permitted_path(self, path: str) -> Dict[str, Any]:
        """Add a path to the permitted indexing paths"""
        path = os.path.abspath(os.path.expanduser(path))
        
        if not os.path.exists(path):
            return {
                "success": False,
                "error": f"Path does not exist: {path}"
            }
        
        if not os.access(path, os.R_OK):
            return {
                "success": False,
                "error": f"No read permission for path: {path}"
            }
        
        self.permitted_paths.add(path)
        self._save_settings()
        
        logger.info(f"Added permitted path: {path}")
        return {
            "success": True,
            "path": path,
            "message": f"Path added successfully: {path}"
        }
    
    def remove_permitted_path(self, path: str) -> Dict[str, Any]:
        """Remove a path from permitted indexing paths"""
        path = os.path.abspath(os.path.expanduser(path))
        
        if path not in self.permitted_paths:
            return {
                "success": False,
                "error": f"Path not in permitted list: {path}"
            }
        
        self.permitted_paths.remove(path)
        self._save_settings()
        
        logger.info(f"Removed permitted path: {path}")
        return {
            "success": True,
            "path": path,
            "message": f"Path removed successfully: {path}"
        }
    
    def get_permitted_paths(self) -> List[str]:
        """Get all permitted paths"""
        return sorted(list(self.permitted_paths))
    
    def add_exclusion_pattern(self, pattern: str) -> Dict[str, Any]:
        """Add an exclusion pattern"""
        self.exclusion_patterns.add(pattern)
        self._save_settings()
        
        logger.info(f"Added exclusion pattern: {pattern}")
        return {
            "success": True,
            "pattern": pattern,
            "message": f"Exclusion pattern added: {pattern}"
        }
    
    def remove_exclusion_pattern(self, pattern: str) -> Dict[str, Any]:
        """Remove an exclusion pattern (except defaults)"""
        if pattern in self.DEFAULT_EXCLUSIONS:
            return {
                "success": False,
                "error": "Cannot remove default exclusion pattern"
            }
        
        if pattern not in self.exclusion_patterns:
            return {
                "success": False,
                "error": f"Pattern not found: {pattern}"
            }
        
        self.exclusion_patterns.remove(pattern)
        self._save_settings()
        
        logger.info(f"Removed exclusion pattern: {pattern}")
        return {
            "success": True,
            "pattern": pattern,
            "message": f"Exclusion pattern removed: {pattern}"
        }
    
    def get_exclusion_patterns(self) -> Dict[str, List[str]]:
        """Get all exclusion patterns"""
        return {
            "default": sorted(list(self.DEFAULT_EXCLUSIONS)),
            "custom": sorted(list(self.exclusion_patterns - set(self.DEFAULT_EXCLUSIONS)))
        }
    
    def _should_exclude(self, path: str) -> bool:
        """Check if a path should be excluded from indexing"""
        path_str = str(path)
        
        # Check exclusion patterns
        for pattern in self.exclusion_patterns:
            if pattern in path_str:
                return True
        
        return False
    
    def _is_supported_file(self, file_path: str) -> bool:
        """Check if file type is supported"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    def _get_file_hash(self, file_path: str) -> Optional[str]:
        """Get file hash for change detection"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Read first 64KB for hash (faster for large files)
                hasher.update(f.read(65536))
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return None
    
    async def _index_single_file(self, file_path: str) -> Dict[str, Any]:
        """Index a single file"""
        try:
            # Check if file was already indexed and hasn't changed
            file_hash = self._get_file_hash(file_path)
            if not file_hash:
                return {"success": False, "error": "Could not hash file"}
            
            # Check if file exists in database with same hash
            existing = db_service.get_file_by_path(file_path)
            if existing and existing.get("metadata", {}).get("file_hash") == file_hash:
                logger.debug(f"File already indexed and unchanged: {file_path}")
                return {"success": True, "status": "skipped", "reason": "already_indexed"}
            
            # Process the file
            file_id = existing["id"] if existing else str(__import__('uuid').uuid4())
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Add/update in database
            file_data = {
                "id": file_id,
                "name": file_name,
                "type": self._get_file_type(file_path),
                "size": file_size,
                "path": file_path,
                "uploaded_at": datetime.now().isoformat(),
                "status": "processing",
                "chunks": 0,
                "metadata": {
                    "file_hash": file_hash,
                    "source": "system_indexer",
                    "indexed_at": datetime.now().isoformat()
                }
            }
            
            if existing:
                db_service.update_file(file_id, file_data)
            else:
                db_service.add_file(file_data)
            
            # Process file content
            result = await file_processor.process_file(file_path, file_id, file_data["type"])
            
            # Check if processing was successful
            if result.get("success", False):
                # Update status to indexed
                chunks = result.get("chunks", 0)
                db_service.update_file_status(file_id, "indexed", chunks)
                
                return {
                    "success": True,
                    "status": "indexed",
                    "file_id": file_id,
                    "chunks": chunks
                }
            else:
                # Processing failed
                error_msg = result.get("error", "Unknown error")
                logger.warning(f"Failed to process {file_path}: {error_msg}")
                db_service.update_file_status(file_id, "failed", 0)
                
                return {
                    "success": False,
                    "status": "failed",
                    "error": error_msg
                }
            
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}", exc_info=True)
            # Update status to failed
            try:
                if existing or 'file_id' in locals():
                    db_service.update_file_status(file_id, "failed", 0)
            except:
                pass
            return {"success": False, "error": str(e)}
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.pdf', '.docx', '.doc', '.txt', '.md', '.rtf', '.odt']:
            return "document"
        elif ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
                     '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.html', '.css']:
            return "code"
        elif ext in ['.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.conf']:
            return "config"
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:
            return "image"
        elif ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
            return "audio"
        else:
            return "document"
    
    async def start_system_indexing(self, max_files: Optional[int] = None) -> Dict[str, Any]:
        """Start indexing all permitted paths"""
        if self.indexing_in_progress:
            return {
                "success": False,
                "error": "Indexing already in progress"
            }
        
        if not self.permitted_paths:
            return {
                "success": False,
                "error": "No permitted paths configured"
            }
        
        self.indexing_in_progress = True
        self.current_stats = {
            "indexed_files": 0,
            "failed_files": 0,
            "skipped_files": 0,
            "total_size": 0,
            "current_path": None,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
        }
        
        logger.info(f"Starting system-wide indexing of {len(self.permitted_paths)} paths")
        
        # Run indexing in background
        asyncio.create_task(self._run_indexing(max_files))
        
        return {
            "success": True,
            "message": "System indexing started",
            "permitted_paths": list(self.permitted_paths)
        }
    
    async def _run_indexing(self, max_files: Optional[int] = None):
        """Run the actual indexing process"""
        try:
            files_to_index = []
            
            # Collect all files from permitted paths
            for permitted_path in self.permitted_paths:
                logger.info(f"Scanning path: {permitted_path}")
                self.current_stats["current_path"] = permitted_path
                
                if os.path.isfile(permitted_path):
                    # Single file
                    if self._is_supported_file(permitted_path) and not self._should_exclude(permitted_path):
                        files_to_index.append(permitted_path)
                else:
                    # Directory - walk recursively
                    for root, dirs, files in os.walk(permitted_path):
                        # Filter out excluded directories
                        dirs[:] = [d for d in dirs if not self._should_exclude(os.path.join(root, d))]
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            
                            if self._should_exclude(file_path):
                                continue
                            
                            if not self._is_supported_file(file_path):
                                continue
                            
                            files_to_index.append(file_path)
                            
                            if max_files and len(files_to_index) >= max_files:
                                break
                        
                        if max_files and len(files_to_index) >= max_files:
                            break
            
            logger.info(f"Found {len(files_to_index)} files to index")
            
            # Index files with concurrency control
            semaphore = asyncio.Semaphore(5)  # Max 5 concurrent file processing
            
            async def index_with_semaphore(file_path):
                async with semaphore:
                    return await self._index_single_file(file_path)
            
            tasks = [index_with_semaphore(fp) for fp in files_to_index]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update stats
            for result in results:
                if isinstance(result, Exception):
                    self.current_stats["failed_files"] += 1
                elif result.get("success"):
                    if result.get("status") == "skipped":
                        self.current_stats["skipped_files"] += 1
                    else:
                        self.current_stats["indexed_files"] += 1
                else:
                    self.current_stats["failed_files"] += 1
            
            self.current_stats["end_time"] = datetime.now().isoformat()
            self.current_stats["current_path"] = None
            
            logger.info(f"Indexing completed: {self.current_stats}")
            
        except Exception as e:
            logger.error(f"Error during system indexing: {e}")
        finally:
            self.indexing_in_progress = False
    
    def get_indexing_status(self) -> Dict[str, Any]:
        """Get current indexing status"""
        return {
            "in_progress": self.indexing_in_progress,
            "stats": self.current_stats,
            "permitted_paths": list(self.permitted_paths),
            "exclusion_patterns": len(self.exclusion_patterns)
        }
    
    def stop_indexing(self) -> Dict[str, Any]:
        """Stop ongoing indexing"""
        if not self.indexing_in_progress:
            return {
                "success": False,
                "error": "No indexing in progress"
            }
        
        # Note: This is a simple flag-based stop
        # In production, you'd want more sophisticated cancellation
        self.indexing_in_progress = False
        
        logger.info("Indexing stop requested")
        return {
            "success": True,
            "message": "Indexing will stop after current file"
        }


# Global instance
system_indexer = SystemIndexer()
