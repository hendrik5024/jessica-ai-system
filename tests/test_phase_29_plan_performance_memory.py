from jessica.planning import PlanPerformanceMemory, PlanEvaluation


def test_plan_performance_memory():

    memory = PlanPerformanceMemory()

    eval1 = PlanEvaluation("plan1", 0.5, "ok")
    eval2 = PlanEvaluation("plan2", 0.9, "better")

    memory.record("goal1", eval1)
    memory.record("goal1", eval2)

    best = memory.best_plan("goal1")

    assert best.plan_id == "plan2"
