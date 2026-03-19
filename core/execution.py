import difflib
from datetime import datetime


def find_similar(input_text, memory):
    best_match = None
    highest_score = 0

    for item in memory:
        score = difflib.SequenceMatcher(
            None,
            input_text.lower(),
            item["input"].lower()
        ).ratio()

        if score > highest_score:
            highest_score = score
            best_match = item

    if highest_score > 0.6:
        return best_match

    return None


class ExecutionEngine:
    def get_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def get_date(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def execute(self, action: dict) -> str:
        action_type = action.get("type")

        if action_type == "greeting":
            return "Hello! How can I help?"

        if action_type == "get_time":
            return self.get_time()

        if action_type == "get_date":
            return self.get_date()

        if action_type == "identity":
            return "I am Jessica, your personal AI assistant."

        if action_type == "multi":
            results = []

            for intent in action.get("parameters", {}).get("intents", []):
                if intent == "get_time":
                    results.append(self.get_time())
                elif intent == "get_date":
                    results.append(self.get_date())

            return " | ".join(results)

        if action_type == "recall_memory":
            memory = action.get("parameters", {}).get("memory", [])

            if not memory:
                return "I don't remember anything yet."

            questions = [item["input"] for item in memory[-5:]]
            questions = list(dict.fromkeys(questions))

            return "You recently asked me: " + "; ".join(questions)

        if action_type == "unknown":
            memory = action.get("parameters", {}).get("memory", [])

            similar = find_similar(
                action.get("parameters", {}).get("raw_input", ""),
                memory
            )

            if similar:
                return f"I've seen something similar: '{similar['input']}'. My answer was: {similar['response']}"

            return "I'm still learning. Can you rephrase that?"

        return "I don't understand yet."
