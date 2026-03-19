# Jessica - Natural Voice Setup

Jessica now supports **neural TTS** for natural, emotional speech!

## Quick Setup (Recommended)

Install Coqui TTS for high-quality, human-like voice:

```powershell
# In your AGI directory with virtual environment activated
pip install TTS sounddevice soundfile
```

**First run will download the TTS model (one-time, ~100MB).**

## What You Get

### Neural TTS (Coqui)
- Natural prosody and intonation
- Smooth, human-like speech
- Emotional expression support
- Fully offline after initial model download

### Fallback (pyttsx3)
- Already installed
- Works immediately
- Optimized for clarity (slower rate, female voice)
- Used if Coqui TTS not available

## Testing

Run Jessica and click "TTS Test" or say "Hi Jessica" to hear the new voice!

## Audio Dependencies (Optional)

For better audio playback:
```powershell
pip install sounddevice soundfile
```

Without these, Jessica uses Windows built-in audio (slightly slower).

## Troubleshooting

**Model download fails?**
- Check internet connection for first-time setup
- Model is cached locally after download

**Audio doesn't play?**
- Ensure speakers/headphones are connected
- Check Windows audio settings

**Want to switch models?**
- Edit `jessica/tts/neural_tts.py` and change `model_name`
- See available models: https://github.com/coqui-ai/TTS#released-models
