import json
import os


class ImprovementManager:
    def __init__(self, feedback_file: str = "memory/feedback.json"):
        self.feedback_file = feedback_file
        self._suggestions = []

    def _load_feedback(self):
        if not os.path.exists(self.feedback_file):
            return []

        try:
            with open(self.feedback_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def analyze_failures(self):
        feedback = self._load_feedback()
        failed_counts = {}

        for item in feedback:
            if not isinstance(item, dict):
                continue

            if item.get("success") is False:
                key = str(item.get("input", "")).strip()
                if not key:
                    continue
                failed_counts[key] = failed_counts.get(key, 0) + 1

        suggestions = []
        for pattern, count in failed_counts.items():
            if count >= 3:
                if pattern.lower() == "hello":
                    suggestion = "Add greeting response"
                else:
                    suggestion = "Add specific response for this input"

                suggestions.append(
                    {
                        "pattern": pattern,
                        "suggestion": suggestion,
                    }
                )

        self._suggestions = suggestions
        return suggestions

    def get_suggestions(self):
        return list(self._suggestions)

    def auto_learn(self, learning_manager):
        failures = self.analyze_failures()

        for item in failures:
            pattern = item["pattern"].lower()

            if "hello" in pattern:
                response = "Hello! How can I help?"
            elif "hi" in pattern:
                response = "Hi there! What can I do for you?"
            elif "help" in pattern:
                response = "Sure, tell me what you need help with."
            else:
                continue

            if learning_manager.get_learned_response(pattern) is None:
                learning_manager.save_pattern(pattern, response)
