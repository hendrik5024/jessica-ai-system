from dataclasses import FrozenInstanceError, dataclass

import pytest

from jessica.meta_cognition.reasoning_monitor import ReasoningMetrics, ReasoningQualityMonitor


@dataclass(frozen=True)
class DummyReasoningTrace:
    reasoning_id: str
    final_confidence: float
    steps: list[str]


def test_frozen_dataclasses():

    metrics = ReasoningMetrics(2, 0.7, 3.0)

    with pytest.raises(FrozenInstanceError):
        metrics.total_reasonings = 3


def test_record_creation_and_append_only():

    monitor = ReasoningQualityMonitor()
    trace = DummyReasoningTrace("r1", 0.8, ["a", "b"])

    record_one = monitor.record_reasoning(trace)
    record_two = monitor.record_reasoning(trace)

    history = monitor.history()
    assert len(history) == 2
    assert history[0] == record_one
    assert history[1] == record_two

    history.append(record_one)
    assert len(monitor.history()) == 2


def test_deterministic_metrics():

    monitor = ReasoningQualityMonitor()
    trace_one = DummyReasoningTrace("r1", 0.8, ["a", "b"])
    trace_two = DummyReasoningTrace("r2", 0.6, ["a", "b", "c"])

    monitor.record_reasoning(trace_one)
    monitor.record_reasoning(trace_two)

    first = monitor.compute_metrics()
    second = monitor.compute_metrics()

    assert first == second
