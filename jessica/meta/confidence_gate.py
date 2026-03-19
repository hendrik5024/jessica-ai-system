from __future__ import annotations

from typing import Any, Dict


class ConfidenceGate:
    """Gates low-confidence responses with clarification or deferral."""

    def __init__(self, threshold: float = 0.55) -> None:
        self.threshold = threshold

    def apply(
        self,
        *,
        confidence: float,
        intent: Dict[str, Any] | str,
        user_text: str,
        draft_response: str | None = None,
        mode: str | None = None,
    ) -> Dict[str, Any]:
        intent_label = intent.get("intent") if isinstance(intent, dict) else str(intent)

        if confidence >= self.threshold:
            return {
                "action": "allow",
                "confidence": confidence,
                "threshold": self.threshold,
            }

        strategy = self._select_strategy(intent_label, user_text, mode)
        response = self._build_gate_response(strategy, intent_label, user_text)

        return {
            "action": "gate",
            "confidence": confidence,
            "threshold": self.threshold,
            "strategy": strategy,
            "response": response,
        }

    def _select_strategy(self, intent_label: str, user_text: str, mode: str | None) -> str:
        text = (user_text or "").lower()
        short_query = len(text.split()) < 6
        vague_pronouns = any(p in text.split() for p in ["it", "that", "this", "they", "them"])

        if intent_label == "code" or mode == "code":
            return "clarify_options_code"
        if short_query or vague_pronouns:
            return "clarify"
        if intent_label in {"chat", "advice"}:
            return "clarify_options"
        return "defer"

    def _build_gate_response(self, strategy: str, intent_label: str, user_text: str) -> str:
        if strategy == "clarify_options_code":
            return (
                "I want to be accurate here. Which language/runtime should I target?\n"
                "Options: Python 3.x, JavaScript/Node, Java, C#, or something else.\n"
                "Also, any constraints (framework, OS, performance, format)?"
            )

        if strategy == "clarify_options":
            return (
                "I want to make sure I answer the right thing.\n"
                "What outcome are you aiming for, and do you want a quick overview or step-by-step?"
            )

        if strategy == "clarify":
            return "Can you clarify what you need? A bit more context will help me answer accurately."

        return (
            "I’m not confident enough to answer that accurately yet. "
            "If you can add a bit of context or clarify the goal, I can help."
        )
