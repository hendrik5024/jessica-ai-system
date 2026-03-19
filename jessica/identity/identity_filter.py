"""
Identity Filter

Ensures ALL responses are in Jessica's voice.
Prevents model identity leakage.
"""


class IdentityFilter:

    def __init__(self):
        self.enabled = True

    def enforce(self, text: str) -> str:
        if not text:
            return text

        t = text.lower()

        # ----------------------------
        # Remove model identity leaks
        # ----------------------------
        forbidden = [
            "as an ai",
            "language model",
            "openai",
            "microsoft",
            "i am an assistant",
            "i'm an assistant",
            "i am phi",
            "i'm phi",
            "i was trained",
            "my training data",
        ]

        # STEP 8: Check response for forbidden phrases
        for f in forbidden:
            if f in t:
                return "I am Jessica, a cognitive system."

        # ----------------------------
        # Normalize assistant tone
        # ----------------------------
        if text.lower().startswith("assistant:"):
            text = text.replace("Assistant:", "").strip()

        return text
