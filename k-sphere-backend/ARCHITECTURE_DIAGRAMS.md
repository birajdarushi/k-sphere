> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# System-Wide RAG Indexing Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              K-SPHERE FRONTEND                              │
│                         (React/Next.js Application)                         │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    System Indexer UI Page                            │  │
│  │  • Permission Manager    • Exclusion Manager                         │  │
│  │  • Indexing Controls     • Progress Monitor                          │  │
│  │  • Auto-Monitor Toggle   • Statistics Dashboard                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    │ REST API (HTTP/JSON)                   │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              K-SPHERE BACKEND                               │
│                         (FastAPI/Python Application)                        │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    API Routes (system_indexer.py)                    │  │
│  │  • /permitted-paths      • /exclusions                               │  │
│  │  • /start               • /stop                                      │  │
│  │  • /status              • /monitoring/*                              │  │
│  └──────────────────┬───────────────────────────────────────────────────┘  │
│                     │                                                       │
│                     ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  System Indexer Service                             │   │
│  │  • Permission Management   • Path Validation                        │   │
│  │  • Exclusion Filtering     • File Discovery                         │   │
│  │  • Hash-based Change Detection                                      │   │
│  │  • Concurrent Processing (5 files at once)                          │   │
│  │  • Progress Tracking                                                │   │
│  └────────────┬──────────────────────────────┬─────────────────────────┘   │
│               │                              │                             │
│               ▼                              ▼                             │
│  ┌─────────────────────────┐    ┌──────────────────────────────────────┐  │
│  │  File System Watcher    │    │      File Processor Service          │  │
│  │  (fs_watcher.py)        │    │      (file_processor.py)             │  │
│  │                         │    │                                      │  │
│  │  • Watchdog Library     │    │  • PDF Extraction (pypdf)            │  │
│  │  • Real-time Monitoring │    │  • DOCX Extraction (python-docx)     │  │
│  │  • Event Handling       │    │  • Image OCR (pytesseract)           │  │
│  │  • Background Processing│    │  • Audio Transcription (whisper)     │  │
│  │  • Change Detection     │    │  • Code/Text Processing              │  │
│  └────────────┬────────────┘    └───────────────┬──────────────────────┘  │
│               │                                  │                         │
│               │                                  ▼                         │
│               │                     ┌──────────────────────────────────┐   │
│               │                     │    Ollama Service Integration    │   │
│               │                     │    (ollama_service.py)           │   │
│               │                     │                                  │   │
│               │                     │  • Text Embeddings               │   │
│               │                     │  • LLM Queries                   │   │
│               │                     │  • Model Management              │   │
│               │                     └──────────────┬───────────────────┘   │
│               │                                    │                       │
│               ▼                                    ▼                       │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                         Storage Layer                              │   │
│  │                                                                    │   │
│  │  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────┐  │   │
│  │  │  SQLite DB      │    │   ChromaDB       │    │  File System │  │   │
│  │  │  (k-sphere.db)  │    │  (vectordb/)     │    │  (uploads/)  │  │   │
│  │  │                 │    │                  │    │              │  │   │
│  │  │  • File Metadata│    │  • Embeddings    │    │  • Original  │  │   │
│  │  │  • Settings     │    │  • Vectors       │    │    Files     │  │   │
│  │  │  • Conversations│    │  • Collections   │    │  • Cache     │  │   │
│  │  └─────────────────┘    └──────────────────┘    └──────────────┘  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     ▲
                                     │
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                              USER'S FILE SYSTEM                             │
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐     │
│  │  ~/Documents     │    │  ~/Desktop       │    │  ~/Projects      │     │
│  │  (Permitted)     │    │  (Permitted)     │    │  (Permitted)     │     │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘     │
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐     │
│  │  /System         │    │  node_modules/   │    │  .git/           │     │
│  │  (Excluded)      │    │  (Excluded)      │    │  (Excluded)      │     │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INDEXING WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  1. USER ACTION
     │
     ├─> Add Permitted Path ────────────────┐
     │                                       │
     └─> Start Indexing                     │
         │                                   │
         ▼                                   ▼
  2. PERMISSION CHECK              3. FILE SYSTEM WATCH
     │                                       │
     • Path exists?                          • Monitor for changes
     • Readable?                             • Detect new files
     • Not excluded?                         • Detect modifications
     │                                       • Detect deletions
     ▼                                       │
  4. FILE DISCOVERY                          ▼
     │                              5. CHANGE DETECTION
     • Walk directories                      │
     • Filter by extensions                  • Compute MD5 hash
     • Apply exclusions                      • Compare with DB
     • Queue for processing                  • Skip if unchanged
     │                                       │
     ▼                                       ▼
  6. CONTENT EXTRACTION ◄───────────────────┘
     │
     ├─> PDF ──> Extract text with pypdf
     ├─> DOCX ─> Extract text with python-docx
     ├─> Image ─> OCR with pytesseract
     ├─> Audio ─> Transcribe with whisper
     └─> Code ──> Read as text
     │
     ▼
  7. TEXT CHUNKING
     │
     • Split into chunks (512 tokens)
     • Overlap chunks (50 tokens)
     • Preserve context
     │
     ▼
  8. EMBEDDING GENERATION
     │
     • Send to Ollama
     • Generate vectors (nomic-embed-text)
     • Receive embeddings
     │
     ▼
  9. STORAGE
     │
     ├─> ChromaDB ─────> Store vectors
     │                   Store metadata
     │                   Create index
     │
     └─> SQLite ───────> Store file info
                         Update status
                         Record hash
     │
     ▼
 10. COMPLETION
     │
     • Update statistics
     • Notify frontend
     • Ready for queries
```

## Query Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            QUERY WORKFLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  1. USER QUERY
     │
     "What are the key findings in my research papers?"
     │
     ▼
  2. QUERY EMBEDDING
     │
     • Send to Ollama
     • Generate query vector
     │
     ▼
  3. VECTOR SEARCH
     │
     • Query ChromaDB
     • Find similar vectors (Top-K)
     • Apply similarity threshold
     │
     ▼
  4. CONTEXT RETRIEVAL
     │
     • Get matching chunks
     • Retrieve metadata
     • Rank by relevance
     │
     ▼
  5. CONTEXT ASSEMBLY
     │
     • Combine chunks
     • Add source information
     • Format for LLM
     │
     ▼
  6. LLM GENERATION
     │
     • Build prompt with context
     • Send to Ollama LLM
     • Stream response
     │
     ▼
  7. RESPONSE DELIVERY
     │
     • Include answer
     • Include sources
     • Show confidence
     │
     ▼
  8. USER RECEIVES ANSWER
     │
     "Based on your research papers in ~/Documents/Research/...,
      the key findings are: [answer with citations]"
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       COMPONENT INTERACTION FLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

Frontend UI
    │
    │ 1. Add Path Request
    ├──────────────────────────────────────────┐
    │                                           │
    │                                           ▼
    │                                    API Routes
    │                                           │
    │                                           │ 2. Validate & Store
    │                                           ├──────────────────┐
    │                                           │                  │
    │                                           ▼                  ▼
    │                                    System Indexer    Database Service
    │                                           │                  │
    │ 3. Start Indexing                        │                  │
    ├──────────────────────────────────────────┤                  │
    │                                           │                  │
    │                                           ▼                  │
    │                                    File Discovery            │
    │                                           │                  │
    │                                           │ 4. Queue Files   │
    │                                           ▼                  │
    │                                    File Processor            │
    │                                           │                  │
    │                                           │ 5. Extract Text  │
    │                                           ▼                  │
    │                                    Ollama Service            │
    │                                           │                  │
    │                                           │ 6. Generate      │
    │                                           │    Embeddings    │
    │                                           ▼                  │
    │                                    Vector DB Service         │
    │                                           │                  │
    │                                           │ 7. Store Vectors │
    │                                           ├──────────────────┤
    │                                           │                  │
    │ 8. Progress Updates                       │ 8. Store Metadata│
    ◄───────────────────────────────────────────┴──────────────────┘
    │
    │ 9. Display Status
    └─> User sees progress, statistics, completion
```

## Permission & Security Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SECURITY & PERMISSION MODEL                           │
└─────────────────────────────────────────────────────────────────────────────┘

User Action: Add Path "/Users/john/Documents"
    │
    ▼
┌─────────────────────────────────┐
│  PERMISSION VALIDATION          │
│                                 │
│  1. Path exists?           ✓    │
│  2. Readable?              ✓    │
│  3. Not in exclusion list? ✓    │
│  4. User confirmed?        ✓    │
└────────────┬────────────────────┘
             │
             ▼ GRANTED
┌─────────────────────────────────┐
│  PERMITTED PATHS STORAGE        │
│                                 │
│  Stored in: k-sphere.db         │
│  Key: "system_indexer"          │
│  Value: {                       │
│    "permitted_paths": [         │
│      "/Users/john/Documents"    │
│    ],                           │
│    "exclusion_patterns": [...]  │
│  }                              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  ACCESS CONTROL                 │
│                                 │
│  Before accessing any file:     │
│  1. Check if path within        │
│     permitted paths      ✓      │
│  2. Check exclusions     ✓      │
│  3. Check file exists    ✓      │
│  4. Check readable       ✓      │
│                                 │
│  Action: READ ONLY              │
└─────────────────────────────────┘

SECURITY GUARANTEES:
• No external network calls
• No file modifications
• No file deletions
• Explicit permission required
• User can revoke anytime
• All data stored locally
• Complete transparency
```

---

This architecture provides:
- **Scalability**: Handles thousands of files efficiently
- **Security**: Permission-based access control
- **Privacy**: All processing happens locally
- **Reliability**: Error handling at every layer
- **Performance**: Concurrent processing and caching
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new file types or features
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
