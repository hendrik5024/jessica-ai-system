from dataclasses import FrozenInstanceError
from datetime import datetime
import inspect

import pytest

from jessica.strategy.capability_descriptor import CapabilityDescriptor
from jessica.strategy.capability_orchestrator import CapabilityOrchestrator
from jessica.strategy.capability_registry import CapabilityRegistry


def test_descriptor_immutable():

    descriptor = CapabilityDescriptor(
        "cap1",
        "StrategyEval",
        "Evaluates strategy alignment",
        "1.0",
        ("strategy",),
        ("evaluation",),
        "LOW",
        datetime(2026, 2, 10, 12, 0, 0),
    )

    with pytest.raises(FrozenInstanceError):
        descriptor.name = "Changed"


def test_registry_append_only():

    registry = CapabilityRegistry()

    descriptor = CapabilityDescriptor(
        "cap1",
        "StrategyEval",
        "Evaluates strategy alignment",
        "1.0",
        ("strategy",),
        ("evaluation",),
        "LOW",
        datetime(2026, 2, 10, 12, 0, 0),
    )

    registry.register_capability(descriptor)
    registry.register_capability(descriptor)

    snapshot = registry.registry_snapshot()
    assert len(snapshot) == 1

    snapshot.append(descriptor)
    assert len(registry.registry_snapshot()) == 1


def test_registry_deterministic_order():

    registry = CapabilityRegistry()

    first = CapabilityDescriptor(
        "cap1",
        "First",
        "First capability",
        "1.0",
        ("a",),
        ("b",),
        "LOW",
        datetime(2026, 2, 10, 12, 0, 0),
    )
    second = CapabilityDescriptor(
        "cap2",
        "Second",
        "Second capability",
        "1.0",
        ("c",),
        ("d",),
        "LOW",
        datetime(2026, 2, 10, 12, 1, 0),
    )

    registry.register_capability(first)
    registry.register_capability(second)

    listed = registry.list_capabilities()
    assert [cap.capability_id for cap in listed] == ["cap1", "cap2"]


def test_capability_lookup_success():

    registry = CapabilityRegistry()
    descriptor = CapabilityDescriptor(
        "cap1",
        "StrategyEval",
        "Evaluates strategy alignment",
        "1.0",
        ("strategy",),
        ("evaluation",),
        "LOW",
        datetime(2026, 2, 10, 12, 0, 0),
    )

    registry.register_capability(descriptor)

    assert registry.get_capability("cap1") == descriptor


def test_capability_lookup_failure():

    registry = CapabilityRegistry()

    assert registry.get_capability("missing") is None


def test_orchestrator_read_only_access():

    registry = CapabilityRegistry()
    descriptor = CapabilityDescriptor(
        "cap1",
        "StrategyEval",
        "Evaluates strategy alignment",
        "1.0",
        ("strategy",),
        ("evaluation",),
        "LOW",
        datetime(2026, 2, 10, 12, 0, 0),
    )

    registry.register_capability(descriptor)

    orchestrator = CapabilityOrchestrator(registry)

    assert orchestrator.resolve_capability("StrategyEval") == descriptor
    assert orchestrator.list_available_capabilities() == [descriptor]


def test_no_execution_methods_exist():

    registry = CapabilityRegistry()
    orchestrator = CapabilityOrchestrator(registry)

    for name, _ in inspect.getmembers(orchestrator, predicate=inspect.ismethod):
        assert "execute" not in name.lower()
