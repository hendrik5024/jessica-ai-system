class DecisionEngine:
    def decide(self, context: dict) -> dict:
        return {
            "type": context["intent"],
            "parameters": context
        }
