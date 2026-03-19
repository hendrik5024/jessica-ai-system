"""Phase 9.1: Narrative Formatter (read-only, deterministic)."""

from __future__ import annotations

from .reflection_record import ReflectionRecord


class NarrativeFormatter:
    """Deterministic formatter for first-person narrative output."""

    def format(self, reflection: ReflectionRecord) -> str:
        summary = reflection.summary.strip()
        if not summary:
            return ""
        lowered = summary.lower()
        if lowered.startswith("i ") or lowered.startswith("i'm"):
            return summary
        return f"I {lowered}".rstrip(".") + "."
