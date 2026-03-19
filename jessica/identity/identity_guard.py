class IdentityGuard:
    def enforce(self, response: str) -> str:
        if not response:
            return "I could not generate a response."

        text = response.strip()

        # Remove model identity leakage
        replacements = [
            ("phi", "Jessica"),
            ("assistant", "Jessica"),
            ("language model", "cognitive system"),
            ("ai model", "cognitive system"),
        ]

        lower = text.lower()

        for old, new in replacements:
            if old in lower:
                text = text.replace(old, new)
                text = text.replace(old.capitalize(), new)

        return text
