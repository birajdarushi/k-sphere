> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# Chat Features Implementation

## Overview
Implemented three major features to enhance the chat experience:
1. **Image Upload & Vision Chat** - Upload images and ask questions about them
2. **Voice Recording** - Record voice, transcribe to text automatically
3. **File Selection Modal** - Choose specific files to chat with

## Features Implemented

### 1. 📷 Image Upload in Chat

Upload images directly in chat and ask questions about them using vision models or OCR.

#### How It Works:
- Click the **image icon** (📷) in chat input
- Select an image from your device
- Image preview appears above input
- Type your question (or leave blank for default "What can you tell me about this image?")
- Send to get analysis

#### Backend Processing:
1. **Try vision model first** (LLaVA if available via Ollama)
2. **Fallback to OCR** (Tesseract) if vision model unavailable
   - Extracts text from image
   - Uses RAG on extracted text + knowledge base
3. **Saves conversation** with image indicator

#### Example:
```
User: [Image] What does this diagram show?
Assistant: Based on the architecture diagram, this shows a microservices design...
```

### 2. 🎤 Voice Recording & Transcription

Record your voice and have it automatically transcribed into text using Whisper.

#### How It Works:
- Click the **mic icon** (🎤) to start recording
- Icon turns **red** while recording
- Click again to stop recording
- Audio automatically transcribed
- Transcription fills input field
- Press Send to ask the question

#### Backend Processing:
1. Browser captures audio via MediaRecorder API
2. Audio sent to `/api/chat/transcribe` endpoint
3. Whisper transcribes audio (supports 99+ languages including Hindi)
4. Returns transcribed text
5. Frontend auto-fills input

#### Features:
- **Multilingual**: Supports Hindi, English, and all Whisper languages
- **Fast**: Uses Whisper base model for quick transcription
- **No storage**: Audio deleted after transcription

### 3. 🗂️ File Selection Modal

Choose specific files from your knowledge base to focus the conversation on targeted content.

#### How It Works:
- Click **"Select Files"** button in chat header (top right)
- Modal opens showing all uploaded files
- Check files you want to include
- Click "Apply" to activate filtering
- Button shows `"N files selected"` when active

#### Features:
- **File Preview**: See file name, type, size, chunks, upload date
- **Batch Selection**: "Select All" or "Clear" buttons
- **Visual Indicators**: Checkboxes, badges, file icons
- **Persistent**: Selection stays active until changed
- **Optional**: Empty selection = search all files (default behavior)

#### Backend Filtering:
- Passes `fileIds` array to chat endpoint
- Vector search filtered by file IDs using ChromaDB's `where` clause
- Only retrieves chunks from selected files
- Works with streaming and non-streaming chat

### 4. 🎯 Complete RAG Pipeline Updates

Updated the entire RAG pipeline to support these features:

#### Vector Search Service:
```python
def search_all_collections(
    query_embeddings,
    n_results=5,
    file_ids=None  # New parameter
):
    # Filters by file_ids if provided
    where_clause = {"file_id": {"$in": file_ids}} if file_ids else None
```

#### Chat Endpoints:
Both `/api/chat` and `/api/chat/stream` now accept:
```json
{
  "query": "Your question",
  "conversationId": "abc123",
  "fileIds": ["file1", "file2"]  // Optional
}
```

#### Ollama Service:
```python
async def generate_with_image(model, prompt, image_base64):
    # Sends image to vision model
    # Returns analyzed content
```

## Technical Implementation

### Frontend Files Modified

#### `app/chat/page.tsx`
**New State Variables:**
```typescript
const [selectedImage, setSelectedImage] = useState<File | null>(null)
const [selectedImagePreview, setSelectedImagePreview] = useState<string | null>(null)
const [isRecording, setIsRecording] = useState<boolean>(false)
const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
const [selectedFiles, setSelectedFiles] = useState<string[]>([])
const [showFileSelector, setShowFileSelector] = useState<boolean>(false)
const imageInputRef = useRef<HTMLInputElement>(null)
```

**New Functions:**
- `handleImageUpload()` - Handles image selection and preview
- `handleImageSend()` - Sends image with query to backend
- `handleVoiceRecording()` - Starts/stops recording, transcribes
- `clearImage()` - Removes selected image
- File selector modal integration

**UI Updates:**
- Image button triggers file input
- Mic button with recording indicator (red when active)
- Image preview with remove button
- File selector button in header
- Hidden file input for image upload

#### `components/file-selector-dialog.tsx` (NEW)
Complete file selection modal with:
- File list from knowledge base
- Checkboxes for selection
- Select All / Clear actions
- File metadata display
- Apply/Cancel buttons

### Backend Files Modified

#### `src/routes/chat.py`
**New Endpoints:**

1. **POST `/api/chat/transcribe`**
```python
async def transcribe_audio(file: UploadFile):
    # Saves audio temporarily
    # Loads Whisper model
    # Transcribes audio
    # Returns { transcription, language }
```

2. **POST `/api/chat/image`**
```python
async def chat_with_image(
    file: UploadFile,
    query: str,
    conversationId: Optional[str]
):
    # Tries vision model (LLaVA)
    # Falls back to OCR + RAG
    # Saves conversation
    # Returns answer with sources
```

**Updated Endpoints:**
- `/api/chat` - Now accepts `fileIds` parameter
- `/api/chat/stream` - Now accepts `fileIds` parameter

#### `src/services/ollama_service.py`
**New Method:**
```python
async def generate_with_image(model: str, prompt: str, image_base64: str):
    # Calls Ollama vision model
    # Passes base64 encoded image
    # Returns vision analysis
```

#### `src/services/vector_db_service.py`
**Updated Method:**
```python
def search_all_collections(
    query_embeddings,
    n_results=5,
    file_ids=None  # NEW
):
    # Builds where clause if file_ids provided
    where_clause = {"file_id": {"$in": file_ids}} if file_ids else None
    # Passes to ChromaDB query
```

#### `src/models/schemas.py`
**Updated Schema:**
```python
class ChatRequest(BaseModel):
    query: str
    conversationId: Optional[str] = None
    topK: Optional[int] = 5
    fileIds: Optional[List[str]] = None  # NEW
```

## Usage Examples

### Example 1: Voice Question
1. Click 🎤 mic button
2. Speak: "What are the key features of the ML model?"
3. Click 🎤 again to stop
4. Text appears: "What are the key features of the ML model?"
5. Click Send

### Example 2: Image Analysis with Vision Model
1. Click 📷 image button
2. Select architecture diagram
3. Type: "Explain this system design"
4. Send
5. Get: "This shows a microservices architecture with..."

### Example 3: Image Analysis with OCR Fallback
1. Upload image with text (no vision model)
2. OCR extracts text from image
3. RAG searches knowledge base + extracted text
4. Returns relevant answer with citations

### Example 4: Chat with Specific Files
1. Click "Select Files" in header
2. Check: "ML_Paper.pdf" and "Model_Docs.pdf"
3. Click "Apply (2 selected)"
4. Ask: "What's the accuracy?"
5. Only searches those 2 files

### Example 5: Hindi Voice Input
1. Click 🎤 mic
2. Speak in Hindi: "मशीन लर्निंग क्या है?"
3. Stop recording
4. Text appears in Hindi
5. Get answer from RAG system

## Error Handling

### Image Upload:
- **No Vision Model**: Fallback to OCR + RAG
- **No OCR**: Returns error message
- **Empty Image**: "Couldn't extract text"

### Voice Recording:
- **No Microphone**: Alert user to check permissions
- **Whisper Not Installed**: Returns 501 error with install instructions
- **Transcription Fails**: Logs error, shows message

### File Selection:
- **No Files Uploaded**: Modal shows empty state
- **Invalid File IDs**: Vector search returns no results
- **Network Error**: Handled gracefully with error messages

## Requirements

### Backend:
```bash
pip install openai-whisper  # For voice transcription
pip install Pillow          # For image processing
pip install pytesseract     # For OCR fallback
```

### Ollama (Optional):
```bash
ollama pull llava  # For vision model
```

### Frontend:
- Modern browser with MediaRecorder API support
- Microphone permissions for voice recording
- File input support for images

## Performance Considerations

### Voice Recording:
- Uses base Whisper model for speed
- Audio deleted immediately after transcription
- No storage overhead

### Image Processing:
- Temporary files cleaned up after processing
- Base64 encoding for vision models
- OCR as lightweight fallback

### File Filtering:
- ChromaDB native filtering (very fast)
- No post-processing needed
- Reduces search space for faster responses

## Future Enhancements

### Possible Additions:
1. **Video Upload**: Process video frames + audio
2. **Multiple Images**: Compare or analyze multiple images
3. **Image Generation**: Generate images from text
4. **Voice Output**: Text-to-speech for responses
5. **File Upload in Modal**: Add files directly from selector
6. **Smart File Suggestions**: Auto-select relevant files based on query

## Testing Checklist

- [ ] Upload PNG image and ask question
- [ ] Upload JPEG image with text (OCR test)
- [ ] Record voice in English
- [ ] Record voice in Hindi
- [ ] Select 1 file and verify filtered search
- [ ] Select multiple files
- [ ] Clear file selection
- [ ] Upload image while files selected
- [ ] Voice recording while files selected
- [ ] Test with vision model (if LLaVA installed)
- [ ] Test without vision model (OCR fallback)

## Troubleshooting

### "Whisper not installed" error:
```bash
cd k-sphere-backend
./venv/bin/pip install openai-whisper
```

### "Could not access microphone":
- Check browser permissions
- Ensure HTTPS or localhost
- Try different browser

### "Vision model failed":
- Normal if LLaVA not installed
- System falls back to OCR automatically
- To enable: `ollama pull llava`

### Images not uploading:
- Check file size (default 100MB limit)
- Verify image format (PNG, JPEG supported)
- Check backend logs for errors

### File selection not working:
- Ensure files are uploaded first
- Check knowledge base page shows files
- Verify backend `/api/knowledge-base` endpoint working
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
