"""Phase 8.2: Contextual Orchestrator (read-only, deterministic)."""

from __future__ import annotations

from typing import Optional, Tuple

from .conversation_context import ConversationContext
from .enhanced_narrative_formatter import EnhancedNarrativeFormatter
from .identity_profile import IdentityProfile
from .reflection_record import ReflectionRecord


class ContextualOrchestrator:
    def __init__(self, identity_profile: Optional[IdentityProfile] = None):
        self.profile = identity_profile or IdentityProfile.default()
        self.formatter = EnhancedNarrativeFormatter(self.profile)

    def respond_with_context(
        self,
        current_reflection: ReflectionRecord,
        reflection_history: Tuple[ReflectionRecord, ...],
    ) -> str:
        context = ConversationContext(
            current_reflection=current_reflection,
            prior_reflections=tuple(reflection_history),
        )
        return self.formatter.format_with_context(
            reflection=current_reflection,
            context=context,
        )

    def update_context(self, *args, **kwargs):
        return None

    def get_conversation_summary(self):
        return ""

    def clear_context(self):
        return None
