from collections import Counter


class CapabilityAdvisor:

    def __init__(self):
        self.intent_history = []

    def record_intent(self, intent):
        self.intent_history.append(intent)

    def analyze_patterns(self):

        if len(self.intent_history) < 5:
            return None

        counter = Counter(self.intent_history)

        most_common_intent, count = counter.most_common(1)[0]

        if count >= 5:

            if most_common_intent == "GENERAL":
                return "Insight: GENERAL tasks appear frequently. Consider automation."

            if most_common_intent == "CREATE_PROJECT":
                return "Insight: You frequently create Python projects. Consider a project template tool."

            if most_common_intent == "ANALYZE_DATA":
                return "You frequently analyze CSV files."

        return None
