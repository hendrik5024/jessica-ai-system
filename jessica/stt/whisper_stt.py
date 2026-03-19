"""Offline Speech-to-Text using OpenAI Whisper with push-to-talk hotkey.

Uses whisper-base model for fast, local transcription.
Hotkey: Hold 'Ctrl+Shift+Space' to record, release to transcribe.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Callable, Optional

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class WhisperSTT:
    """Whisper-based speech-to-text with push-to-talk."""

    def __init__(self, model_name: str = "base", sample_rate: int = 16000):
        self.model_name = model_name
        self.sample_rate = sample_rate
        self.model: Optional[whisper.Whisper] = None
        self.is_recording = False
        self.audio_data = []
        self.callback: Optional[Callable[[str], None]] = None
        
        if not AUDIO_AVAILABLE:
            print("[STT] Audio libraries missing. Install: pip install sounddevice soundfile numpy")
        if not WHISPER_AVAILABLE:
            print("[STT] Whisper not installed. Install: pip install openai-whisper")
        if not PYNPUT_AVAILABLE:
            print("[STT] Keyboard library missing. Install: pip install pynput")

    def load_model(self):
        """Load Whisper model (lazy loading to save startup time)."""
        if self.model is None and WHISPER_AVAILABLE:
            print(f"[STT] Loading Whisper {self.model_name} model...")
            self.model = whisper.load_model(self.model_name)
            print("[STT] Model loaded.")

    def start_recording(self):
        """Start audio recording."""
        if not AUDIO_AVAILABLE:
            return
        
        self.is_recording = True
        self.audio_data = []
        print("[STT] 🎤 Recording... (release hotkey to transcribe)")

        def audio_callback(indata, frames, time_info, status):
            if self.is_recording:
                self.audio_data.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            callback=audio_callback
        )
        self.stream.start()

    def stop_recording(self) -> str:
        """Stop recording and transcribe."""
        if not AUDIO_AVAILABLE or not self.is_recording:
            return ""

        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        
        if not self.audio_data:
            print("[STT] No audio recorded.")
            return ""

        print("[STT] Processing audio...")
        
        # Combine audio chunks
        audio = np.concatenate(self.audio_data, axis=0).squeeze()
        
        # Save temporary file
        temp_path = "temp_recording.wav"
        sf.write(temp_path, audio, self.sample_rate)
        
        # Transcribe
        text = self.transcribe_file(temp_path)
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return text

    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe an audio file using Whisper."""
        if not WHISPER_AVAILABLE:
            return "[STT] Whisper not installed."
        
        if not os.path.isfile(audio_path):
            return f"[STT] File not found: {audio_path}"
        
        try:
            self.load_model()
            result = self.model.transcribe(audio_path, fp16=False)
            text = result["text"].strip()
            print(f"[STT] Transcribed: {text}")
            return text
        except Exception as e:
            return f"[STT] Transcription failed: {e}"

    def set_callback(self, callback: Callable[[str], None]):
        """Set callback function to receive transcribed text."""
        self.callback = callback

    def on_press(self, key):
        """Handle hotkey press."""
        try:
            # Check for Ctrl+Shift+Space
            if (hasattr(key, 'char') and key.char == ' ' and 
                keyboard.Controller().ctrl and keyboard.Controller().shift):
                if not self.is_recording:
                    self.start_recording()
        except AttributeError:
            pass

    def on_release(self, key):
        """Handle hotkey release."""
        try:
            # Check for space release
            if hasattr(key, 'char') and key.char == ' ':
                if self.is_recording:
                    text = self.stop_recording()
                    if text and self.callback:
                        self.callback(text)
        except AttributeError:
            pass

    def start_listener(self):
        """Start keyboard listener for push-to-talk."""
        if not PYNPUT_AVAILABLE:
            print("[STT] Cannot start listener: pynput not installed.")
            return

        print("[STT] Push-to-talk ready. Hold Ctrl+Shift+Space to record.")
        
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            listener.join()


def check_dependencies() -> dict:
    """Check if all required dependencies are installed."""
    return {
        "sounddevice": AUDIO_AVAILABLE,
        "whisper": WHISPER_AVAILABLE,
        "pynput": PYNPUT_AVAILABLE,
    }


def install_instructions() -> str:
    """Return installation instructions for missing dependencies."""
    deps = check_dependencies()
    missing = [name for name, available in deps.items() if not available]
    
    if not missing:
        return "✓ All dependencies installed."
    
    instructions = ["Missing dependencies for Speech-to-Text:"]
    if not deps["sounddevice"]:
        instructions.append("  pip install sounddevice soundfile numpy")
    if not deps["whisper"]:
        instructions.append("  pip install openai-whisper")
    if not deps["pynput"]:
        instructions.append("  pip install pynput")
    
    return "\n".join(instructions)


if __name__ == "__main__":
    print(install_instructions())
    print("\nTesting Whisper STT...")
    
    stt = WhisperSTT(model_name="base")
    
    def on_transcribe(text: str):
        print(f"Transcribed: {text}")
    
    stt.set_callback(on_transcribe)
    stt.start_listener()
