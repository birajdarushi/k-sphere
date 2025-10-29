#!/usr/bin/env python3
"""
ChromaDB Inspector - View contents of the vector database
Usage: python inspect_vectordb.py
"""

import sys
sys.path.insert(0, '/Users/rushiraj/Desktop/k-sphere-backend')

from src.services.vector_db_service import vector_db_service
from src.services.database_service import db_service
import json

def format_size(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def inspect_database():
    print("=" * 70)
    print(" K-Sphere Vector Database Inspector")
    print("=" * 70)
    print()
    
    # Get database stats
    stats = db_service.get_stats()
    
    print("📊 DATABASE STATISTICS")
    print("-" * 70)
    print(f"Total Files:      {stats.get('totalFiles', 0)}")
    print(f"Total Chunks:     {stats.get('totalChunks', 0)}")
    print(f"Documents:        {stats.get('byType', {}).get('documents', 0)}")
    print(f"Images:           {stats.get('byType', {}).get('images', 0)}")
    print(f"Audio:            {stats.get('byType', {}).get('audio', 0)}")
    print(f"Storage Used:     {format_size(stats.get('storageUsed', 0))}")
    print()
    
    # Get vector DB info
    print("🗄️  VECTOR DATABASE COLLECTIONS")
    print("-" * 70)
    for name, collection in vector_db_service.collections.items():
        count = collection.count()
        print(f"Collection: {name}")
        print(f"  - Chunks stored: {count}")
        
        if count > 0:
            # Get a sample
            results = collection.get(limit=3, include=["metadatas", "documents"])
            print(f"  - Sample entries:")
            for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
                file_name = meta.get('file_name', 'Unknown')
                chunk_idx = meta.get('chunk_index', '?')
                preview = doc[:80] + "..." if len(doc) > 80 else doc
                print(f"    [{i+1}] {file_name} (chunk {chunk_idx})")
                print(f"        \"{preview}\"")
        print()
    
    # Get all files
    print("📁 INDEXED FILES")
    print("-" * 70)
    files = db_service.get_all_files()
    
    if not files:
        print("No files indexed yet.")
    else:
        for f in files:
            status_icon = "✓" if f['status'] == 'indexed' else "⚠" if f['status'] == 'processing' else "✗"
            print(f"{status_icon} {f['name']}")
            print(f"   Type: {f['type']} | Size: {format_size(f['size'])} | Chunks: {f['chunks']}")
            print(f"   Uploaded: {f['uploadedAt']}")
            print()
    
    print("=" * 70)
    print()

if __name__ == "__main__":
    try:
        inspect_database()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
