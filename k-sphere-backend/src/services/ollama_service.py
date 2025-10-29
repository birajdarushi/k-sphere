import httpx
import asyncio
from typing import List, Dict, Any, Optional
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama API"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_HOST
        self.llm_model = settings.OLLAMA_LLM_MODEL
        self.embedding_model = settings.OLLAMA_EMBEDDING_MODEL
        self.timeout = 120.0  # 2 minutes for LLM generation
    
    async def check_health(self) -> Dict[str, Any]:
        """Check if Ollama is running and available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return {
                        "status": "running",
                        "available_models": [m["name"] for m in models],
                        "version": "ollama"
                    }
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embeddings for a given text using Ollama"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("embedding")
                else:
                    logger.error(f"Embedding generation failed: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        tasks = [self.generate_embedding(text) for text in texts]
        return await asyncio.gather(*tasks)
    
    async def generate_chat_response(
        self, 
        prompt: str, 
        context: str = "",
        stream: bool = False
    ):
        """
        Generate chat response using Ollama LLM
        IMPORTANT: Only uses provided context, not model's training data
        
        If stream=True, returns an async generator that yields response chunks
        If stream=False, returns the complete response string
        """
        # Construct prompt with explicit instruction to use only provided context
        system_prompt = """You are a RAG (Retrieval-Augmented Generation) AI assistant that answers questions based on uploaded documents.

CRITICAL RULES:
1. You can ONLY use information from the Context below (from user's uploaded files)
2. If the Context contains relevant information about the question, provide a helpful answer
3. If the Context is about a completely different topic than the question, respond with:
   "I don't have information about this topic in the uploaded documents. Please upload relevant files first."
4. DO NOT use your training data or general knowledge beyond what's in the Context
5. DO NOT explain the system's process - just answer the question directly

Context from uploaded files:
---
{context}
---

User Question: {query}

Answer (use the context above, or say you don't have information if context is unrelated):"""
        
        full_prompt = system_prompt.format(context=context, query=prompt)
        
        if stream:
            # Return generator for streaming mode
            return self._stream_response(full_prompt)
        else:
            # Return complete response for non-streaming mode
            return await self._generate_complete_response(full_prompt)
    
    async def _stream_response(self, prompt: str):
        """Generator for streaming responses"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.llm_model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40,
                        }
                    }
                ) as response:
                    if response.status_code == 200:
                        import json
                        async for line in response.aiter_lines():
                            if line.strip():
                                try:
                                    chunk = json.loads(line)
                                    if "response" in chunk:
                                        yield chunk["response"]
                                except json.JSONDecodeError:
                                    continue
                    else:
                        logger.error(f"Chat generation failed: {await response.aread()}")
                        yield ""
        except Exception as e:
            logger.error(f"Error streaming chat response: {e}")
            yield ""
    
    async def _generate_complete_response(self, prompt: str) -> Optional[str]:
        """Generate complete non-streaming response"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.llm_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40,
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    logger.error(f"Chat generation failed: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return None
    
    async def check_model_exists(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        try:
            health = await self.check_health()
            if health.get("status") == "running":
                available_models = health.get("available_models", [])
                # Check exact match or match with :latest tag
                return (
                    model_name in available_models or 
                    f"{model_name}:latest" in available_models or
                    any(m.startswith(f"{model_name}:") for m in available_models)
                )
            return False
        except Exception as e:
            logger.error(f"Error checking model existence: {e}")
            return False
    
    async def generate_with_image(self, model: str, prompt: str, image_base64: str) -> str:
        """Generate response using a vision model with image input"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "images": [image_base64],
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    logger.error(f"Vision model generation failed: {response.text}")
                    raise Exception(f"Vision model failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error generating with vision model: {e}")
            raise


# Global instance
ollama_service = OllamaService()
