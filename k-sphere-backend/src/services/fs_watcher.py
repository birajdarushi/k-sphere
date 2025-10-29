"""
File System Watcher Service

This service monitors permitted paths for file changes and triggers automatic indexing.
Uses the watchdog library for efficient file system monitoring.
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Set
from datetime import datetime
import logging
import threading

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create dummy classes when watchdog is not available
    class FileSystemEventHandler:
        pass
    class FileSystemEvent:
        pass
    class Observer:
        pass

logger = logging.getLogger(__name__)

if not WATCHDOG_AVAILABLE:
    logger.warning("watchdog not installed - file system monitoring disabled. Install with: pip install watchdog")

from src.services.system_indexer import system_indexer


class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events"""
    
    def __init__(self, watcher_service):
        super().__init__()
        self.watcher_service = watcher_service
        self.pending_changes: Set[str] = set()
        self.lock = threading.Lock()
    
    def _should_process(self, file_path: str) -> bool:
        """Check if file should be processed"""
        # Check if it's a supported file
        if not system_indexer._is_supported_file(file_path):
            return False
        
        # Check if it should be excluded
        if system_indexer._should_exclude(file_path):
            return False
        
        return True
    
    def _queue_file_for_indexing(self, file_path: str):
        """Queue a file for indexing"""
        if not self._should_process(file_path):
            return
        
        with self.lock:
            self.pending_changes.add(file_path)
        
        logger.debug(f"Queued file for indexing: {file_path}")
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation"""
        if not event.is_directory:
            self._queue_file_for_indexing(event.src_path)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification"""
        if not event.is_directory:
            self._queue_file_for_indexing(event.src_path)
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion"""
        if not event.is_directory:
            # Remove from index
            self.watcher_service.handle_file_deletion(event.src_path)
    
    def on_moved(self, event: FileSystemEvent):
        """Handle file move/rename"""
        if not event.is_directory:
            # Remove old path
            self.watcher_service.handle_file_deletion(event.src_path)
            # Add new path
            self._queue_file_for_indexing(event.dest_path)
    
    def get_pending_changes(self) -> Set[str]:
        """Get and clear pending changes"""
        with self.lock:
            changes = self.pending_changes.copy()
            self.pending_changes.clear()
            return changes


class FileSystemWatcher:
    """Service for monitoring file system changes in permitted paths"""
    
    def __init__(self):
        self.observer = None
        self.handler = None
        self.monitoring = False
        self.watched_paths: Set[str] = set()
        self.background_task = None
        
        if not WATCHDOG_AVAILABLE:
            logger.warning("File system watching disabled - watchdog not installed")
    
    def start_monitoring(self) -> Dict[str, Any]:
        """Start monitoring permitted paths"""
        if not WATCHDOG_AVAILABLE:
            return {
                "success": False,
                "error": "watchdog library not installed"
            }
        
        if self.monitoring:
            return {
                "success": False,
                "error": "Already monitoring"
            }
        
        permitted_paths = system_indexer.get_permitted_paths()
        if not permitted_paths:
            return {
                "success": False,
                "error": "No permitted paths to monitor"
            }
        
        try:
            self.observer = Observer()
            self.handler = FileChangeHandler(self)
            
            # Watch all permitted paths
            for path in permitted_paths:
                if os.path.exists(path):
                    self.observer.schedule(self.handler, path, recursive=True)
                    self.watched_paths.add(path)
                    logger.info(f"Monitoring path: {path}")
            
            self.observer.start()
            self.monitoring = True
            
            # Start background processing task
            self.background_task = asyncio.create_task(self._process_changes())
            
            logger.info(f"File system monitoring started for {len(self.watched_paths)} paths")
            
            return {
                "success": True,
                "message": f"Monitoring {len(self.watched_paths)} paths",
                "watched_paths": list(self.watched_paths)
            }
            
        except Exception as e:
            logger.error(f"Error starting file system monitoring: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring file system"""
        if not self.monitoring:
            return {
                "success": False,
                "error": "Not currently monitoring"
            }
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            if self.background_task:
                self.background_task.cancel()
                self.background_task = None
            
            self.monitoring = False
            self.watched_paths.clear()
            
            logger.info("File system monitoring stopped")
            
            return {
                "success": True,
                "message": "File system monitoring stopped"
            }
            
        except Exception as e:
            logger.error(f"Error stopping file system monitoring: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_changes(self):
        """Background task to process pending changes"""
        try:
            while self.monitoring:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                if not self.handler:
                    continue
                
                pending = self.handler.get_pending_changes()
                
                if pending:
                    logger.info(f"Processing {len(pending)} file changes")
                    
                    # Process files in batches
                    for file_path in pending:
                        try:
                            await system_indexer._index_single_file(file_path)
                        except Exception as e:
                            logger.error(f"Error indexing file {file_path}: {e}")
        
        except asyncio.CancelledError:
            logger.info("Background processing task cancelled")
        except Exception as e:
            logger.error(f"Error in background processing: {e}")
    
    def handle_file_deletion(self, file_path: str):
        """Handle file deletion from index"""
        try:
            from src.services.database_service import db_service
            from src.services.vector_db_service import vector_db_service
            
            # Get file from database
            file_data = db_service.get_file_by_path(file_path)
            
            if file_data:
                file_id = file_data["id"]
                
                # Remove from vector database
                vector_db_service.delete_document(file_id)
                
                # Remove from database
                db_service.delete_file(file_id)
                
                logger.info(f"Removed deleted file from index: {file_path}")
        
        except Exception as e:
            logger.error(f"Error handling file deletion: {e}")
    
    def update_watched_paths(self) -> Dict[str, Any]:
        """Update watched paths based on current permitted paths"""
        if not self.monitoring:
            return {
                "success": False,
                "error": "Not currently monitoring"
            }
        
        try:
            current_permitted = set(system_indexer.get_permitted_paths())
            
            # Stop and restart with new paths
            self.stop_monitoring()
            return self.start_monitoring()
            
        except Exception as e:
            logger.error(f"Error updating watched paths: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring": self.monitoring,
            "watched_paths": list(self.watched_paths),
            "watchdog_available": WATCHDOG_AVAILABLE
        }


# Global instance
fs_watcher = FileSystemWatcher()
