from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import uuid
from datetime import datetime
import logging
import time
import json

from src.models.schemas import ChatRequest, ChatResponse, Source
from src.services.ollama_service import ollama_service
from src.services.vector_db_service import vector_db_service
from src.services.database_service import db_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Handle chat requests with RAG pipeline.
    IMPORTANT: Only uses context from uploaded files, not model's training data.
    """
    try:
        start_time = time.time()
        
        # Generate conversation ID if not provided
        conversation_id = request.conversationId or str(uuid.uuid4())
        
        # If new conversation, create it in database
        if not request.conversationId:
            db_service.create_conversation(conversation_id)
        
        # Get conversation history to provide context for vague queries
        conversation_history = db_service.get_conversation_history(conversation_id)
        
        # Expand vague queries with conversation context
        search_query = request.query
        if conversation_history and len(request.query.split()) < 4:
            # If query is short (likely a follow-up), add context from last user message
            recent_messages = [m for m in conversation_history[-4:] if m.get("role") == "user"]
            if recent_messages:
                last_user_query = recent_messages[-1].get("content", "")
                # Combine for better semantic search
                search_query = f"{last_user_query} {request.query}"
                logger.info(f"Expanded query from '{request.query}' to '{search_query}'")
        
        # Generate embedding for the (potentially expanded) query
        query_embedding = await ollama_service.generate_embedding(search_query)
        
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # Search across all collections, optionally filtered by file IDs
        search_results = vector_db_service.search_all_collections(
            query_embeddings=[query_embedding],
            n_results=request.topK or 5,
            file_ids=request.fileIds  # Pass file IDs for filtering
        )
        
        # If no results found, inform user
        if not search_results:
            answer = "I don't have any information in my knowledge base to answer this question. Please upload relevant documents first."
            sources = []
        else:
            # Build context from search results
            context_parts = []
            sources = []
            
            # Set a relevance threshold - only use results with distance < 450
            # Balance between filtering irrelevant results and keeping useful context
            # Typical distances: <350 excellent, 350-420 good, 420-500 okay, >500 poor
            RELEVANCE_THRESHOLD = 450
            
            for i, result in enumerate(search_results):
                content = result["document"]
                metadata = result["metadata"]
                distance = result["distance"]
                
                # Skip results that are too distant (irrelevant)
                if distance > RELEVANCE_THRESHOLD:
                    logger.info(f"Skipping irrelevant result with distance {distance}")
                    continue
                
                # Include filename in context for better LLM understanding
                file_name = metadata.get("file_name", "Unknown")
                # Clean up the filename for display
                display_name = file_name.split('_', 1)[-1] if '_' in file_name else file_name
                file_type = metadata.get("type", "document")
                
                context_parts.append(f"[Source {len(context_parts)+1} - {display_name} ({file_type})]: {content}")
                
                # Convert squared euclidean distance to similarity percentage
                # ChromaDB returns squared L2 distance for cosine similarity
                # Typical ranges:
                # < 350: Excellent match (95-100%)
                # 350-420: Good match (85-95%)
                # 420-500: Okay match (70-85%)
                # > 500: Poor match (< 70%, should be filtered)
                if distance < 350:
                    similarity = 95 + (350 - distance) / 350 * 5  # 95-100%
                elif distance < 420:
                    similarity = 85 + (420 - distance) / 70 * 10  # 85-95%
                elif distance < 500:
                    similarity = 70 + (500 - distance) / 80 * 15  # 70-85%
                else:
                    similarity = max(0, 70 * (600 - distance) / 100)  # < 70%
                
                similarity = max(0, min(100, similarity))
                
                sources.append(Source(
                    fileId=metadata.get("file_id", ""),
                    fileName=metadata.get("file_name", ""),
                    chunkId=result["id"],
                    content=content,
                    relevanceScore=similarity,
                    metadata=metadata
                ))
            
            # Check if we have any relevant results after filtering
            if not context_parts or not sources:
                answer = "I don't have information about this topic in the uploaded documents. Please upload relevant files first."
            else:
                # Build conversation context
                recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                history_text = ""
                if recent_history:
                    history_text = "\n\nPrevious conversation:\n"
                    for msg in recent_history:
                        role = "User" if msg.get("role") == "user" else "Assistant"
                        content = msg.get("content", "")
                        history_text += f"{role}: {content[:200]}...\n" if len(content) > 200 else f"{role}: {content}\n"
                
                # Combine context
                context = "\n\n".join(context_parts)
                full_context = context + history_text
                
                # Generate response using Ollama with ONLY the provided context
                answer = await ollama_service.generate_chat_response(
                    prompt=request.query,
                    context=full_context
                )
                
                if not answer:
                    raise HTTPException(status_code=500, detail="Failed to generate response")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save user message
        user_message = {
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.query,
            "timestamp": datetime.now().isoformat()
        }
        db_service.add_message(user_message)
        
        # Save assistant message
        assistant_message = {
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().isoformat(),
            "sources": [
                {
                    "name": source.fileName,
                    "type": source.metadata.get("type", "document"),
                    "relevance": source.relevanceScore
                }
                for source in sources
            ]
        }
        db_service.add_message(assistant_message)
        
        return ChatResponse(
            conversationId=conversation_id,
            answer=answer,
            sources=sources,
            processingTime=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Handle chat requests with streaming responses.
    Returns Server-Sent Events (SSE) stream of tokens as they're generated.
    """
    async def generate_stream():
        try:
            start_time = time.time()
            
            # Generate conversation ID if not provided
            conversation_id = request.conversationId or str(uuid.uuid4())
            
            # If new conversation, create it in database
            if not request.conversationId:
                db_service.create_conversation(conversation_id)
            
            # Get conversation history to provide context for vague queries
            conversation_history = db_service.get_conversation_history(conversation_id)
            
            # Expand vague queries with conversation context
            search_query = request.query
            if conversation_history and len(request.query.split()) < 4:
                # If query is short (likely a follow-up), add context from last user message
                recent_messages = [m for m in conversation_history[-4:] if m.get("role") == "user"]
                if recent_messages:
                    last_user_query = recent_messages[-1].get("content", "")
                    # Combine for better semantic search
                    search_query = f"{last_user_query} {request.query}"
                    logger.info(f"Expanded query from '{request.query}' to '{search_query}'")
            
            # Generate embedding for the (potentially expanded) query
            query_embedding = await ollama_service.generate_embedding(search_query)
            
            if not query_embedding:
                yield f"data: {json.dumps({'error': 'Failed to generate query embedding'})}\n\n"
                return
            
            # Search across all collections, optionally filtered by file IDs
            search_results = vector_db_service.search_all_collections(
                query_embeddings=[query_embedding],
                n_results=request.topK or 5,
                file_ids=request.fileIds  # Pass file IDs for filtering
            )
            
            # Build sources list
            sources = []
            context_parts = []
            RELEVANCE_THRESHOLD = 450
            
            if search_results:
                for i, result in enumerate(search_results):
                    content = result["document"]
                    metadata = result["metadata"]
                    distance = result["distance"]
                    
                    # Skip irrelevant results
                    if distance > RELEVANCE_THRESHOLD:
                        continue
                    
                    # Build context
                    file_name = metadata.get("file_name", "Unknown")
                    display_name = file_name.split('_', 1)[-1] if '_' in file_name else file_name
                    file_type = metadata.get("type", "document")
                    
                    context_parts.append(f"[Source {len(context_parts)+1} - {display_name} ({file_type})]: {content}")
                    
                    # Calculate similarity
                    if distance < 350:
                        similarity = 95 + (350 - distance) / 350 * 5
                    elif distance < 420:
                        similarity = 85 + (420 - distance) / 70 * 10
                    elif distance < 500:
                        similarity = 70 + (500 - distance) / 80 * 15
                    else:
                        similarity = max(0, 70 * (600 - distance) / 100)
                    
                    similarity = max(0, min(100, similarity))
                    
                    sources.append({
                        "fileId": metadata.get("file_id", ""),
                        "fileName": metadata.get("file_name", ""),
                        "chunkId": result["id"],
                        "content": content,
                        "relevanceScore": similarity,
                        "metadata": metadata
                    })
            
            # Send sources first
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
            
            # Check if we have relevant context
            if not context_parts or not sources:
                no_info_msg = "I don't have information about this topic in the uploaded documents. Please upload relevant files first."
                yield f"data: {json.dumps({'type': 'token', 'token': no_info_msg})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            
            # Build conversation context (last 10 messages for brevity)
            recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            history_text = ""
            if recent_history:
                history_text = "\n\nPrevious conversation:\n"
                for msg in recent_history:
                    role = "User" if msg.get("role") == "user" else "Assistant"
                    content = msg.get("content", "")
                    history_text += f"{role}: {content[:200]}...\n" if len(content) > 200 else f"{role}: {content}\n"
            
            # Combine context
            context = "\n\n".join(context_parts)
            full_context = context + history_text
            
            # Stream response from Ollama
            full_answer = ""
            response_stream = await ollama_service.generate_chat_response(
                prompt=request.query,
                context=full_context,
                stream=True
            )
            async for token in response_stream:
                full_answer += token
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
            
            # Save messages to database
            processing_time = time.time() - start_time
            
            user_message = {
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "role": "user",
                "content": request.query,
                "timestamp": datetime.now().isoformat()
            }
            db_service.add_message(user_message)
            
            assistant_message = {
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": full_answer,
                "timestamp": datetime.now().isoformat(),
                "sources": [
                    {
                        "name": source.get("fileName", "Unknown"),
                        "type": source.get("metadata", {}).get("type", "document"),
                        "relevance": source.get("relevanceScore", 0)
                    }
                    for source in sources
                ]
            }
            db_service.add_message(assistant_message)
            
            # Send done signal
            yield f"data: {json.dumps({'type': 'done', 'processingTime': processing_time})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@router.get("/chat/history")
async def get_chat_history(
    conversationId: Optional[str] = None,
    limit: Optional[int] = 100
):
    """Get chat history"""
    try:
        messages = db_service.get_conversation_history(conversationId)
        
        # Group messages by conversation
        conversations = {}
        for msg in messages:
            conv_id = msg["conversationId"]
            if conv_id not in conversations:
                conversations[conv_id] = {
                    "id": conv_id,
                    "messages": [],
                    "createdAt": msg["timestamp"],
                    "updatedAt": msg["timestamp"]
                }
            
            conversations[conv_id]["messages"].append(msg)
            
            # Update timestamps
            if msg["timestamp"] < conversations[conv_id]["createdAt"]:
                conversations[conv_id]["createdAt"] = msg["timestamp"]
            if msg["timestamp"] > conversations[conv_id]["updatedAt"]:
                conversations[conv_id]["updatedAt"] = msg["timestamp"]
        
        return {
            "conversations": list(conversations.values())[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search(
    query: str,
    type: Optional[str] = "all",
    limit: Optional[int] = 5
):
    """Search across knowledge base"""
    try:
        start_time = time.time()
        
        # Generate embedding for the query
        query_embedding = await ollama_service.generate_embedding(query)
        
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # Search based on type
        if type == "all":
            search_results = vector_db_service.search_all_collections(
                query_embeddings=[query_embedding],
                n_results=limit
            )
        else:
            collection_map = {
                "document": "documents",
                "image": "images",
                "audio": "audio"
            }
            collection_name = collection_map.get(type)
            
            if not collection_name:
                raise HTTPException(status_code=400, detail="Invalid type")
            
            results = vector_db_service.query(
                collection_name=collection_name,
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            search_results = []
            if results and results.get("ids"):
                for i, doc_id in enumerate(results["ids"][0]):
                    search_results.append({
                        "id": doc_id,
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "collection": collection_name
                    })
        
        # Format results
        formatted_results = []
        for result in search_results:
            metadata = result["metadata"]
            distance = result["distance"]
            
            # Convert squared euclidean distance to similarity percentage (same as chat)
            if distance < 300:
                similarity = 95 + (300 - distance) / 300 * 5
            elif distance < 500:
                similarity = 75 + (500 - distance) / 200 * 20
            elif distance < 700:
                similarity = 50 + (700 - distance) / 200 * 25
            else:
                similarity = max(0, 50 * (1000 - distance) / 300)
            
            similarity = max(0, min(100, similarity))
            
            formatted_results.append({
                "fileId": metadata.get("file_id", ""),
                "fileName": metadata.get("file_name", ""),
                "type": metadata.get("type", ""),
                "snippet": result["document"][:200] + "..." if len(result["document"]) > 200 else result["document"],
                "relevanceScore": similarity,
                "metadata": metadata
            })
        
        processing_time = time.time() - start_time
        
        return {
            "results": formatted_results,
            "total": len(formatted_results),
            "processingTime": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def get_conversations():
    """Get all conversations"""
    try:
        conversations = db_service.get_all_conversations()
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    """Get messages for a specific conversation"""
    try:
        messages = db_service.get_conversation_history(conversation_id)
        return {"messages": messages}
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/conversations/{conversation_id}/title")
async def update_conversation_title(conversation_id: str, title: str):
    """Update conversation title"""
    try:
        success = db_service.update_conversation_title(conversation_id, title)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update title")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation title: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation and all its messages"""
    try:
        success = db_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio to text using Whisper
    Used for voice input in chat
    """
    from fastapi import UploadFile, File
    import tempfile
    import os
    
    try:
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name
        
        try:
            # Load Whisper model
            import whisper
            model = whisper.load_model("base")
            
            # Transcribe
            result = model.transcribe(temp_path)
            transcription = result["text"]
            
            return {
                "success": True,
                "transcription": transcription,
                "language": result.get("language", "unknown")
            }
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Whisper not installed. Install with: pip install openai-whisper"
        )
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/image")
async def chat_with_image(
    file: UploadFile = File(...),
    query: str = Form(...),
    conversationId: Optional[str] = Form(None)
):
    """
    Process uploaded image: extract text via OCR, add to knowledge base temporarily,
    then answer user's query using RAG with the image context
    """
    import tempfile
    import os
    from PIL import Image
    
    try:
        # Generate conversation ID if not provided
        conversation_id = conversationId or str(uuid.uuid4())
        
        # If new conversation, create it in database
        if not conversationId:
            db_service.create_conversation(conversation_id)
        
        # Save image to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name
        
        try:
            # Open image
            img = Image.open(temp_path)
            
            # Extract text from image using OCR
            import pytesseract
            text_from_image = pytesseract.image_to_string(img)
            
            if not text_from_image.strip():
                # No text found in image
                db_service.add_message({
                    "id": str(uuid.uuid4()),
                    "conversation_id": conversation_id,
                    "role": "user",
                    "content": f"[Image uploaded] {query}",
                    "timestamp": datetime.now().isoformat(),
                    "sources": json.dumps([])
                })
                
                db_service.add_message({
                    "id": str(uuid.uuid4()),
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": "I couldn't extract any text from the image. Please upload a clearer image with visible text, or try asking a text-based question.",
                    "timestamp": datetime.now().isoformat(),
                    "sources": json.dumps([])
                })
                
                return {
                    "conversationId": conversation_id,
                    "answer": "I couldn't extract any text from the image. Please upload a clearer image with visible text, or try asking a text-based question.",
                    "sources": [],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Process extracted text + user query together
            combined_query = f"{query}\n\nContext from uploaded image:\n{text_from_image}"
            
            # Generate embedding for combined query
            query_embedding = await ollama_service.generate_embedding(combined_query)
            
            if not query_embedding:
                raise HTTPException(status_code=500, detail="Failed to generate query embedding")
            
            # Search knowledge base with combined context
            search_results = vector_db_service.search_all_collections(
                query_embeddings=[query_embedding],
                n_results=5
            )
            
            # Build context from search results + image text
            context_parts = [f"Text extracted from uploaded image:\n{text_from_image}\n"]
            sources = []
            RELEVANCE_THRESHOLD = 450
            
            if search_results:
                for result in search_results:
                    content = result["document"]
                    metadata = result["metadata"]
                    distance = result["distance"]
                    
                    if distance > RELEVANCE_THRESHOLD:
                        continue
                    
                    context_parts.append(content)
                    
                    # Calculate relevance percentage
                    relevance_score = max(0, min(100, 100 - (distance / 10)))
                    
                    sources.append({
                        "fileName": metadata.get("file_name", "Unknown"),
                        "relevanceScore": relevance_score,
                        "metadata": metadata
                    })
            
            context = "\n\n".join(context_parts)
            
            # Generate answer
            prompt = f"""Context from knowledge base and uploaded image:
{context}

User question: {query}

Provide a helpful answer based ONLY on the context above. If you cannot answer from the context, say so."""

            answer = await ollama_service.generate(prompt)
            
            if not answer:
                answer = "I apologize, but I'm having trouble generating a response. Please try again."
            
            # Transform sources to frontend format
            frontend_sources = []
            for source in sources:
                frontend_sources.append({
                    "name": source["fileName"],
                    "type": source["metadata"].get("type", "document"),
                    "relevance": source["relevanceScore"]
                })
            
            # Save user message
            db_service.add_message({
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "role": "user",
                "content": f"[Image uploaded] {query}",
                "timestamp": datetime.now().isoformat(),
                "sources": json.dumps([])
            })
            
            # Save assistant response
            db_service.add_message({
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": answer,
                "timestamp": datetime.now().isoformat(),
                "sources": json.dumps(frontend_sources)
            })
            
            return {
                "conversationId": conversation_id,
                "answer": answer,
                "sources": frontend_sources,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Error processing image query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
