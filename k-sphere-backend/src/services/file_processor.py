import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Document processing
import pypdf
from docx import Document as DocxDocument
import pdfplumber

# Image processing
from PIL import Image
import pytesseract

# Audio processing
# whisper imported dynamically in _load_whisper_model()
import soundfile as sf

from src.services.ollama_service import ollama_service
from src.services.vector_db_service import vector_db_service
from src.services.database_service import db_service
from src.config.settings import settings

logger = logging.getLogger(__name__)


class FileProcessor:
    """Service for processing different file types"""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.whisper_model = None
    
    def _load_whisper_model(self):
        """Lazy load Whisper model"""
        if self.whisper_model is None:
            try:
                logger.info("Loading Whisper model...")
                import whisper  # type: ignore
                self.whisper_model = whisper.load_model("base")
                logger.info("Whisper model loaded successfully")
            except ImportError:
                logger.warning("Whisper not installed - audio transcription disabled. Install with: pip install openai-whisper")
                return None
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                return None
        return self.whisper_model
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = " ".join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to MM:SS or HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def _chunk_audio_with_timestamps(self, segments: List[Dict]) -> List[Dict[str, Any]]:
        """Create chunks from audio segments with timestamp information"""
        if not segments:
            return []
        
        chunks = []
        current_chunk = {
            "text": "",
            "start": 0.0,
            "end": 0.0,
            "word_count": 0
        }
        
        for segment in segments:
            segment_text = segment.get("text", "").strip()
            segment_start = segment.get("start", 0.0)
            segment_end = segment.get("end", 0.0)
            
            if not segment_text:
                continue
            
            words_in_segment = len(segment_text.split())
            
            # If adding this segment would exceed chunk size, save current chunk
            if current_chunk["word_count"] > 0 and (current_chunk["word_count"] + words_in_segment) > self.chunk_size:
                chunks.append({
                    "text": current_chunk["text"].strip(),
                    "start": current_chunk["start"],
                    "end": current_chunk["end"]
                })
                current_chunk = {
                    "text": segment_text,
                    "start": segment_start,
                    "end": segment_end,
                    "word_count": words_in_segment
                }
            else:
                # Add to current chunk
                if current_chunk["word_count"] == 0:
                    current_chunk["start"] = segment_start
                
                current_chunk["text"] += " " + segment_text if current_chunk["text"] else segment_text
                current_chunk["end"] = segment_end
                current_chunk["word_count"] += words_in_segment
        
        # Add the last chunk
        if current_chunk["word_count"] > 0:
            chunks.append({
                "text": current_chunk["text"].strip(),
                "start": current_chunk["start"],
                "end": current_chunk["end"]
            })
        
        return chunks
    
    async def process_pdf(self, file_path: str, file_id: str) -> Dict[str, Any]:
        """Process PDF file"""
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Extract text from PDF
            text_content = []
            page_mapping = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                        page_mapping.append(page_num)
            
            full_text = "\n\n".join(text_content)
            
            # Chunk the text
            chunks = self._chunk_text(full_text)
            
            # Generate embeddings
            embeddings = await ollama_service.generate_embeddings_batch(chunks)
            
            # Store in vector database
            metadatas = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                
                # Estimate which page this chunk belongs to
                char_position = full_text.find(chunk[:50])
                estimated_page = 1
                if char_position != -1:
                    chars_per_page = len(full_text) // len(page_mapping)
                    estimated_page = min(page_mapping[-1], max(1, char_position // chars_per_page + 1))
                
                metadatas.append({
                    "file_id": file_id,
                    "file_name": os.path.basename(file_path),
                    "chunk_index": i,
                    "content": chunk,
                    "page": estimated_page,
                    "type": "document"
                })
            
            valid_embeddings = [emb for emb in embeddings if emb is not None]
            valid_chunks = [chunk for i, chunk in enumerate(chunks) if embeddings[i] is not None]
            valid_metadatas = [meta for i, meta in enumerate(metadatas) if embeddings[i] is not None]
            valid_ids = [cid for i, cid in enumerate(chunk_ids) if embeddings[i] is not None]
            
            if valid_embeddings:
                vector_db_service.add_documents(
                    collection_name="documents",
                    embeddings=valid_embeddings,
                    documents=valid_chunks,
                    metadatas=valid_metadatas,
                    ids=valid_ids
                )
            
            return {
                "success": True,
                "chunks": len(valid_chunks),
                "pages": len(page_mapping),
                "metadata": {
                    "pages": len(page_mapping)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_docx(self, file_path: str, file_id: str) -> Dict[str, Any]:
        """Process DOCX file"""
        try:
            logger.info(f"Processing DOCX: {file_path}")
            
            # Extract text from DOCX
            doc = DocxDocument(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            full_text = "\n\n".join(paragraphs)
            
            # Chunk the text
            chunks = self._chunk_text(full_text)
            
            # Generate embeddings
            embeddings = await ollama_service.generate_embeddings_batch(chunks)
            
            # Store in vector database
            metadatas = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                metadatas.append({
                    "file_id": file_id,
                    "file_name": os.path.basename(file_path),
                    "chunk_index": i,
                    "content": chunk,
                    "type": "document"
                })
            
            valid_embeddings = [emb for emb in embeddings if emb is not None]
            valid_chunks = [chunk for i, chunk in enumerate(chunks) if embeddings[i] is not None]
            valid_metadatas = [meta for i, meta in enumerate(metadatas) if embeddings[i] is not None]
            valid_ids = [cid for i, cid in enumerate(chunk_ids) if embeddings[i] is not None]
            
            if valid_embeddings:
                vector_db_service.add_documents(
                    collection_name="documents",
                    embeddings=valid_embeddings,
                    documents=valid_chunks,
                    metadatas=valid_metadatas,
                    ids=valid_ids
                )
            
            return {
                "success": True,
                "chunks": len(valid_chunks),
                "metadata": {}
            }
            
        except Exception as e:
            logger.error(f"Error processing DOCX: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_text(self, file_path: str, file_id: str) -> Dict[str, Any]:
        """Process TXT file"""
        try:
            logger.info(f"Processing TXT: {file_path}")
            
            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            
            # Chunk the text
            chunks = self._chunk_text(full_text)
            
            # Generate embeddings
            embeddings = await ollama_service.generate_embeddings_batch(chunks)
            
            # Store in vector database
            metadatas = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                metadatas.append({
                    "file_id": file_id,
                    "file_name": os.path.basename(file_path),
                    "chunk_index": i,
                    "content": chunk,
                    "type": "document"
                })
            
            valid_embeddings = [emb for emb in embeddings if emb is not None]
            valid_chunks = [chunk for i, chunk in enumerate(chunks) if embeddings[i] is not None]
            valid_metadatas = [meta for i, meta in enumerate(metadatas) if embeddings[i] is not None]
            valid_ids = [cid for i, cid in enumerate(chunk_ids) if embeddings[i] is not None]
            
            if valid_embeddings:
                vector_db_service.add_documents(
                    collection_name="documents",
                    embeddings=valid_embeddings,
                    documents=valid_chunks,
                    metadatas=valid_metadatas,
                    ids=valid_ids
                )
            
            return {
                "success": True,
                "chunks": len(valid_chunks),
                "metadata": {}
            }
            
        except Exception as e:
            logger.error(f"Error processing TXT: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_image(self, file_path: str, file_id: str) -> Dict[str, Any]:
        """Process image file with OCR"""
        try:
            logger.info(f"Processing Image: {file_path}")
            
            # Open image
            image = Image.open(file_path)
            width, height = image.size
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                text = f"[Image: {os.path.basename(file_path)}]"
            
            # Chunk the text
            chunks = self._chunk_text(text)
            
            # Generate embeddings
            embeddings = await ollama_service.generate_embeddings_batch(chunks)
            
            # Store in vector database
            metadatas = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                metadatas.append({
                    "file_id": file_id,
                    "file_name": os.path.basename(file_path),
                    "chunk_index": i,
                    "content": chunk,
                    "type": "image",
                    "width": width,
                    "height": height
                })
            
            valid_embeddings = [emb for emb in embeddings if emb is not None]
            valid_chunks = [chunk for i, chunk in enumerate(chunks) if embeddings[i] is not None]
            valid_metadatas = [meta for i, meta in enumerate(metadatas) if embeddings[i] is not None]
            valid_ids = [cid for i, cid in enumerate(chunk_ids) if embeddings[i] is not None]
            
            if valid_embeddings:
                vector_db_service.add_documents(
                    collection_name="images",
                    embeddings=valid_embeddings,
                    documents=valid_chunks,
                    metadatas=valid_metadatas,
                    ids=valid_ids
                )
            
            return {
                "success": True,
                "chunks": len(valid_chunks),
                "metadata": {
                    "width": width,
                    "height": height
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_audio(self, file_path: str, file_id: str) -> Dict[str, Any]:
        """Process audio file with Whisper with timestamp support"""
        try:
            logger.info(f"Processing Audio: {file_path}")
            
            # Load Whisper model
            model = self._load_whisper_model()
            
            if model is None:
                # Return without processing if Whisper is not available
                return {
                    "success": False,
                    "error": "Whisper not available - audio transcription disabled. Install with: pip install openai-whisper"
                }
            
            # Transcribe audio with word-level timestamps
            result = model.transcribe(file_path, word_timestamps=True)
            text = result["text"]
            segments = result.get("segments", [])
            
            # Get audio duration
            data, samplerate = sf.read(file_path)
            duration = len(data) / samplerate
            
            # Create chunks with timestamp information
            chunks_with_timestamps = self._chunk_audio_with_timestamps(segments)
            
            # Extract just the text for embeddings
            chunks = [chunk["text"] for chunk in chunks_with_timestamps]
            
            # Generate embeddings
            embeddings = await ollama_service.generate_embeddings_batch(chunks)
            
            # Store in vector database
            metadatas = []
            chunk_ids = []
            
            for i, chunk_info in enumerate(chunks_with_timestamps):
                chunk_id = f"{file_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                metadatas.append({
                    "file_id": file_id,
                    "file_name": os.path.basename(file_path),
                    "chunk_index": i,
                    "content": chunk_info["text"],
                    "type": "audio",
                    "duration": duration,
                    "start_time": chunk_info["start"],
                    "end_time": chunk_info["end"],
                    "timestamp": f"{self._format_timestamp(chunk_info['start'])} - {self._format_timestamp(chunk_info['end'])}"
                })
            
            valid_embeddings = [emb for emb in embeddings if emb is not None]
            valid_chunks = [chunk for i, chunk in enumerate(chunks) if embeddings[i] is not None]
            valid_metadatas = [meta for i, meta in enumerate(metadatas) if embeddings[i] is not None]
            valid_ids = [cid for i, cid in enumerate(chunk_ids) if embeddings[i] is not None]
            
            if valid_embeddings:
                vector_db_service.add_documents(
                    collection_name="audio",
                    embeddings=valid_embeddings,
                    documents=valid_chunks,
                    metadatas=valid_metadatas,
                    ids=valid_ids
                )
            
            return {
                "success": True,
                "chunks": len(valid_chunks),
                "metadata": {
                    "duration": duration
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_file(self, file_path: str, file_id: str, file_type: str = None) -> Dict[str, Any]:
        """Process a file based on its type"""
        ext = os.path.splitext(file_path)[1].lower()
        
        # PDF files
        if ext == '.pdf':
            return await self.process_pdf(file_path, file_id)
        
        # Word documents
        elif ext == '.docx':
            return await self.process_docx(file_path, file_id)
        
        # Images
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:
            return await self.process_image(file_path, file_id)
        
        # Audio files
        elif ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
            return await self.process_audio(file_path, file_id)
        
        # Text-based files (code, config, markdown, plain text)
        elif ext in ['.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', 
                     '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
                     '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.conf',
                     '.html', '.htm', '.css', '.scss', '.less', '.sql', '.sh', '.bash',
                     '.csv', '.tsv', '.log', '.rtf', '.odt']:
            return await self.process_text(file_path, file_id)
        
        else:
            logger.warning(f"Unsupported file type: {ext} for file {file_path}")
            return {"success": False, "error": f"Unsupported file type: {ext}", "chunks": 0}


# Global instance
file_processor = FileProcessor()
