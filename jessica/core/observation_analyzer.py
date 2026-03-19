from __future__ import annotations

from collections import Counter
from typing import Any, cast


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _direction(recent: float, baseline: float, threshold: float = 0.05) -> str:
    if baseline <= 0.0:
        return "stable"
    delta_ratio = (recent - baseline) / baseline
    if delta_ratio > threshold:
        return "up"
    if delta_ratio < -threshold:
        return "down"
    return "stable"


def _risk_level(score: float) -> str:
    if score < 0.3:
        return "healthy"
    if score < 0.6:
        return "caution"
    return "critical"


class ObservationAnalyzer:
    """Analyze cycle-level world-state history for trend and risk signals."""

    def analyze(self, history: list[dict[str, Any]]) -> dict[str, Any]:
        if not history:
            return {
                "cycles_observed": 0,
                "status_breakdown": {},
                "event_breakdown": {},
                "average_cycle_duration": 0.0,
                "recent_average_cycle_duration": 0.0,
                "duration_spike": False,
                "skipped_streak": 0,
                "failure_rate": 0.0,
                "experiment_success_rate": None,
                "trends": {},
                "anomalies": [],
                "risk_score": 0.0,
                "risk_level": "healthy",
                "alerts": [],
            }

        status_counter: Counter[str] = Counter()
        event_counter: Counter[str] = Counter()
        durations: list[float] = []
        experiment_results: list[bool] = []
        cycle_failures: list[bool] = []

        for cycle in history:
            status = str(cycle.get("status", "unknown"))
            status_counter[status] += 1
            cycle_failures.append(status in {"error", "aborted", "skipped"})

            duration = cycle.get("duration")
            if isinstance(duration, (int, float)):
                durations.append(float(duration))

            events_any = cycle.get("events", [])
            if isinstance(events_any, list):
                events = cast(list[Any], events_any)
                for raw_event in events:
                    if not isinstance(raw_event, dict):
                        continue

                    event = cast(dict[str, Any], raw_event)

                    name = str(event.get("event", "unknown"))
                    event_counter[name] += 1

                    if name == "experiment_result":
                        payload_any = event.get("payload")
                        if isinstance(payload_any, dict):
                            payload = cast(dict[str, Any], payload_any)
                            success = payload.get("success")
                            if isinstance(success, bool):
                                experiment_results.append(success)

        average_duration = (sum(durations) / len(durations)) if durations else 0.0
        recent_durations = durations[-5:]
        recent_average_duration = (sum(recent_durations) / len(recent_durations)) if recent_durations else 0.0

        duration_spike = bool(
            average_duration > 0.0 and recent_average_duration > average_duration * 1.5
        )

        skipped_streak = 0
        for cycle in reversed(history):
            if str(cycle.get("status")) != "skipped":
                break
            skipped_streak += 1
        skipped_total = int(status_counter.get("skipped", 0))

        total_cycles = len(history)
        failure_cycles = (
            status_counter.get("error", 0)
            + status_counter.get("aborted", 0)
            + status_counter.get("skipped", 0)
        )
        failure_rate = failure_cycles / total_cycles if total_cycles else 0.0

        experiment_success_rate: float | None = None
        if experiment_results:
            successes = sum(1 for ok in experiment_results if ok)
            experiment_success_rate = successes / len(experiment_results)

        # Trend extraction (recent window vs baseline/previous window).
        recent_window = min(5, total_cycles)
        recent_failures = cycle_failures[-recent_window:]
        previous_failures = cycle_failures[-(recent_window * 2):-recent_window]

        recent_failure_rate = (
            (sum(1 for failed in recent_failures if failed) / len(recent_failures))
            if recent_failures
            else 0.0
        )
        previous_failure_rate = (
            (sum(1 for failed in previous_failures if failed) / len(previous_failures))
            if previous_failures
            else None
        )

        experiment_recent_success_rate: float | None = None
        experiment_previous_success_rate: float | None = None
        if experiment_results:
            recent_exp = experiment_results[-5:]
            if recent_exp:
                experiment_recent_success_rate = sum(1 for ok in recent_exp if ok) / len(recent_exp)

            previous_exp = experiment_results[-10:-5]
            if previous_exp:
                experiment_previous_success_rate = sum(1 for ok in previous_exp if ok) / len(previous_exp)

        trends: dict[str, Any] = {
            "cycle_duration": {
                "baseline": round(average_duration, 4),
                "recent": round(recent_average_duration, 4),
                "direction": _direction(recent_average_duration, average_duration),
                "delta_ratio": (
                    round((recent_average_duration - average_duration) / average_duration, 4)
                    if average_duration > 0.0
                    else 0.0
                ),
            },
            "failure_rate": {
                "overall": round(failure_rate, 4),
                "recent": round(recent_failure_rate, 4),
                "previous": (
                    round(previous_failure_rate, 4)
                    if isinstance(previous_failure_rate, float)
                    else None
                ),
                "direction": (
                    _direction(recent_failure_rate, previous_failure_rate)
                    if isinstance(previous_failure_rate, float)
                    else "stable"
                ),
            },
            "experiment_success_rate": {
                "overall": (
                    round(experiment_success_rate, 4)
                    if isinstance(experiment_success_rate, float)
                    else None
                ),
                "recent": (
                    round(experiment_recent_success_rate, 4)
                    if isinstance(experiment_recent_success_rate, float)
                    else None
                ),
                "previous": (
                    round(experiment_previous_success_rate, 4)
                    if isinstance(experiment_previous_success_rate, float)
                    else None
                ),
                "direction": (
                    _direction(experiment_recent_success_rate, experiment_previous_success_rate)
                    if isinstance(experiment_recent_success_rate, float)
                    and isinstance(experiment_previous_success_rate, float)
                    else "stable"
                ),
            },
        }

        anomalies: list[dict[str, Any]] = []
        alerts: list[str] = []
        if duration_spike:
            duration_confidence = _clamp01(
                ((recent_average_duration / average_duration) - 1.0) / 0.5
            ) if average_duration > 0.0 else 0.5
            anomalies.append({
                "type": "duration_spike",
                "severity": "high" if recent_average_duration > average_duration * 2.0 else "medium",
                "confidence": round(duration_confidence, 4),
                "metric": "cycle_duration",
                "value": round(recent_average_duration, 4),
                "baseline": round(average_duration, 4),
            })
            alerts.append("Cycle duration spike detected")

        if skipped_streak >= 3:
            anomalies.append({
                "type": "skipped_cycle_streak",
                "severity": "high" if skipped_streak >= 5 else "medium",
                "confidence": round(_clamp01(skipped_streak / 5.0), 4),
                "metric": "skipped_streak",
                "value": skipped_streak,
            })
            alerts.append("Repeated skipped cycles detected")

        if skipped_total >= 3 and skipped_streak < 3:
            anomalies.append({
                "type": "skipped_cycle_frequency",
                "severity": "medium",
                "confidence": round(_clamp01(skipped_total / max(total_cycles, 1)), 4),
                "metric": "skipped_total",
                "value": skipped_total,
            })
            alerts.append("Repeated skipped cycles detected")

        if experiment_success_rate is not None and len(experiment_results) >= 5 and experiment_success_rate < 0.4:
            anomalies.append({
                "type": "experiment_failure_cluster",
                "severity": "high" if experiment_success_rate < 0.25 else "medium",
                "confidence": round(_clamp01((0.4 - experiment_success_rate) / 0.4), 4),
                "metric": "experiment_success_rate",
                "value": round(experiment_success_rate, 4),
                "threshold": 0.4,
            })
            alerts.append("Experiment success rate is degrading")

        if failure_rate >= 0.5:
            anomalies.append({
                "type": "high_failure_rate",
                "severity": "high" if failure_rate >= 0.7 else "medium",
                "confidence": round(_clamp01((failure_rate - 0.5) / 0.5), 4),
                "metric": "failure_rate",
                "value": round(failure_rate, 4),
                "threshold": 0.5,
            })
            alerts.append("Failure rate is elevated")

        if (
            isinstance(previous_failure_rate, float)
            and (recent_failure_rate - previous_failure_rate) > 0.15
        ):
            anomalies.append({
                "type": "failure_rate_trend_up",
                "severity": "medium",
                "confidence": round(_clamp01((recent_failure_rate - previous_failure_rate) / 0.5), 4),
                "metric": "failure_rate",
                "value": round(recent_failure_rate, 4),
                "previous": round(previous_failure_rate, 4),
            })
            alerts.append("Failure rate trend is increasing")

        duration_factor = (
            _clamp01((recent_average_duration - average_duration) / average_duration)
            if average_duration > 0.0 and recent_average_duration > average_duration
            else 0.0
        )
        skipped_factor = _clamp01(skipped_streak / 5.0)
        experiment_failure_factor = (
            (1.0 - experiment_success_rate)
            if isinstance(experiment_success_rate, float)
            else 0.0
        )

        risk_score = _clamp01(
            (failure_rate * 0.4)
            + (duration_factor * 0.2)
            + (skipped_factor * 0.2)
            + (experiment_failure_factor * 0.2)
        )
        risk_level = _risk_level(risk_score)

        return {
            "cycles_observed": total_cycles,
            "status_breakdown": dict(status_counter),
            "event_breakdown": dict(event_counter),
            "average_cycle_duration": round(average_duration, 4),
            "recent_average_cycle_duration": round(recent_average_duration, 4),
            "duration_spike": duration_spike,
            "skipped_streak": skipped_streak,
            "failure_rate": round(failure_rate, 4),
            "experiment_success_rate": (
                round(experiment_success_rate, 4)
                if isinstance(experiment_success_rate, float)
                else None
            ),
            "trends": trends,
            "anomalies": anomalies,
            "risk_score": round(risk_score, 4),
            "risk_level": risk_level,
            "alerts": alerts,
        }
