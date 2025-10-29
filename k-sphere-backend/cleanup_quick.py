#!/usr/bin/env python3
"""
Quick cleanup script to DELETE all files stuck in 'processing' or 'failed' status (no confirmation)
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.database_service import db_service
from src.services.vector_db_service import vector_db_service

def cleanup_stuck_files():
    """Delete all files stuck in processing or failed status"""
    # Get all files with 'processing' status
    processing_files = db_service.get_all_files(status='processing')
    
    # Get all files with 'failed' status  
    failed_files = db_service.get_all_files(status='failed')
    
    all_files = processing_files + failed_files
    
    if not all_files:
        print("✅ No files found with 'processing' or 'failed' status")
        return
    
    print(f"\n📋 Found {len(all_files)} files to delete")
    print(f"   - Processing: {len(processing_files)}")
    print(f"   - Failed: {len(failed_files)}\n")
    
    # Delete each file
    deleted_count = 0
    for file in all_files:
        file_id = file['id']
        file_name = file['name']
        
        try:
            # Delete from vector database
            vector_db_service.delete_by_file_id("files", file_id)
            
            # Delete from SQLite database
            if db_service.delete_file(file_id):
                deleted_count += 1
                
        except Exception as e:
            print(f"   ✗ Error deleting file {file_name}: {e}")
    
    print(f"\n✅ Deleted {deleted_count} files!\n")

if __name__ == "__main__":
    print("=" * 70)
    print("  K-SPHERE: CLEANUP STUCK FILES")
    print("=" * 70)
    
    cleanup_stuck_files()
