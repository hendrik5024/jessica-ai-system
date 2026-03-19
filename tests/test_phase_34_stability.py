from jessica.reasoning.stability_orchestrator import StabilityOrchestrator


def test_stability_consistent():

    orch = StabilityOrchestrator()

    record = orch.evaluate("s1", "arb1", "Paris", "Paris")

    assert record.consistent is True


def test_stability_inconsistent():

    orch = StabilityOrchestrator()

    record = orch.evaluate("s2", "arb2", "Paris", "London")

    assert record.consistent is False
