"""Phase 8.2: Contextual Formatter (read-only, deterministic)."""

from __future__ import annotations

import re
from typing import Optional

from .conversation_context import ConversationContext
from .reflection_record import ReflectionRecord


_FORBIDDEN_TERMS = [
    "phase",
    "module",
    "dataclass",
    "reflectionrecord",
    "source_id",
    "execution_id",
    "orchestrator",
    "enum",
    "jessica.",
]


def _sanitize(text: str) -> str:
    cleaned = text.strip()
    for term in _FORBIDDEN_TERMS:
        cleaned = re.sub(re.escape(term), "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _first_person(summary: str) -> str:
    cleaned = _sanitize(summary)
    if not cleaned:
        return ""
    lowered = cleaned.lower()
    if lowered.startswith("i ") or lowered.startswith("i'm"):
        return cleaned.rstrip(".")
    return f"I {lowered}".rstrip(".")


class ContextualFormatter:
    """Stateless formatter for contextual, first-person narratives."""

    def format(
        self,
        reflection: ReflectionRecord,
        context: Optional[ConversationContext] = None,
    ) -> str:
        parts: list[str] = []

        main_sentence = _first_person(reflection.summary)
        if main_sentence:
            parts.append(main_sentence)

        if context and context.prior_reflections:
            prior = context.prior_reflections[0]
            prior_summary = _sanitize(prior.summary)
            if prior_summary:
                parts.append(f"Earlier, I noticed {prior_summary.lower()}")

        if reflection.identified_risks:
            risks = ", ".join(_sanitize(r).rstrip(".") for r in reflection.identified_risks if _sanitize(r))
            if risks:
                parts.append(f"I noticed {risks.lower()}")

        response = ". ".join(p for p in parts if p).strip()
        if response and not response.endswith("."):
            response += "."
        return response
