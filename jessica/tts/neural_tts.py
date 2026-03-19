"""Neural TTS using Coqui TTS for natural, emotional speech.

Provides high-quality offline TTS with prosody and emotion.
Falls back to pyttsx3 if Coqui TTS is not installed.
"""
import os
import threading
from typing import Optional
import tempfile

_tts_model = None
_tts_lock = threading.Lock()
_USE_COQUI = False


def _init_coqui():
    """Initialize Coqui TTS model (lazy loading)."""
    global _tts_model, _USE_COQUI
    if _tts_model is not None:
        return _tts_model
    
    try:
        from TTS.api import TTS
        print("[NeuralTTS] Loading Coqui TTS model (this may take a moment)...")
        
        # Use a fast, high-quality English model that runs offline
        # VITS models are fast and natural-sounding
        model_name = "tts_models/en/ljspeech/vits"
        
        _tts_model = TTS(model_name=model_name, progress_bar=False)
        _USE_COQUI = True
        print(f"[NeuralTTS] Coqui TTS loaded: {model_name}")
        return _tts_model
    except ImportError:
        print("[NeuralTTS] Coqui TTS not installed. Install: pip install TTS")
        return None
    except Exception as e:
        print(f"[NeuralTTS] Failed to load Coqui TTS: {e}")
        return None


def speak_neural(text: str, emotion: str = "neutral") -> bool:
    """Speak text using neural TTS with emotion.
    
    Args:
        text: Text to speak
        emotion: Emotion hint (neutral, happy, sad, excited) - not all models support this
    
    Returns:
        True if spoken successfully, False if fallback needed
    """
    if not text:
        return True
    
    with _tts_lock:
        model = _init_coqui()
        if model is None:
            return False
        
        try:
            # Generate audio to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            
            # Generate speech
            model.tts_to_file(text=text, file_path=tmp_path)
            
            # Play the audio
            try:
                import sounddevice as sd
                import soundfile as sf
                data, samplerate = sf.read(tmp_path)
                sd.play(data, samplerate)
                sd.wait()
            except ImportError:
                # Fallback: use system player
                import subprocess
                import sys
                if sys.platform == 'win32':
                    # Use Windows Media Player
                    subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{tmp_path}").PlaySync()'], 
                                   check=False, capture_output=True)
                else:
                    # Use afplay on macOS, aplay on Linux
                    player = 'afplay' if sys.platform == 'darwin' else 'aplay'
                    subprocess.run([player, tmp_path], check=False, capture_output=True)
            
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            
            return True
            
        except Exception as e:
            print(f"[NeuralTTS] Error generating speech: {e}")
            return False


def is_available() -> bool:
    """Check if neural TTS is available."""
    try:
        from TTS.api import TTS
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    print("Testing Neural TTS...")
    if speak_neural("Hello! I am Jessica, your AI assistant. I now have a more natural voice with better prosody."):
        print("Neural TTS test successful!")
    else:
        print("Neural TTS not available.")
