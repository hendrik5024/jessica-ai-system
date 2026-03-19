from dataclasses import FrozenInstanceError
from datetime import datetime
import pytest

from jessica.strategy.drift_detector import DriftDetector
from jessica.strategy.drift_registry import DriftRegistry
from jessica.strategy.operational_activity_snapshot import OperationalActivitySnapshot
from jessica.strategy.strategic_direction_record import StrategicDirectionRecord


def test_records_immutable():

    direction = StrategicDirectionRecord(
        "d1",
        "Maintain stability",
        1,
        datetime(2026, 2, 10, 12, 0, 0),
        {"source": "governance"},
    )

    with pytest.raises(FrozenInstanceError):
        direction.description = "Change"


def test_deterministic_drift_detection():

    detector = DriftDetector()

    direction = StrategicDirectionRecord(
        "d1",
        "Maintain stability",
        1,
        datetime(2026, 2, 10, 12, 0, 0),
        {"source": "governance"},
    )

    activity = OperationalActivitySnapshot(
        "s1",
        "Maintain stability in operations",
        ("Maintain stability",),
        datetime(2026, 2, 10, 12, 5, 0),
    )

    first = detector.detect_drift(direction, activity)
    second = detector.detect_drift(direction, activity)

    assert first == second


def test_disable_flag_returns_no_drift():

    detector = DriftDetector()
    detector.disable()

    direction = StrategicDirectionRecord(
        "d1",
        "Maintain stability",
        1,
        datetime(2026, 2, 10, 12, 0, 0),
        {"source": "governance"},
    )

    activity = OperationalActivitySnapshot(
        "s1",
        "Expand aggressively",
        ("Expand",),
        datetime(2026, 2, 10, 12, 5, 0),
    )

    assessment = detector.detect_drift(direction, activity)

    assert assessment.drift_detected is False
    assert assessment.drift_score == 0.0
    assert assessment.explanation == "Drift detection disabled."


def test_registry_append_only():

    registry = DriftRegistry()

    direction = StrategicDirectionRecord(
        "d1",
        "Maintain stability",
        1,
        datetime(2026, 2, 10, 12, 0, 0),
        {"source": "governance"},
    )

    activity = OperationalActivitySnapshot(
        "s1",
        "Expand aggressively",
        ("Expand",),
        datetime(2026, 2, 10, 12, 5, 0),
    )

    detector = DriftDetector()
    assessment = detector.detect_drift(direction, activity)

    registry.add(assessment)
    registry.add(assessment)

    history = registry.history()
    assert len(history) == 2

    history.append(assessment)
    assert len(registry.history()) == 2
