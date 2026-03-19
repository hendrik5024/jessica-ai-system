from jessica.strategy.strategic_stability_orchestrator import StrategicStabilityOrchestrator
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


def test_stability_monitor():

    orch = StrategicStabilityOrchestrator()

    plans = [
        LongHorizonPlanRecord("p1", "STABILITY_PRIORITY", "EXTENDED", "")
        for _ in range(3)
    ]

    record = orch.evaluate("s1", plans)

    assert record.stability_level == "STABLE"
