import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from src.config.settings import settings
import logging
import uuid

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service for managing ChromaDB vector database"""
    
    def __init__(self):
        self.client = None
        self.collections = {}
        self.initialize()
    
    def initialize(self):
        """Initialize ChromaDB client and collections"""
        try:
            # Initialize ChromaDB with persistent storage
            self.client = chromadb.PersistentClient(
                path=settings.VECTOR_DB_PATH,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collections for different file types
            self.collections["documents"] = self.client.get_or_create_collection(
                name="documents",
                metadata={"description": "Text chunks from documents"}
            )
            
            self.collections["images"] = self.client.get_or_create_collection(
                name="images",
                metadata={"description": "Image embeddings and descriptions"}
            )
            
            self.collections["audio"] = self.client.get_or_create_collection(
                name="audio",
                metadata={"description": "Transcribed audio chunks"}
            )
            
            logger.info("Vector database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> bool:
        """Add documents to a collection"""
        try:
            if collection_name not in self.collections:
                logger.error(f"Collection {collection_name} not found")
                return False
            
            collection = self.collections[collection_name]
            
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to {collection_name}: {e}")
            return False
    
    def query(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Query a collection for similar documents"""
        try:
            if collection_name not in self.collections:
                logger.error(f"Collection {collection_name} not found")
                return None
            
            collection = self.collections[collection_name]
            
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying {collection_name}: {e}")
            return None
    
    def delete_by_file_id(self, collection_name: str, file_id: str) -> bool:
        """Delete all chunks associated with a file"""
        try:
            if collection_name not in self.collections:
                logger.error(f"Collection {collection_name} not found")
                return False
            
            collection = self.collections[collection_name]
            
            # Delete all documents with matching file_id
            collection.delete(
                where={"file_id": file_id}
            )
            
            logger.info(f"Deleted all chunks for file {file_id} from {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id} from {collection_name}: {e}")
            return False
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection"""
        try:
            if collection_name not in self.collections:
                return 0
            
            collection = self.collections[collection_name]
            return collection.count()
            
        except Exception as e:
            logger.error(f"Error getting count for {collection_name}: {e}")
            return 0
    
    def get_total_chunks(self) -> int:
        """Get total number of chunks across all collections"""
        try:
            total = 0
            for collection_name in self.collections:
                total += self.get_collection_count(collection_name)
            return total
        except Exception as e:
            logger.error(f"Error getting total chunks: {e}")
            return 0
    
    def search_all_collections(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        file_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search across all collections and merge results, optionally filtered by file IDs"""
        try:
            all_results = []
            
            for collection_name, collection in self.collections.items():
                # Build where clause for file ID filtering
                where_clause = None
                if file_ids:
                    where_clause = {"file_id": {"$in": file_ids}}
                
                results = collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results,
                    where=where_clause
                )
                
                if results and results.get("ids"):
                    for i, doc_id in enumerate(results["ids"][0]):
                        all_results.append({
                            "id": doc_id,
                            "document": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i],
                            "collection": collection_name
                        })
            
            # Sort by distance (lower is better)
            all_results.sort(key=lambda x: x["distance"])
            
            return all_results[:n_results]
            
        except Exception as e:
            logger.error(f"Error searching all collections: {e}")
            return []
    
    def reset_database(self) -> bool:
        """Reset all collections (use with caution!)"""
        try:
            for collection_name in list(self.collections.keys()):
                self.client.delete_collection(name=collection_name)
            
            self.collections.clear()
            self.initialize()
            
            logger.info("Vector database reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            return False


# Global instance
vector_db_service = VectorDBService()
