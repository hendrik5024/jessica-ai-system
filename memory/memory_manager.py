import json
import os
from datetime import datetime


class MemoryManager:
    def __init__(self, memory_file: str = "memory/memory.json"):
        self.memory_file = memory_file
        self._ensure_memory_file()

    def _ensure_memory_file(self):
        directory = os.path.dirname(self.memory_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

    def load_memory(self):
        self._ensure_memory_file()
        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            data = data if isinstance(data, list) else []
            cleaned = self.clean_memory(data)
            if len(cleaned) > 50:
                cleaned = cleaned[-50:]

            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump(cleaned, file, indent=4)

            return cleaned
        except (json.JSONDecodeError, OSError):
            with open(self.memory_file, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)
            return []

    def clean_memory(self, data):
        if not isinstance(data, list):
            return []

        cleaned = []
        seen = set()

        for entry in data:
            if not isinstance(entry, dict):
                continue

            response = entry.get("response")
            if response is None:
                continue
            if response == "I don't understand yet.":
                continue

            key = (entry.get("input"), response)
            if key in seen:
                continue

            seen.add(key)
            cleaned.append(entry)

        return cleaned

    def save_interaction(self, input_text, intent, response):
        if response is None:
            return

        if response == "I don't understand yet.":
            return

        memories = self.load_memory()
        memories = self.clean_memory(memories)

        if memories:
            last_entry = memories[-1]
            if (
                last_entry.get("input") == input_text
                and last_entry.get("response") == response
            ):
                return

        memories.append(
            {
                "input": input_text,
                "intent": intent,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        memories = self.clean_memory(memories)

        if len(memories) > 50:
            memories = memories[-50:]

        with open(self.memory_file, "w", encoding="utf-8") as file:
            json.dump(memories, file, indent=4)

    def get_recent(self, limit=5):
        memories = self.load_memory()
        if limit is None or limit <= 0:
            return []
        return memories[-limit:]
