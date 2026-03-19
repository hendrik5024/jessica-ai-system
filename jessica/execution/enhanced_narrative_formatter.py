"""Phase 8.2: Enhanced Narrative Formatter (read-only, deterministic)."""

from __future__ import annotations

import re
from typing import Optional

from .conversation_context import ConversationContext
from .identity_profile import IdentityProfile
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


def _join_items(items: list[str]) -> str:
    cleaned_items = [item.rstrip(".") for item in (_sanitize(i) for i in items) if item]
    if not cleaned_items:
        return ""
    if len(cleaned_items) == 1:
        return cleaned_items[0]
    return ", ".join(cleaned_items)


class EnhancedNarrativeFormatter:
    """Deterministic formatter for context-aware first-person narratives."""

    def __init__(self, identity_profile: IdentityProfile):
        self.profile = identity_profile

    def format_with_context(
        self,
        reflection: ReflectionRecord,
        context: Optional[ConversationContext] = None,
    ) -> str:
        parts: list[str] = []

        current_sentence = _first_person(reflection.summary)
        if current_sentence:
            parts.append(current_sentence)

        if context and context.prior_reflections:
            prior = context.prior_reflections[0]
            prior_summary = _sanitize(prior.summary)
            if prior_summary:
                parts.append(f"Earlier, I noticed {prior_summary.lower()}")

        if reflection.identified_risks:
            risks = _join_items(list(reflection.identified_risks))
            if risks:
                parts.append(f"I noticed {risks.lower()}")

        if reflection.anomalies:
            anomalies = _join_items(list(reflection.anomalies))
            if anomalies:
                parts.append(f"I noticed {anomalies.lower()}")

        confidence = _sanitize(self.profile.get_confidence_phrase(
            reflection.confidence_level.value
        ))
        if confidence:
            parts.append(confidence)

        response = ". ".join(p for p in parts if p).strip()
        if response and not response.endswith("."):
            response += "."
        return response
