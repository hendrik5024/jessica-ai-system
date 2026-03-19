from jessica.strategy.strategic_governance_orchestrator import StrategicGovernanceOrchestrator
from jessica.planning.long_horizon_plan_record import LongHorizonPlanRecord


def test_strategic_governance():

    orch = StrategicGovernanceOrchestrator()

    plans = [
        LongHorizonPlanRecord("p1", "STABILITY_PRIORITY", "EXTENDED", ""),
        LongHorizonPlanRecord("p2", "NORMAL_STRATEGIC_FLOW", "EXTENDED", ""),
    ]

    record = orch.evaluate("g1", plans)

    assert record.plan_count == 2
    assert record.stability_state == "MULTI_PLAN_BALANCING"
