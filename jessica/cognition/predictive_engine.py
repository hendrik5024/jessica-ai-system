from collections import Counter


class PredictiveEngine:

    def __init__(self):

        self.intent_history = []

    def record_intent(self, intent):

        self.intent_history.append(intent)

        if len(self.intent_history) > 50:
            self.intent_history.pop(0)

    def predict_next(self):
        return self.predict_next_with_skills()

    def predict_next_with_skills(self, skill_map=None):

        if len(self.intent_history) < 5:
            return None

        counter = Counter(self.intent_history)

        intent, count = counter.most_common(1)[0]

        if count >= 5:

            if skill_map:
                learned_tool = skill_map.get(intent)

                if learned_tool:
                    return (
                        f"I noticed repeated {intent} tasks and I can use "
                        f"{learned_tool} automatically. Would you like me to keep using it?"
                    )

            if intent == "SYSTEM_STATUS":
                return "You often check system status. Would you like a quick status command?"

            if intent == "CREATE_PROJECT":
                return "You frequently create Python projects. Would you like me to prepare a project template?"

            if intent == "GENERAL":
                return None

        return None