from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import sys
import os

from src.config.settings import settings
from src.routes import knowledge_base, chat, system, settings as settings_router, system_indexer

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="K-Sphere AI Backend",
    description="Offline-first multimodal RAG system with Ollama",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(knowledge_base.router, prefix="/api", tags=["Knowledge Base"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(system.router, prefix="/api", tags=["System"])
app.include_router(settings_router.router, prefix="/api", tags=["Settings"])
app.include_router(system_indexer.router, prefix="/api", tags=["System Indexer"])

# Mount uploads directory as static files
uploads_dir = os.path.join(os.path.dirname(__file__), "data", "uploads")
if os.path.exists(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "K-Sphere AI Backend",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info("Starting K-Sphere AI Backend...")
    logger.info(f"Ollama Host: {settings.OLLAMA_HOST}")
    logger.info(f"LLM Model: {settings.OLLAMA_LLM_MODEL}")
    logger.info(f"Embedding Model: {settings.OLLAMA_EMBEDDING_MODEL}")
    logger.info(f"Vector DB Path: {settings.VECTOR_DB_PATH}")
    logger.info(f"Watch Directory: {settings.WATCH_DIRECTORY}")
    
    # Check Ollama connection
    from src.services.ollama_service import ollama_service
    health = await ollama_service.check_health()
    
    if health.get("status") == "running":
        logger.info("✓ Ollama is running")
        available_models = health.get("available_models", [])
        logger.info(f"Available models: {', '.join(available_models)}")
        
        # Check if required models are available using proper matching
        llm_exists = await ollama_service.check_model_exists(settings.OLLAMA_LLM_MODEL)
        if not llm_exists:
            logger.warning(f"⚠ LLM model '{settings.OLLAMA_LLM_MODEL}' not found. Please run: ollama pull {settings.OLLAMA_LLM_MODEL}")
        
        embedding_exists = await ollama_service.check_model_exists(settings.OLLAMA_EMBEDDING_MODEL)
        if not embedding_exists:
            logger.warning(f"⚠ Embedding model '{settings.OLLAMA_EMBEDDING_MODEL}' not found. Please run: ollama pull {settings.OLLAMA_EMBEDDING_MODEL}")
    else:
        logger.error("✗ Ollama is not running. Please start Ollama service.")
    
    logger.info("K-Sphere AI Backend started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("Shutting down K-Sphere AI Backend...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
