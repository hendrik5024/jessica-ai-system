import json
import os


class LearningManager:
    def __init__(self, patterns_file: str = "memory/learned_patterns.json"):
        self.patterns_file = patterns_file
        self._ensure_patterns_file()

    def _ensure_patterns_file(self):
        directory = os.path.dirname(self.patterns_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.patterns_file):
            with open(self.patterns_file, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)

    def load_patterns(self):
        self._ensure_patterns_file()
        try:
            with open(self.patterns_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            with open(self.patterns_file, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)
            return {}

    def save_pattern(self, input_text, response):
        patterns = self.load_patterns()
        key = str(input_text).strip().lower()
        if key in patterns:
            return

        patterns[key] = response

        with open(self.patterns_file, "w", encoding="utf-8") as file:
            json.dump(patterns, file, indent=4)

    def get_learned_response(self, input_text):
        patterns = self.load_patterns()
        key = str(input_text).strip().lower()
        return patterns.get(key)
