from dataclasses import FrozenInstanceError
from time import time

import pytest

from jessica.meta_cognition.reasoning_drift_detector import ReasoningDriftDetector, ReasoningDriftReport
from jessica.meta_cognition.reasoning_monitor import ReasoningRecord


def _make_record(idx: int, confidence: float, depth: int) -> ReasoningRecord:
    return ReasoningRecord(
        record_id=f"r{idx}",
        reasoning_id=f"reason-{idx}",
        confidence_score=confidence,
        step_count=depth,
        timestamp=time(),
    )


def test_frozen_report():

    report = ReasoningDriftReport(False, 0.0, 0.0, 0, time())

    with pytest.raises(FrozenInstanceError):
        report.records_analyzed = 5


def test_no_drift():

    detector = ReasoningDriftDetector(window_size=4)
    records = [
        _make_record(1, 0.8, 4),
        _make_record(2, 0.79, 4),
        _make_record(3, 0.78, 4),
        _make_record(4, 0.77, 4),
    ]

    report = detector.detect_drift(records)

    assert report.drift_detected is False


def test_drift_detected():

    detector = ReasoningDriftDetector(window_size=4)
    records = [
        _make_record(1, 0.9, 5),
        _make_record(2, 0.88, 5),
        _make_record(3, 0.7, 4),
        _make_record(4, 0.68, 4),
    ]

    report = detector.detect_drift(records)

    assert report.drift_detected is True


def test_deterministic_runs():

    detector = ReasoningDriftDetector(window_size=4)
    records = [
        _make_record(1, 0.8, 4),
        _make_record(2, 0.79, 4),
        _make_record(3, 0.78, 4),
        _make_record(4, 0.77, 4),
    ]

    first = detector.detect_drift(records)
    second = detector.detect_drift(records)

    assert first.drift_detected == second.drift_detected
    assert first.confidence_trend == second.confidence_trend
    assert first.depth_trend == second.depth_trend
    assert first.records_analyzed == second.records_analyzed
