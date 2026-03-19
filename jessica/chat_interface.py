"""Phase 8: Conversational Identity Layer - Chat Interface

Human-facing conversational entry point for Jessica.

CRITICAL CONSTRAINTS:
- Read-only narrative interface
- No execution capability
- No proposal creation
- No learning
- No memory mutation
- Deterministic and side-effect free
"""

from jessica.execution import (
    IdentityProfile,
    ConversationalOrchestrator,
    ReflectionRecord,
)


def chat_from_reflection(reflection: ReflectionRecord) -> str:
    """
    Convert a ReflectionRecord into a natural language response.

    This function is stateless and deterministic. It creates a default
    IdentityProfile and uses the ConversationalOrchestrator to format
    the reflection into first-person narrative without side effects.

    Args:
        reflection: Phase 7.3 ReflectionRecord

    Returns:
        Natural language conversational response
    """
    profile = IdentityProfile.default()
    orchestrator = ConversationalOrchestrator(profile)
    return orchestrator.respond(reflection=reflection)
