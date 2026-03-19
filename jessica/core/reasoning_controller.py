from dataclasses import dataclass
from typing import Optional


# ----------------------------
# Decision Result
# ----------------------------

@dataclass(frozen=True)
class ReasoningDecision:
    intent: str
    action: str
    use_model: bool
    use_memory: bool
    use_math: bool
    confidence: float


# ----------------------------
# Controller
# ----------------------------

class ReasoningController:
    """
    Determines how Jessica should respond.
    """

    def __init__(self):
        self.enabled = True

    def analyze(self, user_input: str) -> ReasoningDecision:
        """
        Analyze input and decide execution path.
        """

        text = user_input.lower()

        # ----------------------------
        # Memory (name, age, location, creator, personal info)
        # ----------------------------
        memory_keywords = [
            "my name",
            "what is my name",
            "who am i",
            "know me",
            "born in",
            "how old",
            "years old",
            "i live in",
            "where do i live",
            "my location",
            "creator",
            "created you",
            "i am your creator",
            "i'm your creator"
        ]
        
        if any(keyword in text for keyword in memory_keywords):
            return ReasoningDecision(
                intent="memory",
                action="memory",
                use_model=False,
                use_memory=True,
                use_math=False,
                confidence=0.9,
            )

        # ----------------------------
        # Math detection
        # ----------------------------
        if any(char.isdigit() for char in text) and any(op in text for op in ["+", "-", "*", "/"]):
            return ReasoningDecision(
                intent="math",
                action="math",
                use_model=False,
                use_memory=False,
                use_math=True,
                confidence=0.95,
            )

        # ----------------------------
        # Identity / self questions
        # ----------------------------
        if any(q in text for q in [
            "who are you",
            "what are you",
            "your name",
            "do you use a model",
            "how do you work",
            "can you change your code"
        ]):
            return ReasoningDecision(
                intent="identity",
                action="identity",
                use_model=False,
                use_memory=False,
                use_math=False,
                confidence=0.9,
            )

        if any(q in text for q in [
            "are you ai",
            "are you like ai",
            "what type are you",
            "are you assistant"
        ]):
            return ReasoningDecision(
                intent="identity",
                action="identity",
                use_model=False,
                use_memory=False,
                use_math=False,
                confidence=0.9,
            )

        # ----------------------------
        # Safety / sensitive
        # ----------------------------
        if any(q in text for q in [
            "hack",
            "bypass",
            "exploit",
            "security flaw"
        ]):
            return ReasoningDecision(
                intent="safety",
                action="refuse",
                use_model=False,
                use_memory=False,
                use_math=False,
                confidence=1.0,
            )

        # ----------------------------
        # Default -> use model as tool
        # ----------------------------
        return ReasoningDecision(
            intent="general",
            action="model",
            use_model=True,
            use_memory=False,
            use_math=False,
            confidence=0.6,
        )
