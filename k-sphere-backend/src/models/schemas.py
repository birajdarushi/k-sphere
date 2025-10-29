from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FileType(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"


class FileStatus(str, Enum):
    INDEXED = "indexed"
    PROCESSING = "processing"
    ERROR = "error"


class FileMetadata(BaseModel):
    id: str
    name: str
    type: FileType
    size: int
    uploadedAt: str
    status: FileStatus
    chunks: int
    path: str
    metadata: Dict[str, Any] = {}


class ChunkDetail(BaseModel):
    id: str
    content: str
    page: Optional[int] = None
    timestamp: Optional[float] = None


class FileDetailResponse(FileMetadata):
    preview: Optional[str] = None
    chunks_detail: List[ChunkDetail] = []


class Source(BaseModel):
    fileId: str
    fileName: str
    chunkId: str
    content: str
    relevanceScore: float
    metadata: Dict[str, Any] = {}


class ChatMessage(BaseModel):
    id: str
    conversationId: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    sources: Optional[List[Source]] = None


class ChatRequest(BaseModel):
    query: str
    conversationId: Optional[str] = None
    topK: Optional[int] = 5
    fileIds: Optional[List[str]] = None  # For filtering to specific files


class ChatResponse(BaseModel):
    conversationId: str
    answer: str
    sources: List[Source]
    processingTime: float


class SystemStatus(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, Any]
    resources: Dict[str, float]


class SettingsModel(BaseModel):
    general: Dict[str, Any]
    processing: Dict[str, int]
    retrieval: Dict[str, Any]
    models: Dict[str, str]
