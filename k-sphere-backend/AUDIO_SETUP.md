> [!NOTE]
> Refreshed on 2026-05-25 for clarity and consistency.
> Where applicable, frontend commands use `npm` (`npm install`, `npm run dev`, `npm run build`, `npm run lint`).

# Audio Processing Setup Guide

K-Sphere now supports audio file processing (MP3, WAV, M4A, FLAC) with automatic transcription using OpenAI's Whisper model.

## Installation

### 1. Install Whisper

```bash
cd k-sphere-backend
pip install openai-whisper
```

### 2. Install FFmpeg (Required by Whisper)

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

### 3. Verify Installation

```bash
python -c "import whisper; print('Whisper installed successfully!')"
```

## Supported Audio Formats

- `.mp3` - MP3 audio files
- `.wav` - WAV audio files  
- `.m4a` - M4A audio files (iPhone voice memos)
- `.flac` - FLAC lossless audio

## How It Works

1. **Upload Audio** - Drop audio files into the Knowledge Base
2. **Transcription** - Whisper automatically transcribes speech to text
3. **Indexing** - Transcribed text is chunked and indexed for search
4. **Query** - Ask questions about the audio content in Chat

## Example Use Cases

- 📝 Meeting transcriptions and summaries
- 🎓 Lecture notes and Q&A
- 🎙️ Podcast content search
- 📞 Interview analysis
- 🎵 Song lyrics extraction

## Model Size

The default Whisper model is **"base"** (~140MB). You can change this in `src/services/file_processor.py`:

```python
# Available models: tiny, base, small, medium, large
self.whisper_model = whisper.load_model("base")
```

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39 MB | Fastest | Good |
| base | 74 MB | Fast | Better |
| small | 244 MB | Medium | Good |
| medium | 769 MB | Slow | Very Good |
| large | 1550 MB | Slowest | Best |

## Performance Tips

- **First run**: Model downloads automatically (~140MB for base model)
- **GPU acceleration**: Automatically uses GPU if available
- **Processing time**: ~1-2 minutes per hour of audio (base model)
- **Offline ready**: Once model is downloaded, works completely offline

## Troubleshooting

### "Whisper not installed" error
```bash
pip install openai-whisper
```

### "FFmpeg not found" error
Install FFmpeg using the instructions above

### Out of memory error
Try a smaller model (tiny or base) or use CPU instead of GPU

## Testing Audio Processing

1. Upload a short audio file (1-2 minutes)
2. Wait for processing (check logs)
3. Ask questions about the content in Chat
4. Check Knowledge Base to see transcription chunks

## Example Query

After uploading a meeting recording:
```
"What were the main action items discussed in the meeting?"
```

K-Sphere will search the transcribed text and provide answers with source citations!
---

_This document is part of the K-Sphere documentation set. If you find outdated steps, please open an issue or PR._
