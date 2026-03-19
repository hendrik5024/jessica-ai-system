import json
import os
import re
from datetime import datetime

MEMORY_FILE = "jessica/memory/episodic_memory.json"


class EpisodicMemory:

    def __init__(self):
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w", encoding="utf-8") as handle:
                json.dump([], handle)

        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as handle:
                self.memories = json.load(handle)
        except Exception:
            self.memories = []

    def store_event(self, user_input, response, intent, user_id="default"):

        event = {
            "timestamp": str(datetime.now()),
            "intent": intent,
            "user_input": str(user_input),
            "response": str(response),
            "user_id": str(user_id or "default"),
        }

        self.memories.append(event)

        if len(self.memories) > 200:
            self.memories.pop(0)

        with open(MEMORY_FILE, "w", encoding="utf-8") as handle:
            json.dump(self.memories, handle, indent=2)

    def search(self, keyword, user_id=None):

        query = (keyword or "").strip().lower()

        if not query:
            return []

        query_tokens = [
            token for token in re.findall(r"[a-z0-9']+", query)
            if len(token) > 3 and token not in {
                "what",
                "did",
                "about",
                "earlier",
                "previous",
                "discuss",
                "remember",
                "talked",
            }
        ]

        results = []
        normalized_user = None if user_id is None else str(user_id or "default")

        for event in reversed(self.memories):
            event_user = str(event.get("user_id", "")).strip()

            if normalized_user is not None:
                if event_user:
                    if event_user != normalized_user:
                        continue
                elif normalized_user != "default":
                    continue

            user_text = str(event.get("user_input", "")).lower()
            response_text = str(event.get("response", "")).lower()

            if query in user_text or query in response_text:
                results.append(event)
                if len(results) >= 3:
                    break
                continue

            if any(token in user_text or token in response_text for token in query_tokens):
                results.append(event)

            if len(results) >= 3:
                break

        return results