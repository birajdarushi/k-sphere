#!/usr/bin/env python3
"""
Migration script to fix sources format in existing messages.
Converts old format (fileName, relevanceScore, metadata) to new format (name, type, relevance)
"""

import sqlite3
import json
import sys
import os

# Add parent directory to path to import settings
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import settings

def migrate_sources():
    """Migrate sources in all messages to new format"""
    db_path = settings.DATABASE_PATH
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all messages with sources
    cursor.execute("SELECT id, sources FROM messages WHERE sources IS NOT NULL AND sources != '[]'")
    rows = cursor.fetchall()
    
    print(f"Found {len(rows)} messages with sources")
    
    migrated = 0
    errors = 0
    
    for msg_id, sources_json in rows:
        try:
            sources = json.loads(sources_json)
            
            if not sources:
                continue
            
            # Check if already in new format (has 'name' field)
            if sources and isinstance(sources[0], dict) and 'name' in sources[0]:
                print(f"Message {msg_id} already in new format, skipping")
                continue
            
            # Convert to new format
            new_sources = []
            for source in sources:
                if isinstance(source, dict):
                    new_source = {
                        "name": source.get("fileName", "Unknown"),
                        "type": source.get("metadata", {}).get("type", "document") if isinstance(source.get("metadata"), dict) else "document",
                        "relevance": source.get("relevanceScore", 0)
                    }
                    new_sources.append(new_source)
            
            # Update message with new sources
            cursor.execute(
                "UPDATE messages SET sources = ? WHERE id = ?",
                (json.dumps(new_sources), msg_id)
            )
            migrated += 1
            print(f"Migrated message {msg_id}: {len(new_sources)} sources")
            
        except Exception as e:
            errors += 1
            print(f"Error migrating message {msg_id}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\nMigration complete!")
    print(f"  Migrated: {migrated}")
    print(f"  Errors: {errors}")
    print(f"  Total: {len(rows)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Sources Format Migration Script")
    print("=" * 60)
    
    response = input("\nThis will update all messages in the database. Continue? (y/n): ")
    
    if response.lower() == 'y':
        migrate_sources()
    else:
        print("Migration cancelled")
