"""
Settings Service for K-Sphere
Manages application configuration with persistence to JSON file
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class SettingsService:
    """Service for managing application settings"""
    
    def __init__(self, settings_file: str = "./data/settings.json"):
        self.settings_file = settings_file
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create defaults"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}, using defaults")
        
        # Default settings
        default_settings = {
            "ollama_llm_model": "llama3.2:3b",
            "ollama_embedding_model": "nomic-embed-text",
            "chunk_size": 512,
            "chunk_overlap": 50,
            "top_k": 5,
            "watch_directory": "./data/uploads",
            "database_path": "./data/k-sphere.db",
            "vector_db_path": "./data/vectordb"
        }
        
        # Save defaults
        self._save_settings(default_settings)
        return default_settings
    
    def _save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get a specific setting"""
        return self.settings.get(key, default)
    
    def update(self, key: str, value: Any) -> bool:
        """Update a specific setting"""
        self.settings[key] = value
        return self._save_settings(self.settings)
    
    def update_many(self, updates: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        self.settings.update(updates)
        return self._save_settings(self.settings)
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        self.settings = {
            "ollama_llm_model": "llama3.2:3b",
            "ollama_embedding_model": "nomic-embed-text",
            "chunk_size": 512,
            "chunk_overlap": 50,
            "top_k": 5,
            "watch_directory": "./data/uploads",
            "database_path": "./data/k-sphere.db",
            "vector_db_path": "./data/vectordb"
        }
        return self._save_settings(self.settings)


# Global instance
settings_service = SettingsService()
