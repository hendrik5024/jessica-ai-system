from __future__ import annotations

from jessica.meta.continuity_pressure import ContinuityPressureEngine


def test_contradiction_detection():
    engine = ContinuityPressureEngine(history_limit=10)

    engine.evaluate_response(response_text="I will always prioritize clarity.")
    report = engine.evaluate_response(response_text="I will not prioritize clarity anymore.")

    assert report.contradictions
    assert any("clarity" in c for c in report.contradictions)


def test_continuity_score_decreases_on_contradiction():
    engine = ContinuityPressureEngine(history_limit=10)

    baseline = engine.evaluate_response(response_text="I will support long-term value.")
    report = engine.evaluate_response(response_text="I will not support long-term value.")

    assert report.continuity_score < baseline.continuity_score


def test_no_contradiction_for_unrelated_claims():
    engine = ContinuityPressureEngine(history_limit=10)

    engine.evaluate_response(response_text="I will protect user well-being.")
    report = engine.evaluate_response(response_text="I will improve trust by being transparent.")

    assert not report.contradictions
