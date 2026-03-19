"""
Phase 78.1 — Response Guard

Ensures Jessica ALWAYS speaks as herself.
Strips model identity leakage.
"""


class ResponseGuard:

    FORBIDDEN_PHRASES = [
        "i am an ai language model",
        "as an ai",
        "i am phi",
        "openai",
        "trained on",
        "i don't have access to",
        "i cannot access your files",
        "i am a chatbot",
        "i am an assistant",
    ]

    def enforce_identity(self, response: str) -> str:
        text = response.lower()

        # Strip forbidden phrases
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in text:
                return self._rewrite(response)

        return response

    def _rewrite(self, original: str) -> str:
        return "I am Jessica. I respond based on my internal architecture and available knowledge."
