"""Voice command listener that directly triggers Jessica's intent parser.

Listens for wake word 'Jessica' followed by commands like:
- 'Jessica, open the terminal'
- 'Jessica, help me with this spreadsheet'
- 'Jessica, take a screenshot'
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from jessica.stt.whisper_stt import WhisperSTT
from jessica.nlp.intent_parser import parse_intent


class VoiceListener:
    """Voice command listener with wake word detection."""

    def __init__(self, wake_word: str = "jessica", command_callback: Optional[Callable] = None):
        self.wake_word = wake_word.lower()
        self.command_callback = command_callback
        self.stt = WhisperSTT(model_name="base")
        self.is_active = True
        
        # Set up STT callback
        self.stt.set_callback(self._on_transcribed)

    def _on_transcribed(self, text: str):
        """Handle transcribed text and detect wake word."""
        if not text:
            return
        
        text_lower = text.lower().strip()
        print(f"[Listener] Heard: {text}")
        
        # Check for wake word
        if self.wake_word in text_lower:
            # Extract command after wake word
            parts = text_lower.split(self.wake_word, 1)
            if len(parts) > 1:
                command = parts[1].strip().lstrip(',').strip()
                if command:
                    self._process_command(command)
                else:
                    print(f"[Listener] Wake word detected but no command followed.")
            else:
                print(f"[Listener] Wake word detected: {text}")
        else:
            print(f"[Listener] No wake word in: {text}")

    def _process_command(self, command: str):
        """Parse and execute voice command."""
        print(f"[Listener] Processing command: {command}")
        
        try:
            intent = parse_intent(command)
            print(f"[Listener] Intent: {intent}")
            
            if self.command_callback:
                self.command_callback(command, intent)
            else:
                print(f"[Listener] No callback set. Intent would be: {intent}")
        
        except Exception as e:
            print(f"[Listener] Error processing command: {e}")

    def start(self):
        """Start the voice listener in a background thread."""
        print(f"[Listener] Starting voice command listener...")
        print(f"[Listener] Wake word: '{self.wake_word}'")
        print(f"[Listener] Push-to-talk: Hold Ctrl+Shift+Space")
        
        # Start STT listener (blocking)
        threading.Thread(target=self.stt.start_listener, daemon=True).start()
        
        print(f"[Listener] Ready. Say '{self.wake_word}, <command>' while holding hotkey.")

    def stop(self):
        """Stop the voice listener."""
        self.is_active = False
        print("[Listener] Stopped.")


def demo():
    """Demo the voice listener."""
    def handle_command(command: str, intent: dict):
        print(f"\n=== Command Received ===")
        print(f"Command: {command}")
        print(f"Intent: {intent}")
        print("========================\n")
    
    listener = VoiceListener(wake_word="jessica", command_callback=handle_command)
    listener.start()
    
    print("\nPress Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        listener.stop()


if __name__ == "__main__":
    demo()
