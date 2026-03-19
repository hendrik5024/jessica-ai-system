from jessica.reasoning.confidence_orchestrator import ConfidenceOrchestrator


def test_confidence_basic():

    orch = ConfidenceOrchestrator()

    rec = orch.compute("c1", "r1", True, 0.8, 3, True)

    assert rec.final_confidence > 0.8


def test_confidence_penalty():

    orch = ConfidenceOrchestrator()

    rec = orch.compute("c2", "r2", False, 0.8, 2, True)

    assert rec.final_confidence < 0.8
