from memory.memory_manager import MemoryManager


def detect_intent(text):
    text = text.lower()

    # time / date
    if "time" in text:
        return "get_time"

    if "date" in text or "today" in text:
        return "get_date"

    # greeting
    if text in ["hi", "hello", "hey"]:
        return "greeting"

    # identity
    if "your name" in text or "who are you" in text:
        return "identity"

    # coding
    if any(word in text for word in ["code", "python", "program"]):
        return "code"

    # reasoning
    if any(word in text for word in ["why", "how", "explain"]):
        return "reason"

    # knowledge
    if any(word in text for word in ["what", "who", "where"]):
        return "knowledge"

    return "unknown"


class Perception:
    def __init__(self):
        try:
            self.memory = MemoryManager()
        except Exception:
            self.memory = None

    def process(self, raw_input: str) -> dict:
        context = {"memory": []}
        try:
            if self.memory is not None:
                context["memory"] = self.memory.get_recent(limit=5)
        except Exception:
            context["memory"] = []
        memory = context.get("memory", [])
        text = (raw_input or "")
        intent = detect_intent(text)

        if intent == "unknown":
            confidence = 0.3
        elif intent in ["knowledge", "code", "reason"]:
            confidence = 0.8
        else:
            confidence = 0.9

        return {
            "raw_input": raw_input,
            "intent": intent,
            "confidence": confidence,
            "entities": [],
            "memory": memory,
        }
