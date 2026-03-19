"""
Phase 78 — Cognitive Routing Engine

Jessica decides HOW to think before answering.
LLM is only used as a fallback tool.
"""

from enum import Enum


class CognitiveMode(Enum):
    MEMORY = "memory"
    IDENTITY = "identity"
    LOGIC = "logic"
    WORLD = "world"
    LLM = "llm"
    UNKNOWN = "unknown"


class CognitiveRouter:

    def is_math_expression(self, text: str) -> bool:
        allowed = "0123456789+-*/(). "
        stripped = text.strip()
        if not stripped:
            return False
        return all(char in allowed for char in stripped)

    def classify(self, user_input: str) -> CognitiveMode:
        text = user_input.lower()

        # MEMORY
        if "my name is" in text or "what is my name" in text:
            return CognitiveMode.MEMORY
        if "name" in text and "my" in text:
            return CognitiveMode.MEMORY

        # IDENTITY
        if "who are you" in text or "what are you" in text:
            return CognitiveMode.IDENTITY

        # LOGIC / MATH
        if self.is_math_expression(text):
            return CognitiveMode.LOGIC

        # WORLD KNOWLEDGE
        if "capital" in text or "country" in text:
            return CognitiveMode.WORLD

        # FALLBACK
        return CognitiveMode.LLM
