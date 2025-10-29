import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.config.settings import settings
import logging
import json

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing SQLite database for metadata"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self.initialize()
    
    def initialize(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    path TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    chunks INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Chat conversations table
            # Conversations table for chat management
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    title TEXT
                )
            """)
            
            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sources TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # File operations
    def add_file(self, file_data: Dict[str, Any]) -> bool:
        """Add a new file to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO files (id, name, type, size, path, uploaded_at, status, chunks, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_data["id"],
                file_data["name"],
                file_data["type"],
                file_data["size"],
                file_data["path"],
                file_data["uploaded_at"],
                file_data["status"],
                file_data.get("chunks", 0),
                json.dumps(file_data.get("metadata", {}))
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding file: {e}")
            return False
    
    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "size": row["size"],
                    "path": row["path"],
                    "uploadedAt": row["uploaded_at"],
                    "status": row["status"],
                    "chunks": row["chunks"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting file: {e}")
            return None
    
    def get_all_files(self, file_type: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all files with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM files WHERE 1=1"
            params = []
            
            if file_type:
                query += " AND type = ?"
                params.append(file_type)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY uploaded_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            files = []
            for row in rows:
                files.append({
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "size": row["size"],
                    "path": row["path"],
                    "uploadedAt": row["uploaded_at"],
                    "status": row["status"],
                    "chunks": row["chunks"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting files: {e}")
            return []
    
    def update_file_status(self, file_id: str, status: str, chunks: int = 0) -> bool:
        """Update file status and chunk count"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE files SET status = ?, chunks = ? WHERE id = ?
            """, (status, chunks, file_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating file status: {e}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file by path"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM files WHERE path = ?", (path,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "type": row["type"],
                    "size": row["size"],
                    "path": row["path"],
                    "uploadedAt": row["uploaded_at"],
                    "status": row["status"],
                    "chunks": row["chunks"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting file by path: {e}")
            return None
    
    def update_file(self, file_id: str, file_data: Dict[str, Any]) -> bool:
        """Update file data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE files 
                SET name = ?, type = ?, size = ?, path = ?, status = ?, chunks = ?, metadata = ?
                WHERE id = ?
            """, (
                file_data["name"],
                file_data["type"],
                file_data["size"],
                file_data["path"],
                file_data["status"],
                file_data.get("chunks", 0),
                json.dumps(file_data.get("metadata", {})),
                file_id
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating file: {e}")
            return False
    
    # Conversation operations
    def create_conversation(self, conversation_id: str) -> bool:
        """Create a new conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO conversations (id, created_at, updated_at)
                VALUES (?, ?, ?)
            """, (conversation_id, now, now))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return False
    
    def add_message(self, message_data: Dict[str, Any]) -> bool:
        """Add a message to a conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO messages (id, conversation_id, role, content, timestamp, sources)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                message_data["id"],
                message_data["conversation_id"],
                message_data["role"],
                message_data["content"],
                message_data["timestamp"],
                json.dumps(message_data.get("sources", []))
            ))
            
            # Update conversation updated_at
            cursor.execute("""
                UPDATE conversations SET updated_at = ? WHERE id = ?
            """, (message_data["timestamp"], message_data["conversation_id"]))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            return False
    
    def get_conversation_history(self, conversation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get conversation history"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if conversation_id:
                cursor.execute("""
                    SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC
                """, (conversation_id,))
            else:
                cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 100")
            
            rows = cursor.fetchall()
            conn.close()
            
            messages = []
            for row in rows:
                messages.append({
                    "id": row["id"],
                    "conversationId": row["conversation_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "timestamp": row["timestamp"],
                    "sources": json.loads(row["sources"]) if row["sources"] else []
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Get all conversations with metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get conversations with their first message as title
            cursor.execute("""
                SELECT 
                    c.id,
                    c.created_at,
                    c.updated_at,
                    c.title,
                    (SELECT content FROM messages WHERE conversation_id = c.id AND role = 'user' ORDER BY timestamp ASC LIMIT 1) as first_message,
                    (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
                FROM conversations c
                ORDER BY c.updated_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            conversations = []
            for row in rows:
                # Use stored title or generate from first message
                title = row["title"] if row["title"] else (
                    row["first_message"][:50] + "..." if row["first_message"] and len(row["first_message"]) > 50 
                    else row["first_message"] or "New Chat"
                )
                
                conversations.append({
                    "id": row["id"],
                    "title": title,
                    "createdAt": row["created_at"],
                    "updatedAt": row["updated_at"],
                    "messageCount": row["message_count"]
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        try:
            logger.info(f"Updating title for conversation {conversation_id} to '{title}'")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First check if conversation exists, create if not
            cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
            existing = cursor.fetchone()
            
            if not existing:
                logger.info(f"Conversation {conversation_id} doesn't exist, creating it")
                # Create the conversation if it doesn't exist
                cursor.execute("""
                    INSERT INTO conversations (id, created_at, updated_at, title)
                    VALUES (?, ?, ?, ?)
                """, (conversation_id, datetime.now().isoformat(), datetime.now().isoformat(), title))
            else:
                logger.info(f"Conversation {conversation_id} exists, updating title")
                # Update existing conversation
                cursor.execute("""
                    UPDATE conversations 
                    SET title = ?, updated_at = ?
                    WHERE id = ?
                """, (title, datetime.now().isoformat(), conversation_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Successfully updated title for conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating conversation title: {e}", exc_info=True)
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        try:
            logger.info(f"Deleting conversation {conversation_id}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete all messages for this conversation
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            
            # Delete the conversation
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"Successfully deleted conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}", exc_info=True)
            return False
    
    # Statistics
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total files
            cursor.execute("SELECT COUNT(*) FROM files")
            total_files = cursor.fetchone()[0]
            
            # Files by type
            cursor.execute("SELECT type, COUNT(*) FROM files GROUP BY type")
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total chunks
            cursor.execute("SELECT SUM(chunks) FROM files")
            total_chunks = cursor.fetchone()[0] or 0
            
            # Storage used
            cursor.execute("SELECT SUM(size) FROM files")
            storage_used = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "totalFiles": total_files,
                "totalChunks": total_chunks,
                "byType": {
                    "documents": by_type.get("document", 0) + by_type.get("code", 0) + by_type.get("config", 0),
                    "images": by_type.get("image", 0),
                    "audio": by_type.get("audio", 0)
                },
                "storageUsed": storage_used,
                "lastUpdated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    # Settings operations
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row[0])
            return default
            
        except Exception as e:
            logger.error(f"Error getting setting: {e}")
            return default
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update or insert a setting"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            """, (key, json.dumps(value)))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating setting: {e}")
            return False


# Global instance
db_service = DatabaseService()
