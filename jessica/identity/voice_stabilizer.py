"""
Phase 9 — Voice Stabilizer

Ensures Jessica's conversational voice remains consistent regardless
of which subsystem generates the response.
"""

from jessica.identity.identity_contract import DEFAULT_IDENTITY


class VoiceStabilizer:
    """Applies identity contract voice rules to responses."""

    def __init__(self):
        self.identity = DEFAULT_IDENTITY

    def stabilize(self, text: str) -> str:
        """Ensures first-person conversational framing."""
        if not text:
            return text

        if not text.lower().startswith("i "):
            return f"I {text[0].lower() + text[1:]}"
        return text
"""
Phase 9 — Voice Stabilizer

Ensures Jessica's conversational voice remains consistent regardless
of which subsystem generates the response.
"""

from jessica.identity.identity_contract import DEFAULT_IDENTITY


class VoiceStabilizer:
    """
    Applies identity contract voice rules to responses.
    """

    def __init__(self):
        self.identity = DEFAULT_IDENTITY

    def stabilize(self, text: str) -> str:
        """
        Ensures first-person conversational framing.
        """
        if not text:
            return text

        # Example stabilization rule:
        if not text.lower().startswith("i "):
            return f"I {text[0].lower() + text[1:]}"
        return text

