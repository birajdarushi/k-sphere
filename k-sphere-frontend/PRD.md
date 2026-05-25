> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# K-Sphere AI - Product Requirements Document

## Executive Summary

K-Sphere AI is an offline-first multimodal RAG (Retrieval-Augmented Generation) system designed to run locally on Mac M1 with 8GB RAM. The system ingests documents, images, and audio files, processes them using local AI models (Ollama), and provides intelligent search and chat capabilities with source citations.

---

## System Architecture

### Technology Stack

**Frontend:**
- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS v4
- shadcn/ui components
- SWR for data fetching

**Backend:**
- Next.js API Routes
- Ollama (Local LLM - optimized for Mac M1)
- Local Vector Database (ChromaDB or similar)
- Local Speech-to-Text (Whisper.cpp)
- Local Image Processing (CLIP embeddings)

**Storage:**
- Local file system for documents
- SQLite or similar for metadata
- Vector database for embeddings

---

## API Specification

### Base URL
\`\`\`
http://localhost:3000/api
\`\`\`

### Authentication
All endpoints are local-only. No authentication required for MVP.

---

## API Endpoints

### 1. System Status

#### GET `/api/system-status`

**Description:** Returns the health status of all system components.

**Response:**
\`\`\`typescript
{
  status: "online" | "offline" | "partial",
  timestamp: string,
  services: {
    ollama: {
      status: "running" | "stopped" | "error",
      model: string,
      version: string
    },
    vectorDb: {
      status: "connected" | "disconnected",
      collections: number
    },
    whisper: {
      status: "available" | "unavailable",
      model: string
    },
    embeddings: {
      status: "available" | "unavailable",
      model: string
    }
  },
  resources: {
    cpuUsage: number,
    memoryUsage: number,
    diskSpace: number
  }
}
\`\`\`

**Frontend Integration:**
- Poll this endpoint every 10 seconds
- Update the "System Online" indicator in the sidebar
- Show detailed status in settings page

---

### 2. Knowledge Base Management

#### GET `/api/knowledge-base`

**Description:** Returns list of all indexed files with metadata.

**Query Parameters:**
- `type` (optional): Filter by file type (document, image, audio)
- `status` (optional): Filter by status (indexed, processing, error)
- `search` (optional): Search by filename

**Response:**
\`\`\`typescript
{
  files: [
    {
      id: string,
      name: string,
      type: "document" | "image" | "audio",
      size: number,
      uploadedAt: string,
      status: "indexed" | "processing" | "error",
      chunks: number,
      path: string,
      metadata: {
        pages?: number,
        duration?: number,
        dimensions?: { width: number, height: number }
      }
    }
  ],
  total: number
}
\`\`\`

**Frontend Integration:**
- Use SWR with 5-second refresh interval
- Display in Knowledge Base page
- Update Recent Activity when new files appear

---

#### POST `/api/knowledge-base`

**Description:** Upload new files for indexing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: FormData with files

**Response:**
\`\`\`typescript
{
  success: boolean,
  files: [
    {
      id: string,
      name: string,
      status: "processing"
    }
  ]
}
\`\`\`

**Frontend Integration:**
- Show upload progress
- Trigger SWR revalidation after upload
- Add to Recent Activity feed

---

#### GET `/api/knowledge-base/[id]`

**Description:** Get detailed information about a specific file.

**Response:**
\`\`\`typescript
{
  id: string,
  name: string,
  type: "document" | "image" | "audio",
  size: number,
  uploadedAt: string,
  status: "indexed" | "processing" | "error",
  chunks: number,
  path: string,
  preview: string,
  metadata: object,
  chunks_detail: [
    {
      id: string,
      content: string,
      page?: number,
      timestamp?: number
    }
  ]
}
\`\`\`

**Frontend Integration:**
- Display in document preview modal
- Show chunk breakdown

---

#### DELETE `/api/knowledge-base/[id]`

**Description:** Delete a file and its embeddings.

**Response:**
\`\`\`typescript
{
  success: boolean,
  message: string
}
\`\`\`

**Frontend Integration:**
- Trigger SWR revalidation after deletion
- Remove from UI optimistically

---

### 3. Knowledge Base Statistics

#### GET `/api/knowledge-base/stats`

**Description:** Returns aggregated statistics about the knowledge base.

**Response:**
\`\`\`typescript
{
  totalFiles: number,
  totalChunks: number,
  byType: {
    documents: number,
    images: number,
    audio: number
  },
  storageUsed: number,
  lastUpdated: string
}
\`\`\`

**Frontend Integration:**
- Display in Dashboard cards
- Update in real-time with SWR

---

### 4. Chat Interface

#### POST `/api/chat`

**Description:** Send a text query and receive an AI-generated response with sources.

**Request:**
\`\`\`typescript
{
  query: string,
  conversationId?: string,
  topK?: number
}
\`\`\`

**Response:**
\`\`\`typescript
{
  conversationId: string,
  answer: string,
  sources: [
    {
      fileId: string,
      fileName: string,
      chunkId: string,
      content: string,
      relevanceScore: number,
      metadata: {
        page?: number,
        timestamp?: number
      }
    }
  ],
  processingTime: number
}
\`\`\`

**Frontend Integration:**
- Display answer in chat interface
- Show sources with relevance scores
- Store conversation in localStorage when backend is online
- Save to backend for persistence

---

#### POST `/api/chat/multimodal`

**Description:** Send a multimodal query (text + image or audio).

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `query` (text)
  - `file` (image or audio file)
  - `conversationId` (optional)

**Response:**
\`\`\`typescript
{
  conversationId: string,
  answer: string,
  sources: [
    {
      fileId: string,
      fileName: string,
      chunkId: string,
      content: string,
      relevanceScore: number
    }
  ],
  processingTime: number
}
\`\`\`

**Frontend Integration:**
- Handle file uploads from chat interface
- Display multimodal queries in chat history
- Show processing indicator

---

#### GET `/api/chat/history`

**Description:** Retrieve chat conversation history.

**Query Parameters:**
- `conversationId` (optional): Get specific conversation
- `limit` (optional): Number of messages to return

**Response:**
\`\`\`typescript
{
  conversations: [
    {
      id: string,
      messages: [
        {
          id: string,
          role: "user" | "assistant",
          content: string,
          timestamp: string,
          sources?: Array<Source>
        }
      ],
      createdAt: string,
      updatedAt: string
    }
  ]
}
\`\`\`

**Frontend Integration:**
- Load on chat page mount
- Merge with localStorage data
- Display in conversation history

---

### 5. Search

#### POST `/api/search`

**Description:** Perform a search across the knowledge base with live suggestions.

**Request:**
\`\`\`typescript
{
  query: string,
  type?: "all" | "document" | "image" | "audio",
  limit?: number
}
\`\`\`

**Response:**
\`\`\`typescript
{
  results: [
    {
      fileId: string,
      fileName: string,
      type: "document" | "image" | "audio",
      snippet: string,
      relevanceScore: number,
      metadata: object
    }
  ],
  total: number,
  processingTime: number
}
\`\`\`

**Frontend Integration:**
- Debounce search input (300ms)
- Show suggestions dropdown while typing
- Display full results on submit

---

### 6. Settings

#### GET `/api/settings`

**Description:** Get current system settings.

**Response:**
\`\`\`typescript
{
  general: {
    watchDirectory: string,
    autoIndex: boolean
  },
  processing: {
    chunkSize: number,
    chunkOverlap: number
  },
  retrieval: {
    topK: number,
    similarityThreshold: number
  },
  models: {
    llm: string,
    embedding: string,
    whisper: string
  }
}
\`\`\`

---

#### PUT `/api/settings`

**Description:** Update system settings.

**Request:**
\`\`\`typescript
{
  general?: {
    watchDirectory?: string,
    autoIndex?: boolean
  },
  processing?: {
    chunkSize?: number,
    chunkOverlap?: number
  },
  retrieval?: {
    topK?: number,
    similarityThreshold?: number
  },
  models?: {
    llm?: string,
    embedding?: string,
    whisper?: string
  }
}
\`\`\`

**Response:**
\`\`\`typescript
{
  success: boolean,
  settings: Settings
}
\`\`\`

---

### 7. Ingestion

#### POST `/api/ingestion/trigger`

**Description:** Manually trigger ingestion of files from the watch directory.

**Response:**
\`\`\`typescript
{
  success: boolean,
  filesFound: number,
  message: string
}
\`\`\`

**Frontend Integration:**
- Trigger from settings page
- Show progress indicator
- Revalidate knowledge base after completion

---

## Data Models

### File Metadata
\`\`\`typescript
interface FileMetadata {
  id: string
  name: string
  type: "document" | "image" | "audio"
  size: number
  path: string
  uploadedAt: string
  status: "indexed" | "processing" | "error"
  chunks: number
  metadata: {
    pages?: number
    duration?: number
    dimensions?: { width: number, height: number }
    [key: string]: any
  }
}
\`\`\`

### Chat Message
\`\`\`typescript
interface ChatMessage {
  id: string
  conversationId: string
  role: "user" | "assistant"
  content: string
  timestamp: string
  sources?: Source[]
  attachments?: {
    type: "image" | "audio"
    url: string
  }[]
}
\`\`\`

### Source Citation
\`\`\`typescript
interface Source {
  fileId: string
  fileName: string
  chunkId: string
  content: string
  relevanceScore: number
  metadata: {
    page?: number
    timestamp?: number
    [key: string]: any
  }
}
\`\`\`

---

## Backend Implementation Requirements

### Ollama Integration

**Model Selection:**
- **LLM:** `llama3.2:3b` or `mistral:7b` (optimized for 8GB RAM)
- **Embeddings:** `nomic-embed-text` (efficient for RAG)

**Configuration:**
\`\`\`bash
# Install Ollama
brew install ollama

# Pull models
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# Start Ollama server
ollama serve
\`\`\`

**API Integration:**
\`\`\`typescript
// Example: Generate embeddings
const response = await fetch('http://localhost:11434/api/embeddings', {
  method: 'POST',
  body: JSON.stringify({
    model: 'nomic-embed-text',
    prompt: 'text to embed'
  })
})

// Example: Generate chat response
const response = await fetch('http://localhost:11434/api/generate', {
  method: 'POST',
  body: JSON.stringify({
    model: 'llama3.2:3b',
    prompt: 'user query with context',
    stream: false
  })
})
\`\`\`

---

### Vector Database

**Recommended:** ChromaDB (lightweight, Python-based)

**Setup:**
\`\`\`bash
pip install chromadb
\`\`\`

**Collections:**
- `documents` - Text chunks from PDFs
- `images` - Image embeddings with descriptions
- `audio` - Transcribed audio chunks

**Schema:**
\`\`\`python
{
  "id": "chunk_id",
  "embedding": [float],
  "metadata": {
    "file_id": "string",
    "file_name": "string",
    "chunk_index": int,
    "content": "string",
    "page": int (optional),
    "timestamp": float (optional)
  }
}
\`\`\`

---

### File Processing Pipeline

**1. Document Processing (PDF):**
- Extract text using `pypdf` or `pdfplumber`
- Split into chunks (configurable size/overlap)
- Generate embeddings using Ollama
- Store in vector database

**2. Image Processing:**
- Extract text using OCR (Tesseract)
- Generate image embeddings using CLIP
- Store both text and image embeddings

**3. Audio Processing:**
- Transcribe using Whisper.cpp (local)
- Split transcript into chunks
- Generate embeddings
- Store with timestamp metadata

---

### Query Processing

**1. Text Query:**
\`\`\`
User Query → Generate Embedding → Vector Search → Retrieve Top K → 
Format Context → Send to Ollama → Generate Answer → Return with Sources
\`\`\`

**2. Image Query:**
\`\`\`
User Image → Generate Image Embedding → Vector Search (image collection) → 
Retrieve Similar Images → Extract Context → Generate Answer
\`\`\`

**3. Audio Query:**
\`\`\`
User Audio → Transcribe with Whisper → Generate Embedding → 
Vector Search → Retrieve Context → Generate Answer
\`\`\`

---

## Frontend State Management

### SWR Configuration

\`\`\`typescript
// Global SWR config
const swrConfig = {
  refreshInterval: 5000, // 5 seconds for real-time updates
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
  dedupingInterval: 2000
}
\`\`\`

### Local Storage Schema

**Chat History:**
\`\`\`typescript
localStorage.setItem('k-sphere-chat-history', JSON.stringify({
  conversations: [
    {
      id: string,
      messages: ChatMessage[],
      createdAt: string,
      updatedAt: string
    }
  ]
}))
\`\`\`

**Theme Preference:**
\`\`\`typescript
localStorage.setItem('k-sphere-theme', 'light' | 'dark')
\`\`\`

---

## Real-Time Updates

### WebSocket Events (Future Enhancement)

\`\`\`typescript
// Backend emits events
socket.emit('file:uploaded', { fileId, name, status })
socket.emit('file:indexed', { fileId, chunks })
socket.emit('file:error', { fileId, error })

// Frontend listens
socket.on('file:uploaded', (data) => {
  mutate('/api/knowledge-base')
  addToRecentActivity(data)
})
\`\`\`

### Current Implementation (Polling)

- Knowledge Base: Poll every 5 seconds
- System Status: Poll every 10 seconds
- Chat History: Load on mount, save on change

---

## Performance Optimization

### Mac M1 8GB RAM Considerations

**Memory Management:**
- Use streaming for large file processing
- Limit concurrent operations to 2-3
- Clear embeddings cache periodically

**Model Selection:**
- Prefer quantized models (Q4, Q5)
- Use smaller context windows (2048 tokens)
- Batch embedding generation

**Caching Strategy:**
- Cache frequently accessed embeddings
- Store processed chunks in SQLite
- Use LRU cache for search results

---

## Error Handling

### Backend Errors

\`\`\`typescript
{
  error: {
    code: string,
    message: string,
    details?: any
  }
}
\`\`\`

**Error Codes:**
- `OLLAMA_UNAVAILABLE` - Ollama service not running
- `MODEL_NOT_FOUND` - Required model not installed
- `PROCESSING_ERROR` - File processing failed
- `VECTOR_DB_ERROR` - Database connection issue
- `INSUFFICIENT_MEMORY` - Not enough RAM

### Frontend Error Handling

\`\`\`typescript
// Display user-friendly messages
if (error.code === 'OLLAMA_UNAVAILABLE') {
  toast.error('AI service is offline. Please start Ollama.')
}
\`\`\`

---

## Testing Requirements

### Backend Tests

- Unit tests for each API endpoint
- Integration tests for Ollama connection
- Performance tests for embedding generation
- Load tests for concurrent queries

### Frontend Tests

- Component tests for all pages
- Integration tests for API calls
- E2E tests for critical flows (upload, search, chat)

---

## Deployment Checklist

### Prerequisites

- [ ] Ollama installed and running
- [ ] Required models downloaded
- [ ] Vector database initialized
- [ ] Watch directory configured
- [ ] Environment variables set

### Environment Variables

\`\`\`bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Vector Database
VECTOR_DB_PATH=./data/vectordb

# File Storage
WATCH_DIRECTORY=./data/uploads
MAX_FILE_SIZE=100MB

# Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
\`\`\`

---

## Future Enhancements

1. **WebSocket Support** - Real-time updates without polling
2. **Multi-user Support** - Authentication and user-specific knowledge bases
3. **Cloud Sync** - Optional cloud backup for chat history
4. **Advanced Search** - Filters, date ranges, semantic search
5. **Export Features** - Export conversations, search results
6. **Mobile App** - iOS/Android companion app
7. **Plugin System** - Custom data sources and processors

---

## Success Metrics

- **System Uptime:** >99% when backend is running
- **Query Response Time:** <3 seconds for text queries
- **Indexing Speed:** >10 documents per minute
- **Memory Usage:** <6GB RAM under normal load
- **Search Accuracy:** >80% relevance for top 5 results

---

## Support & Maintenance

### Logs Location
- Frontend: Browser console
- Backend: `./logs/k-sphere.log`
- Ollama: `~/.ollama/logs/`

### Troubleshooting

**Issue:** Ollama not responding
- Check if service is running: `ollama list`
- Restart: `ollama serve`

**Issue:** High memory usage
- Reduce chunk size in settings
- Use smaller model (llama3.2:3b instead of 7b)
- Clear vector database cache

**Issue:** Slow indexing
- Reduce concurrent file processing
- Increase chunk size
- Check disk I/O performance

---

## Conclusion

This PRD provides a complete specification for integrating the K-Sphere frontend with a local Ollama-powered backend. The system is designed to run efficiently on Mac M1 with 8GB RAM while providing powerful multimodal RAG capabilities completely offline.
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
