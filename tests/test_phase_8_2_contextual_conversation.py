"""Phase 8.2: Contextual Conversation - Test Suite.

Tests Phase 8.2 conversational memory boundary components for:
- immutability
- determinism
- read-only behavior
- no autonomy / execution / learning
- no technical leakage
- no persistence across sessions
- backward compatibility with Phase 8.1
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime
from typing import Tuple

import pytest

from jessica.chat_interface import chat_from_reflection
from jessica.execution.conversation_context import ConversationContext
from jessica.execution.contextual_orchestrator import ContextualOrchestrator
from jessica.execution.enhanced_narrative_formatter import EnhancedNarrativeFormatter
from jessica.execution.identity_profile import IdentityProfile
from jessica.execution.reflection_record import (
    ConfidenceLevel,
    ReflectionRecord,
    SourceType,
)


_FIXED_TIME = datetime(2026, 2, 6, 12, 0, 0)


def _make_reflection(
    reflection_id: str,
    source_id: str,
    summary: str,
    risks: Tuple[str, ...] | None = None,
    anomalies: Tuple[str, ...] | None = None,
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM,
) -> ReflectionRecord:
    return ReflectionRecord(
        reflection_id=reflection_id,
        source_type=SourceType.EXECUTION,
        source_id=source_id,
        summary=summary,
        identified_risks=list(risks or ()),
        anomalies=list(anomalies or ()),
        confidence_level=confidence,
        created_at=_FIXED_TIME,
        notes=None,
    )


def _call_formatter(
    formatter: EnhancedNarrativeFormatter,
    current: ReflectionRecord,
    context: ConversationContext,
) -> str:
    if hasattr(formatter, "format_with_context"):
        try:
            return formatter.format_with_context(reflection=current, context=context)
        except TypeError:
            return formatter.format_with_context(current, context)
    if hasattr(formatter, "format"):
        try:
            return formatter.format(reflection=current, context=context)
        except TypeError:
            return formatter.format(current, context)
    if hasattr(formatter, "compose"):
        try:
            return formatter.compose(context=context)
        except TypeError:
            return formatter.compose(context)
    pytest.fail("EnhancedNarrativeFormatter has no usable format method")


def _call_orchestrator(
    orchestrator: ContextualOrchestrator,
    current: ReflectionRecord,
    history: Tuple[ReflectionRecord, ...],
) -> str:
    if hasattr(orchestrator, "respond_with_context"):
        try:
            return orchestrator.respond_with_context(
                current_reflection=current,
                reflection_history=history,
            )
        except TypeError:
            return orchestrator.respond_with_context(current, history)
    if hasattr(orchestrator, "respond"):
        try:
            return orchestrator.respond(
                current_reflection=current,
                reflection_history=history,
            )
        except TypeError:
            return orchestrator.respond(current, history)
    pytest.fail("ContextualOrchestrator has no respond method")


# -------------------------
# ConversationContext Tests
# -------------------------

def test_conversation_context_is_frozen():
    current = _make_reflection("refl_1", "exec_1", "Email sent successfully")
    prior = (_make_reflection("refl_0", "exec_0", "Validation missing"),)

    context = ConversationContext(current_reflection=current, prior_reflections=prior, max_history=3)

    with pytest.raises(FrozenInstanceError):
        context.max_history = 1

    with pytest.raises(FrozenInstanceError):
        context.prior_reflections = ()


def test_conversation_context_window_limited():
    current = _make_reflection("refl_2", "exec_2", "Report generated")
    prior = (
        _make_reflection("refl_a", "exec_a", "Alpha"),
        _make_reflection("refl_b", "exec_b", "Bravo"),
        _make_reflection("refl_c", "exec_c", "Charlie"),
    )

    context = ConversationContext(current_reflection=current, prior_reflections=prior, max_history=2)

    assert len(context.prior_reflections) == 2
    assert context.prior_reflections[0].summary == "Alpha"
    assert context.prior_reflections[1].summary == "Bravo"


def test_conversation_context_read_only_accessors_only():
    current = _make_reflection("refl_3", "exec_3", "Settings updated")
    prior = (_make_reflection("refl_2", "exec_2", "Prior note"),)

    context = ConversationContext(current_reflection=current, prior_reflections=prior, max_history=1)

    assert isinstance(context.prior_reflections, tuple)
    assert not hasattr(context.prior_reflections, "append")
    assert not hasattr(context, "add_reflection")
    assert not hasattr(context, "update_context")


def test_conversation_context_no_mutation_after_creation():
    current = _make_reflection("refl_4", "exec_4", "File scanned")
    prior = (_make_reflection("refl_3", "exec_3", "Earlier scan"),)

    context = ConversationContext(current_reflection=current, prior_reflections=prior, max_history=3)

    assert context.current_reflection.summary == "File scanned"
    assert context.prior_reflections[0].summary == "Earlier scan"


# -----------------
# Determinism Tests
# -----------------

def test_formatter_deterministic_output():
    identity = IdentityProfile.default()
    formatter = EnhancedNarrativeFormatter(identity)

    current = _make_reflection("refl_5", "exec_5", "Email sent successfully")
    prior = (_make_reflection("refl_4", "exec_4", "Validation missing"),)
    context = ConversationContext(current_reflection=current, prior_reflections=prior, max_history=3)

    response1 = _call_formatter(formatter, current, context)
    response2 = _call_formatter(formatter, current, context)

    assert response1 == response2


def test_orchestrator_deterministic_output():
    orchestrator = ContextualOrchestrator(IdentityProfile.default())

    current = _make_reflection("refl_6", "exec_6", "Report generated")
    prior = (_make_reflection("refl_5", "exec_5", "Validation missing"),)

    response1 = _call_orchestrator(orchestrator, current, prior)
    response2 = _call_orchestrator(orchestrator, current, prior)

    assert response1 == response2


# ------------------------
# No Cross-Session Memory
# ------------------------

def test_orchestrator_no_cross_session_memory_with_empty_history():
    orchestrator = ContextualOrchestrator(IdentityProfile.default())

    first = _make_reflection("refl_7", "exec_7", "AlphaUnique marker")
    second = _make_reflection("refl_8", "exec_8", "BetaUnique marker")

    _ = _call_orchestrator(orchestrator, first, ())
    response = _call_orchestrator(orchestrator, second, ())

    assert "AlphaUnique" not in response


def test_new_orchestrator_has_no_prior_context():
    first_orchestrator = ContextualOrchestrator(IdentityProfile.default())
    second_orchestrator = ContextualOrchestrator(IdentityProfile.default())

    current = _make_reflection("refl_9", "exec_9", "GammaUnique marker")

    response1 = _call_orchestrator(first_orchestrator, current, ())
    response2 = _call_orchestrator(second_orchestrator, current, ())

    assert response1 == response2


# ------------------------------
# Context Awareness (Read-Only)
# ------------------------------

def test_context_awareness_references_prior_reflection_linguistically():
    orchestrator = ContextualOrchestrator(IdentityProfile.default())

    current = _make_reflection("refl_10", "exec_10", "Email sent successfully")
    prior = (_make_reflection("refl_9", "exec_9", "Validation missing earlier"),)

    response = _call_orchestrator(orchestrator, current, prior)
    response_lower = response.lower()

    continuity_cues = ["earlier", "previous", "before", "previously", "prior"]
    assert any(cue in response_lower for cue in continuity_cues)


def test_context_awareness_does_not_mutate_reflections():
    orchestrator = ContextualOrchestrator(IdentityProfile.default())

    current = _make_reflection(
        "refl_11",
        "exec_11",
        "Settings updated",
        risks=("Missing approval",),
        anomalies=(),
    )
    prior = (_make_reflection("refl_10", "exec_10", "Earlier update"),)

    original_summary = current.summary
    original_risks = list(current.identified_risks)

    _ = _call_orchestrator(orchestrator, current, prior)

    assert current.summary == original_summary
    assert current.identified_risks == original_risks


# --------------------
# No Technical Leakage
# --------------------

def test_no_technical_leakage_in_output():
    orchestrator = ContextualOrchestrator(IdentityProfile.default())

    current = _make_reflection("refl_12", "exec_12", "File scanned")
    prior = (_make_reflection("refl_11", "exec_11", "Earlier scan"),)

    response = _call_orchestrator(orchestrator, current, prior)
    response_lower = response.lower()

    forbidden_terms = [
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

    for term in forbidden_terms:
        assert term not in response_lower


# -----------------
# Safety Guarantees
# -----------------

def test_no_execute_propose_decide_methods_exist():
    orchestrator = ContextualOrchestrator(IdentityProfile.default())
    formatter = EnhancedNarrativeFormatter(IdentityProfile.default())

    forbidden_methods = [
        "execute",
        "execute_action",
        "propose",
        "propose_action",
        "decide",
        "make_decision",
        "initiate_conversation",
        "auto_respond",
    ]

    for method in forbidden_methods:
        assert not hasattr(orchestrator, method)
        assert not hasattr(formatter, method)


def test_no_learning_or_preference_storage():
    orchestrator = ContextualOrchestrator(IdentityProfile.default())
    formatter = EnhancedNarrativeFormatter(IdentityProfile.default())

    forbidden_attrs = [
        "preferences",
        "preference_store",
        "learning_state",
        "weights",
        "ranking",
        "ranker",
        "memory_store",
        "embedding_store",
    ]

    for attr in forbidden_attrs:
        assert not hasattr(orchestrator, attr)
        assert not hasattr(formatter, attr)


def test_no_session_id_or_persistent_state():
    orchestrator = ContextualOrchestrator(IdentityProfile.default())

    assert not hasattr(orchestrator, "session_id")
    assert not hasattr(orchestrator, "save_context")
    assert not hasattr(orchestrator, "load_context")


# ------------------------
# Backward Compatibility
# ------------------------

def test_phase_8_1_chat_from_reflection_still_works():
    reflection = _make_reflection("refl_13", "exec_13", "Report generated")

    response = chat_from_reflection(reflection)

    assert isinstance(response, str)
    assert len(response) > 0
    assert "i " in response.lower() or "i'm" in response.lower()
