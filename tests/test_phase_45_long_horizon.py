from jessica.planning.long_horizon_plan_orchestrator import LongHorizonPlanOrchestrator
from jessica.executive.oversight_record import ExecutiveOversightRecord


def test_long_horizon_plan():

    orch = LongHorizonPlanOrchestrator()

    oversight = ExecutiveOversightRecord(
        "o1",
        "ACTIVE",
        "MODERATE",
        "MAINTAIN_BALANCE",
        "",
    )

    plan = orch.generate("p1", oversight)

    assert plan.strategic_state == "STABILITY_PRIORITY"
