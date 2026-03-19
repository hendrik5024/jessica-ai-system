from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.strategy.capability_assessment import CapabilityAssessment
from jessica.strategy.capability_descriptor import CapabilityDescriptor
from jessica.strategy.capability_reasoner import CapabilityReasoner
from jessica.strategy.capability_reasoning_orchestrator import CapabilityReasoningOrchestrator
from jessica.strategy.capability_registry import CapabilityRegistry


def test_assessment_immutable():

    assessment = CapabilityAssessment(
        goal="needs: Alpha",
        achievable=True,
        required_capabilities=("Alpha",),
        missing_capabilities=(),
        reasoning_summary="All required capabilities available.",
    )

    with pytest.raises(FrozenInstanceError):
        assessment.goal = "change"


def test_missing_capabilities_detection():

    registry = CapabilityRegistry()
    descriptor = CapabilityDescriptor(
        "cap1",
        "Alpha",
        "Alpha capability",
        "1.0",
        ("input",),
        ("output",),
        "LOW",
        datetime(2026, 2, 10, 12, 0, 0),
    )
    registry.register_capability(descriptor)

    reasoner = CapabilityReasoner(registry)

    goal = "needs: Alpha, Beta"
    missing = reasoner.detect_missing_capabilities(goal)

    assert missing == ["Beta"]


def test_deterministic_outputs():

    registry = CapabilityRegistry()
    descriptor = CapabilityDescriptor(
        "cap1",
        "Alpha",
        "Alpha capability",
        "1.0",
        ("input",),
        ("output",),
        "LOW",
        datetime(2026, 2, 10, 12, 0, 0),
    )
    registry.register_capability(descriptor)

    orchestrator = CapabilityReasoningOrchestrator(registry)
    goal = "needs: Alpha"

    first = orchestrator.evaluate(goal)
    second = orchestrator.evaluate(goal)

    assert first == second


def test_registry_not_modified():

    registry = CapabilityRegistry()
    descriptor = CapabilityDescriptor(
        "cap1",
        "Alpha",
        "Alpha capability",
        "1.0",
        ("input",),
        ("output",),
        "LOW",
        datetime(2026, 2, 10, 12, 0, 0),
    )
    registry.register_capability(descriptor)

    orchestrator = CapabilityReasoningOrchestrator(registry)
    before = registry.registry_snapshot()

    orchestrator.evaluate("needs: Alpha")

    after = registry.registry_snapshot()

    assert before == after
