class ExplanationEngine:

    def generate(self, last_record) -> str:
        if not last_record:
            return "I don't have enough information to explain my reasoning."

        intent = last_record.get("intent", "")
        decision = last_record.get("decision", "")
        reasoning = last_record.get("reasoning", "")

        response = []

        if intent:
            response.append(f"I interpreted your request as {intent}.")

        if decision:
            response.append(f"My decision was to {decision.replace('_', ' ')}.")

        if reasoning:
            response.append(reasoning)

        return " ".join(response)
