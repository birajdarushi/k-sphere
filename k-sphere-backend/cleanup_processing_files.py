#!/usr/bin/env python3
"""
Cleanup script to DELETE all files stuck in 'processing' or 'failed' status
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.database_service import db_service
from src.services.vector_db_service import vector_db_service
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def cleanup_stuck_files():
    """Delete all files stuck in processing or failed status"""
    try:
        # Get all files with 'processing' status
        processing_files = db_service.get_all_files(status='processing')
        
        # Get all files with 'failed' status
        failed_files = db_service.get_all_files(status='failed')
        
        all_files = processing_files + failed_files
        
        if not all_files:
            logger.info("✅ No files found with 'processing' or 'failed' status")
            return
        
        logger.info(f"\n📋 Found files to delete:")
        logger.info(f"   - Processing: {len(processing_files)}")
        logger.info(f"   - Failed: {len(failed_files)}")
        logger.info(f"   - Total: {len(all_files)}\n")
        
        # Ask for confirmation
        response = input(f"⚠️  Delete all {len(all_files)} files? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            logger.info("❌ Deletion cancelled")
            return
        
        logger.info("\n🗑️  Deleting files...\n")
        
        # Delete each file
        deleted_count = 0
        for file in all_files:
            file_id = file['id']
            file_name = file['name']
            file_status = file['status']
            
            try:
                # Delete from vector database
                vector_db_service.delete_by_file_id("files", file_id)
                
                # Delete from SQLite database
                if db_service.delete_file(file_id):
                    logger.info(f"   ✓ Deleted: {file_name} ({file_status})")
                    deleted_count += 1
                else:
                    logger.error(f"   ✗ Failed to delete from database: {file_name}")
                    
            except Exception as e:
                logger.error(f"   ✗ Error deleting file {file_name}: {e}")
        
        logger.info(f"\n✅ Cleanup complete! Deleted {deleted_count} out of {len(all_files)} files\n")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        raise


if __name__ == "__main__":
    print("=" * 70)
    print("  K-SPHERE: CLEANUP STUCK FILES")
    print("=" * 70)
    
    cleanup_stuck_files()
