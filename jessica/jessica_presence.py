"""
Phase 9.1 — Unified Conversational Presence

Jessica's single conversational identity interface.
"""

from jessica.identity.voice_stabilizer import VoiceStabilizer
from jessica.execution.narrative_formatter import NarrativeFormatter
from jessica.execution.reflection_record import ReflectionRecord


class JessicaPresence:
    """
    Unified conversational presence representing Jessica herself.
    """

    def __init__(self):
        self.voice = VoiceStabilizer()
        self.formatter = NarrativeFormatter()

    def respond_from_reflection(self, reflection: ReflectionRecord) -> str:
        narrative = self.formatter.format(reflection)
        return self.voice.stabilize(narrative)
