"""Offline Text-to-Speech using Piper TTS.

Piper is a lightweight, fast neural TTS engine that works on Python 3.13 and
uses local ONNX models. We use the `en_US-amy-medium.onnx` model from the Voice/
folder for a natural, female voice without requiring external services.

All speech is queued to a single worker thread to avoid threading issues.
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from piper.voice import PiperVoice
except ImportError:
    PiperVoice = None


@dataclass(frozen=True)
class _Utterance:
    text: str
    done: Optional[threading.Event] = None


class _TTSWorker:
    def __init__(self) -> None:
        self._queue: "queue.Queue[_Utterance]" = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._started = False
        self._voice: Optional[object] = None
        self._init_lock = threading.Lock()

    def start(self) -> None:
        with self._init_lock:
            if self._started:
                return
            self._started = True
            self._thread.start()

    def enqueue(self, text: str, wait: bool) -> None:
        if not text:
            return
        self.start()
        done = threading.Event() if wait else None
        self._queue.put(_Utterance(text=text, done=done))
        if done is not None:
            done.wait()

    def _load_voice(self) -> Optional[object]:
        if self._voice is not None:
            return self._voice

        if PiperVoice is None:
            print("[TTS] piper-tts not installed; install with: pip install piper-tts")
            return None

        try:
            model_path = Path(__file__).parent.parent.parent / "Voice" / "en_US-amy-medium.onnx"
            if not model_path.exists():
                print(f"[TTS] Voice model not found at {model_path}")
                return None

            print(f"[TTS] Loading Piper voice from {model_path}")
            self._voice = PiperVoice.load(str(model_path))
            print("[TTS] Piper voice loaded successfully: en_US-amy-medium (female)")
            return self._voice
        except Exception as e:
            print(f"[TTS] Failed to load Piper voice: {e}")
            return None

    def _run(self) -> None:
        while True:
            utt = self._queue.get()
            try:
                voice = self._load_voice()
                if voice is None:
                    print("Jessica:", utt.text)
                    continue

                try:
                    # Synthesize audio chunks from text
                    audio_chunks = list(voice.synthesize(utt.text))
                    if not audio_chunks:
                        print("Jessica:", utt.text)
                        continue
                    
                    # Use first chunk's metadata
                    first_chunk = audio_chunks[0]
                    sample_rate = first_chunk.sample_rate
                    
                    # Concatenate all audio chunks
                    import numpy as np
                    audio_data = np.concatenate([chunk.audio_float_array for chunk in audio_chunks])
                    
                    # Play using sounddevice
                    try:
                        import sounddevice as sd
                        sd.play(audio_data, samplerate=sample_rate)
                        sd.wait()  # Block until playback finishes
                    except ImportError:
                        print(f"[TTS] sounddevice unavailable; text printed instead: {utt.text}")

                except Exception as e:
                    print(f"[TTS] Error during synthesis/playback: {e}")
                    import traceback
                    traceback.print_exc()
                    print("Jessica:", utt.text)
            finally:
                if utt.done is not None:
                    utt.done.set()
                self._queue.task_done()


_worker = _TTSWorker()


def speak(text: str, async_mode: bool = False, emotion: str = "neutral"):
    """Speak text using Piper TTS.

    - If async_mode=True: queue speech and return immediately.
    - If async_mode=False: block until speech finishes (but still uses the worker).
    """
    # `emotion` is currently unused but kept for API compatibility.
    _worker.enqueue(text=text, wait=not async_mode)


def set_voice(voice_index: int = 0):
    """Legacy function - Piper uses the bundled Amy voice."""
    print("[TTS] Using bundled Piper voice (en_US-amy-medium) - selection not needed")


def set_rate(rate: int):
    """Legacy function - Piper TTS rate is fixed by the model."""
    print(f"[TTS] Piper TTS rate is fixed; request noted (was: {rate})")


def list_voices():
    """Legacy function - Piper uses a single bundled female voice."""
    return ["en_US-amy-medium (Piper)"]


def stop():
    """Stop any ongoing speech."""
    # Piper doesn't support mid-speech interruption, so best-effort is to drop the engine.
    _worker._voice = None


if __name__ == "__main__":
    print("Testing Piper TTS...")
    list_voices()
    print("\nSpeaking test...")
    speak("Hello! I am Jessica, your offline AI assistant.")

