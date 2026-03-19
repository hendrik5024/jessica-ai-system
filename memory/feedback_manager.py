import json
import os
from datetime import datetime


class FeedbackManager:
    def __init__(self, feedback_file: str = "memory/feedback.json"):
        self.feedback_file = feedback_file
        self._ensure_feedback_file()

    def _ensure_feedback_file(self):
        directory = os.path.dirname(self.feedback_file)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

    def load_feedback(self):
        self._ensure_feedback_file()
        try:
            with open(self.feedback_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            with open(self.feedback_file, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)
            return []

    def save_feedback(self, input_text, response, success):
        records = self.load_feedback()
        records.append(
            {
                "input": input_text,
                "response": response,
                "success": bool(success),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        if len(records) > 200:
            records = records[-200:]

        with open(self.feedback_file, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=4)

    def get_failed_patterns(self):
        records = self.load_feedback()
        return [item for item in records if not item.get("success", False)]
