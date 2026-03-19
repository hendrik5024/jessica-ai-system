from datetime import datetime
from jessica.core.introspection_record import IntrospectionRecord


class IntrospectionEngine:

    def __init__(self):
        self.last_record = None
        self.history = []

    def record(
        self,
        input_text: str,
        intent: str,
        decision: str,
        response: str,
        reasoning: str,
    ) -> IntrospectionRecord:

        record = {
            "input": input_text,
            "intent": intent,
            "decision": decision,
            "response": response,
            "reasoning": reasoning,
            "created_at": datetime.utcnow(),
        }

        self.history.append(record)
        self.last_record = record
        return record

    def get_last_record(self):
        return self.last_record

    def explain_last(self) -> str:
        if not self.last_record:
            return "I have no recent reasoning to explain."

        r = self.last_record

        return (
            f"I interpreted your request as: {r.get('intent', '')}. "
            f"My decision was: {r.get('decision', '')}. "
            f"I responded this way because: {r.get('reasoning', '')}."
        )
