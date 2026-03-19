# Jessica AI - Desktop UI with Voice Commands

## New Features

### 1. ✅ Offline Text-to-Speech (pyttsx3)
**Location:** [jessica/tts/tts_adapter.py](jessica/tts/tts_adapter.py)

- Voice selection support
- Adjustable speaking rate (WPM)
- Async/sync modes
- Singleton engine pattern for performance

**Usage:**
```python
from jessica.tts.tts_adapter import speak, set_voice, set_rate
speak("Hello, I'm Jessica!")
set_rate(175)  # Words per minute
```

### 2. ✅ Offline Speech-to-Text (Whisper-base)
**Location:** [jessica/stt/whisper_stt.py](jessica/stt/whisper_stt.py)

- Uses OpenAI Whisper base model (fast, offline)
- Push-to-talk hotkey: **Ctrl+Shift+Space**
- Real-time audio recording
- Local transcription (no internet required)

**Dependencies:**
```bash
pip install openai-whisper sounddevice soundfile numpy pynput
```

### 3. ✅ Voice Command Listener
**Location:** [jessica/stt/listener.py](jessica/stt/listener.py)

- Wake word detection: **"Jessica"**
- Direct intent parser integration
- Background listener thread
- Example commands:
  - "Jessica, open the terminal"
  - "Jessica, help me with this spreadsheet"
  - "Jessica, take a screenshot"

**Architecture:**
```
Voice → Whisper STT → Listener → Intent Parser → Skill Execution
```

### 4. ✅ CustomTkinter Desktop UI
**Location:** [jessica/ui/desktop_ui.py](jessica/ui/desktop_ui.py)

Replaces the web interface with a modern desktop app:
- Dark theme by default
- Chat window with history
- Voice input button
- Text-to-speech toggle
- Real-time status updates
- Streaming response support

**Fallback:** Uses standard Tkinter if CustomTkinter not installed

## Installation

### Required Dependencies
```bash
# Text-to-Speech
pip install pyttsx3

# Speech-to-Text
pip install openai-whisper sounddevice soundfile numpy pynput

# Modern UI (optional, falls back to tkinter)
pip install customtkinter
```

### Quick Install (All Features)
```bash
pip install pyttsx3 openai-whisper sounddevice soundfile numpy pynput customtkinter
```

## Launch Options

### Desktop UI (Recommended)
```bash
# Windows
start_jessica_desktop.bat

# Or directly
python start_jessica_desktop.pyw
python -m jessica --desktop
```

### CLI Mode
```bash
python -m jessica
```

### Legacy Tkinter UI
```bash
python -m jessica --ui
```

### Web UI (Old)
```bash
python start_jessica_web.pyw
```

## Voice Commands Guide

### Push-to-Talk Workflow
1. Hold **Ctrl+Shift+Space**
2. Say: **"Jessica, [your command]"**
3. Release the hotkey
4. Jessica processes and responds (with TTS if enabled)

### Example Commands
```
"Jessica, open the terminal"
"Jessica, take a screenshot"
"Jessica, help me with this spreadsheet"
"Jessica, what's 25 times 48?"
"Jessica, write Python code to sort a list"
"Jessica, give me a Tokyo travel itinerary"
"Jessica, explain ad hominem fallacy"
```

### Intent Categories Triggered by Voice
- **Terminal commands:** "open terminal", "list files"
- **Screen monitoring:** "screenshot", "see my screen"
- **Spreadsheets:** "spreadsheet", "excel", "csv"
- **Advice:** "how do I...", "help me with..."
- **Code:** "write code", "Python function"
- **Chess:** "play chess"
- **Recipes:** "recipe for..."
- **Chat:** General conversation

## Architecture Flow

### Voice Command Processing
```
1. User holds Ctrl+Shift+Space
2. WhisperSTT records audio
3. User releases → Whisper transcribes
4. VoiceListener detects "Jessica" wake word
5. listener.py calls parse_intent(command)
6. Intent routes to appropriate skill
7. Response returns to UI
8. TTS speaks response (if enabled)
```

### Desktop UI Components
```
JessicaDesktopUI
├── Chat Display (CTkTextbox)
├── Text Input (CTkEntry)
├── Send Button
├── Voice Button (status indicator)
├── TTS Toggle (CTkSwitch)
└── Status Label

Background Threads:
├── VoiceListener (push-to-talk)
├── Message Processing (async)
└── TTS Playback (non-blocking)
```

## Configuration

### TTS Voice Selection
```python
from jessica.tts.tts_adapter import list_voices, set_voice
list_voices()  # Show available voices
set_voice(1)   # Select by index
```

### Whisper Model Options
Edit [jessica/stt/whisper_stt.py](jessica/stt/whisper_stt.py):
```python
# Change model_name in WhisperSTT.__init__
# Options: tiny, base, small, medium, large
# Trade-off: accuracy vs speed
```

### Wake Word Customization
Edit [jessica/stt/listener.py](jessica/stt/listener.py):
```python
# Change wake_word in VoiceListener.__init__
listener = VoiceListener(wake_word="hey assistant")
```

## Troubleshooting

### TTS Not Working
```bash
# Install/reinstall
pip install --upgrade pyttsx3

# Windows: Ensure SAPI5 voices installed
# Linux: Install espeak or festival
sudo apt-get install espeak
```

### Whisper Model Download Slow
- Models download on first use (~150MB for base)
- Cached in `~/.cache/whisper/`
- Use `tiny` for faster setup: `WhisperSTT(model_name="tiny")`

### Push-to-Talk Not Responding
- Check pynput installation: `pip install pynput`
- Try alternative hotkey (edit in whisper_stt.py)
- Run with admin privileges on Windows if needed

### CustomTkinter UI Issues
```bash
# Fallback to standard Tkinter automatically
# Or force install:
pip install customtkinter

# If issues persist, use legacy UI:
python -m jessica --ui
```

## Performance Tips

1. **Whisper Model Selection:**
   - `tiny`: Fastest, basic accuracy
   - `base`: Good balance (recommended)
   - `small`: Better accuracy, slower
   - `medium/large`: Best quality, much slower

2. **TTS Optimization:**
   - Use `async_mode=True` for non-blocking speech
   - Adjust rate for faster/slower speech

3. **Desktop UI:**
   - Disable TTS if not needed (saves CPU)
   - Close when not in use (Whisper keeps model in RAM)

## Migration from Web UI

The desktop UI replaces [start_jessica_web.pyw](start_jessica_web.pyw) with these advantages:
- ✓ Faster startup (no Flask server)
- ✓ Native OS integration
- ✓ Better voice input UX
- ✓ Lower memory footprint
- ✓ No browser required

**Web UI still available** if you prefer browser-based access.

## Next Steps

1. Launch desktop UI: `start_jessica_desktop.bat`
2. Install voice dependencies: `pip install openai-whisper sounddevice pynput`
3. Test voice command: Hold Ctrl+Shift+Space, say "Jessica, hello"
4. Customize TTS voice: Run `python -m jessica.tts.tts_adapter`
5. Explore voice commands with different intents

---

**Status:** All 4 features implemented and integrated
- ✅ pyttsx3 TTS with voice control
- ✅ Whisper STT with push-to-talk
- ✅ Voice listener with intent parser integration
- ✅ CustomTkinter desktop UI (web UI replacement)
