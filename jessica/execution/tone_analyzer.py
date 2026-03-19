"""Tone analyzer utilities for Phase 8.x."""

from enum import Enum, auto


class Tone(Enum):
    NEUTRAL = auto()
    CONFIDENT = auto()
    CONCERNED = auto()


def analyze_tone(summary: str, risks: list[str]) -> Tone:
    if risks:
        return Tone.CONCERNED

    if summary.lower().startswith(("success", "completed", "sent", "generated")):
        return Tone.CONFIDENT

    return Tone.NEUTRAL
