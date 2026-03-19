"""
Phase 89: Persistent Memory

JSON-based storage for Jessica's memory across sessions.
Transparent, safe, and reversible.
"""

import json
from pathlib import Path


class PersistentMemory:
    """
    Persistent storage using JSON files.
    Automatically saves on every write.
    """

    def __init__(self, file_path="jessica_memory.json"):
        self.file_path = Path(file_path)
        self.data = self._load()

    def _load(self):
        """Load memory from JSON file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh
                return {}
        return {}

    def save(self):
        """Save memory to JSON file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except IOError:
            # Fail silently to avoid breaking the system
            pass

    def set(self, key, value):
        """Store a value and immediately save to disk."""
        self.data[key] = value
        self.save()

    def get(self, key):
        """Retrieve a value from memory."""
        return self.data.get(key)

    def all(self):
        """Get all stored data."""
        return dict(self.data)

    def clear(self):
        """Clear all memory (for testing)."""
        self.data = {}
        self.save()
