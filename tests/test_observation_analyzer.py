from typing import Any, cast

from jessica.core.observation_analyzer import ObservationAnalyzer


Cycle = dict[str, object]


def _cycle(
    status: str,
    duration: float,
    events: list[dict[str, object]] | None = None,
) -> Cycle:
    return {
        "status": status,
        "duration": duration,
        "events": events or [],
    }


def test_empty_history_has_structured_fields() -> None:
    analyzer = ObservationAnalyzer()

    result = analyzer.analyze([])

    assert result["cycles_observed"] == 0
    assert result["anomalies"] == []
    assert result["trends"] == {}
    assert result["risk_score"] == 0.0
    assert result["risk_level"] == "healthy"


def test_anomalies_and_risk_are_emitted_for_degradation() -> None:
    analyzer = ObservationAnalyzer()

    # First 5 healthy-ish, last 5 degraded to trigger trend + spike behavior.
    history: list[Cycle] = [
        _cycle("completed", 1.0, [{"event": "experiment_result", "payload": {"success": False}}]),
        _cycle("completed", 1.1, [{"event": "experiment_result", "payload": {"success": True}}]),
        _cycle("completed", 1.0, [{"event": "experiment_result", "payload": {"success": True}}]),
        _cycle("completed", 1.2, [{"event": "experiment_result", "payload": {"success": False}}]),
        _cycle("completed", 1.1, [{"event": "experiment_result", "payload": {"success": True}}]),
        _cycle("skipped", 3.5, [{"event": "experiment_result", "payload": {"success": False}}]),
        _cycle("skipped", 3.8, [{"event": "experiment_result", "payload": {"success": False}}]),
        _cycle("skipped", 4.2, [{"event": "experiment_result", "payload": {"success": False}}]),
        _cycle("aborted", 4.5, [{"event": "experiment_result", "payload": {"success": False}}]),
        _cycle("error", 4.8, [{"event": "experiment_result", "payload": {"success": False}}]),
    ]

    result = analyzer.analyze(history)

    assert result["cycles_observed"] == 10
    assert isinstance(result["anomalies"], list)
    anomalies = cast(list[dict[str, Any]], result["anomalies"])
    assert isinstance(anomalies, list)
    assert len(anomalies) >= 3
    assert result["risk_score"] > 0.3
    assert result["risk_level"] in {"caution", "critical"}
    assert "cycle_duration" in result["trends"]
    assert "failure_rate" in result["trends"]
    assert "experiment_success_rate" in result["trends"]

    anomaly_types = {str(item.get("type")) for item in anomalies}
    assert "duration_spike" in anomaly_types
    assert "skipped_cycle_streak" in anomaly_types or "skipped_cycle_frequency" in anomaly_types
    assert "experiment_failure_cluster" in anomaly_types


def test_risk_level_bands() -> None:
    analyzer = ObservationAnalyzer()

    healthy = analyzer.analyze([
        _cycle("completed", 1.0),
        _cycle("completed", 1.1),
        _cycle("completed", 1.0),
    ])
    assert healthy["risk_level"] == "healthy"

    caution = analyzer.analyze([
        _cycle("completed", 1.0),
        _cycle("aborted", 2.5),
        _cycle("error", 2.8),
        _cycle("skipped", 1.2),
        _cycle("skipped", 1.3),
    ])
    assert caution["risk_level"] in {"caution", "critical"}


def test_backward_compatible_alerts_still_present() -> None:
    analyzer = ObservationAnalyzer()

    history: list[Cycle] = [
        _cycle("skipped", 1.0),
        _cycle("skipped", 1.0),
        _cycle("skipped", 1.0),
        _cycle("completed", 3.0),
        _cycle("completed", 3.0),
        _cycle("completed", 3.0),
    ]

    result = analyzer.analyze(history)

    assert isinstance(result["alerts"], list)
    alerts = cast(list[str], result["alerts"])
    assert any("skipped" in message.lower() for message in alerts)
