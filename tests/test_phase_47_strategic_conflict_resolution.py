from jessica.strategy.strategic_conflict_resolution_orchestrator import StrategicConflictResolutionOrchestrator
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


def test_conflict_resolution():

    orch = StrategicConflictResolutionOrchestrator()

    plans = [
        LongHorizonPlanRecord("p1", "STABILITY_PRIORITY", "EXTENDED", ""),
        LongHorizonPlanRecord("p2", "EXPANSION_PRIORITY", "EXTENDED", ""),
    ]

    record = orch.resolve("r1", plans)

    assert record.conflicting_plan_count == 2
    assert record.resolution_strategy == "PRIORITIZE_STABILITY"
