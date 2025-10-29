"""
Settings API Routes
Endpoints for managing application settings and models
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel
import subprocess
import asyncio

from src.services.settings_service import settings_service
from src.services.ollama_service import ollama_service

router = APIRouter()


class SettingsUpdate(BaseModel):
    """Model for settings update request"""
    settings: Dict[str, Any]


class ModelPullRequest(BaseModel):
    """Model for pulling a new Ollama model"""
    model_name: str


class ModelSwitchRequest(BaseModel):
    """Model for switching active model"""
    model_type: str  # "llm" or "embedding"
    model_name: str


@router.get("/settings")
async def get_settings():
    """
    Get current application settings
    
    Returns all configurable settings including:
    - LLM model
    - Embedding model
    - Chunk size and overlap
    - Watch directory
    - Database paths
    """
    return {
        "success": True,
        "settings": settings_service.get_all()
    }


@router.post("/settings")
async def update_settings(request: SettingsUpdate):
    """
    Update application settings
    
    Accepts any valid setting key-value pairs and persists to disk.
    Model changes will be applied to active services.
    """
    try:
        success = settings_service.update_many(request.settings)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save settings")
        
        # Apply model changes to ollama service if LLM or embedding model changed
        if "ollama_llm_model" in request.settings:
            ollama_service.llm_model = request.settings["ollama_llm_model"]
        
        if "ollama_embedding_model" in request.settings:
            ollama_service.embedding_model = request.settings["ollama_embedding_model"]
        
        return {
            "success": True,
            "message": "Settings updated successfully",
            "settings": settings_service.get_all()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/models")
async def get_available_models():
    """
    Get all available Ollama models
    
    Returns:
    - List of available models from Ollama
    - Currently active LLM model
    - Currently active embedding model
    """
    try:
        health = await ollama_service.check_health()
        available_models = health.get("available_models", [])
        
        return {
            "success": True,
            "available": available_models,
            "current": {
                "llm": settings_service.get("ollama_llm_model"),
                "embedding": settings_service.get("ollama_embedding_model")
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@router.post("/settings/models/pull")
async def pull_model(request: ModelPullRequest, background_tasks: BackgroundTasks):
    """
    Pull a new model from Ollama
    
    This will download the model in the background. Large models may take time.
    Models are pulled using `ollama pull <model_name>`.
    
    Example model names:
    - llama3.2:3b
    - mistral
    - codellama
    - gemma:7b
    """
    try:
        model_name = request.model_name.strip()
        
        if not model_name:
            raise HTTPException(status_code=400, detail="Model name cannot be empty")
        
        # Check if model already exists
        exists = await ollama_service.check_model_exists(model_name)
        if exists:
            return {
                "success": True,
                "message": f"Model {model_name} already exists",
                "model": model_name
            }
        
        # Pull model using subprocess
        def pull_model_background():
            try:
                result = subprocess.run(
                    ["ollama", "pull", model_name],
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout
                )
                
                if result.returncode != 0:
                    print(f"Error pulling model {model_name}: {result.stderr}")
                else:
                    print(f"Successfully pulled model {model_name}")
            
            except subprocess.TimeoutExpired:
                print(f"Timeout pulling model {model_name}")
            except Exception as e:
                print(f"Exception pulling model {model_name}: {e}")
        
        # Start pull in background
        background_tasks.add_task(pull_model_background)
        
        return {
            "success": True,
            "message": f"Started pulling model {model_name}. This may take a few minutes.",
            "model": model_name,
            "status": "pulling"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/models/pull-status/{model_name}")
async def check_pull_status(model_name: str):
    """
    Check if a model has been pulled and is available
    
    Use this to check if a background pull operation completed.
    """
    try:
        exists = await ollama_service.check_model_exists(model_name)
        
        return {
            "success": True,
            "model": model_name,
            "available": exists,
            "status": "ready" if exists else "pulling"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings/models/switch")
async def switch_model(request: ModelSwitchRequest):
    """
    Switch the active LLM or embedding model
    
    Args:
    - model_type: "llm" or "embedding"
    - model_name: The model to switch to (must already be pulled)
    
    The model will be validated before switching and settings will be persisted.
    """
    try:
        model_type = request.model_type.lower()
        model_name = request.model_name.strip()
        
        if model_type not in ["llm", "embedding"]:
            raise HTTPException(
                status_code=400,
                detail="model_type must be 'llm' or 'embedding'"
            )
        
        # Verify model exists
        exists = await ollama_service.check_model_exists(model_name)
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"Model {model_name} not found. Please pull it first using /settings/models/pull"
            )
        
        # Update setting
        setting_key = f"ollama_{model_type}_model"
        success = settings_service.update(setting_key, model_name)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update setting")
        
        # Apply to ollama service
        if model_type == "llm":
            ollama_service.llm_model = model_name
        else:
            ollama_service.embedding_model = model_name
        
        return {
            "success": True,
            "message": f"Switched {model_type} model to {model_name}",
            "model_type": model_type,
            "model": model_name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings/reset")
async def reset_settings():
    """
    Reset all settings to defaults
    
    WARNING: This will reset:
    - Model selections back to llama3.2:3b and nomic-embed-text
    - Chunk size and overlap to defaults
    - All other configuration values
    """
    try:
        success = settings_service.reset_to_defaults()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset settings")
        
        # Reload ollama service with defaults
        ollama_service.llm_model = settings_service.get("ollama_llm_model")
        ollama_service.embedding_model = settings_service.get("ollama_embedding_model")
        
        return {
            "success": True,
            "message": "Settings reset to defaults",
            "settings": settings_service.get_all()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
