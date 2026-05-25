> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# Audio Features Documentation

## Overview
Enhanced audio processing with timestamp-based indexing and inline audio playback for precise citations.

## Features Implemented

### 1. Timestamp-Based Audio Indexing
Audio files are now processed with word-level timestamps, allowing for precise citation of when specific content was mentioned.

#### How It Works:
- Whisper transcribes audio with `word_timestamps=True`
- Audio is chunked while preserving timestamp information
- Each chunk stores:
  - `start_time`: When the chunk begins (seconds)
  - `end_time`: When the chunk ends (seconds)
  - `timestamp`: Human-readable format (MM:SS or HH:MM:SS)

#### Example Metadata:
```json
{
  "file_id": "abc123",
  "file_name": "interview.mp3",
  "chunk_index": 0,
  "content": "In this interview, we discuss...",
  "type": "audio",
  "duration": 1245.5,
  "start_time": 45.2,
  "end_time": 78.9,
  "timestamp": "00:45 - 01:18"
}
```

### 2. Inline Audio Player
Audio files can now be played directly in the knowledge base page without downloading.

#### Features:
- HTML5 audio player with controls (play, pause, volume, seek)
- Shows waveform visualization
- Displays current time and duration
- Seekable timeline

#### Location:
Knowledge Base page → Click on audio file → Audio player appears in details dialog

### 3. Smart Audio Citations
When citing audio sources in chat, the system now shows:
- **Timestamp badge**: Shows exact time range (e.g., "02:15 - 03:42")
- **Clickable links**: Opens audio file with timestamp
- **Multiple sections**: If multiple chunks are referenced, shows count

#### Example Citation Display:
```
Sources:
[🎤 interview.mp3 02:15 - 03:42 (3 sections) 87% 🔗]
```

### 4. Audio Time Jump
Clicking on an audio citation opens the file at the specific timestamp where the information was mentioned.

- Uses HTML5 audio time fragment: `#t=135` (jumps to 2:15)
- Works in browser's native audio player
- Precise to the second

## Multilingual Support

### Supported Languages:
Whisper supports 99+ languages including:
- English
- Hindi (hi)
- Bengali (bn)
- Telugu (te)
- Tamil (ta)
- Marathi (mr)
- Gujarati (gu)
- Kannada (kn)
- Malayalam (ml)
- Punjabi (pa)
- Urdu (ur)
- And many more...

### Language Detection:
- **Automatic**: Whisper auto-detects language by default
- **Accurate**: Works well for mixed-language content
- **No Configuration Needed**: Just upload and process

## Technical Implementation

### Backend Changes

#### File: `src/services/file_processor.py`

**New Method: `_chunk_audio_with_timestamps()`**
```python
def _chunk_audio_with_timestamps(self, segments: List[Dict]) -> List[Dict[str, Any]]:
    """Create chunks from audio segments with timestamp information"""
    # Groups Whisper segments into meaningful chunks
    # Preserves start/end times for each chunk
    # Respects chunk_size configuration
```

**New Method: `_format_timestamp()`**
```python
def _format_timestamp(self, seconds: float) -> str:
    """Format seconds to MM:SS or HH:MM:SS"""
    # Converts decimal seconds to readable format
    # Handles hours if needed
```

**Updated: `process_audio()`**
```python
async def process_audio(self, file_path: str, file_id: str) -> Dict[str, Any]:
    # Now uses word_timestamps=True
    result = model.transcribe(file_path, word_timestamps=True)
    
    # Creates timestamp-aware chunks
    chunks_with_timestamps = self._chunk_audio_with_timestamps(segments)
    
    # Stores timestamp metadata
    metadatas.append({
        "start_time": chunk_info["start"],
        "end_time": chunk_info["end"],
        "timestamp": f"{self._format_timestamp(start)} - {self._format_timestamp(end)}"
    })
```

### Frontend Changes

#### File: `app/knowledge-base/page.tsx`

**Added Audio Player:**
```tsx
{selectedFile.type === "audio" && (
  <div className="rounded-lg border border-border bg-muted p-4">
    <h4 className="mb-3 text-sm font-semibold text-foreground">Audio Player</h4>
    <audio 
      controls 
      className="w-full"
      src={`${BACKEND_URL}/api/knowledge-base/${selectedFile.id}/view`}
    >
      Your browser does not support the audio element.
    </audio>
  </div>
)}
```

#### File: `app/chat/page.tsx`

**Updated Source Interface:**
```typescript
interface Message {
  sources?: Array<{
    name: string
    type: string
    relevance: number
    timestamp?: string      // "MM:SS - MM:SS"
    startTime?: number      // Decimal seconds
    endTime?: number        // Decimal seconds
  }>
}
```

**Enhanced Citation Display:**
```tsx
// Shows timestamp for audio sources
{group.timestamps.length > 0 && (
  <span className="text-xs font-mono text-primary">
    {group.timestamps[0].timestamp}
  </span>
)}

// Clicks jump to timestamp
onClick={() => {
  if (group.type === 'audio' && group.timestamps.length > 0) {
    const firstTimestamp = group.timestamps[0]
    window.open(`${url}#t=${Math.floor(firstTimestamp.startTime)}`, '_blank')
  }
}}
```

## Usage Examples

### Example 1: Upload Hindi Audio
```bash
# Upload a Hindi podcast
curl -X POST http://localhost:8000/api/knowledge-base/upload \
  -F "file=@hindi_podcast.mp3"

# System automatically:
# 1. Detects Hindi language
# 2. Transcribes with timestamps
# 3. Creates searchable chunks
# 4. Indexes in vector database
```

### Example 2: Query with Timestamp Citation
```
User: "What did the speaker say about AI ethics?"

Assistant: "The speaker emphasizes transparency in model decisions and
responsible dataset use (source: hindi_podcast.mp3 at 07:42)."

Citation:
📎 hindi_podcast.mp3 [07:42 - 08:10]

To review this segment directly, open:
audio/hindi_podcast.mp3#t=462
```
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
