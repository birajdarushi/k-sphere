import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Ollama Configuration
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    
    # Vector Database
    VECTOR_DB_PATH: str = "./data/vectordb"
    
    # File Storage
    WATCH_DIRECTORY: str = "./data/uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Processing Configuration
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Database
    DATABASE_PATH: str = "./data/k-sphere.db"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "./logs/k-sphere.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure directories exist
os.makedirs(settings.WATCH_DIRECTORY, exist_ok=True)
os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_PATH), exist_ok=True)
os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
