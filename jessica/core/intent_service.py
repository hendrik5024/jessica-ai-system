class IntentService:
    """
    Single source of truth for intent classification.
    """

    def classify(self, user_input: str) -> str:
        text = user_input.lower()

        # Order is VERY important

        if self._is_math(text):
            return "calculation"

        if self._is_memory_set(text):
            return "memory_set"

        if self._is_memory_query(text):
            return "memory_query"

        if self._is_identity(text):
            return "identity"

        if self._is_explanation(text):
            return "explanation"

        return "knowledge"

    # ---------- RULES ----------

    def _is_math(self, text):
        return any(op in text for op in ["+", "-", "*", "/", "(", ")"])

    def _is_memory_set(self, text):
        return "my name is" in text or "i am" in text

    def _is_memory_query(self, text):
        return "my name" in text or "do you remember" in text

    def _is_identity(self, text):
        return "what are you" in text or "who are you" in text

    def _is_explanation(self, text):
        return text.startswith("why") or text.startswith("how")
