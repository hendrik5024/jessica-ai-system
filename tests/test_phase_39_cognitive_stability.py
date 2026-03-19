from jessica.reasoning.cognitive_stability_orchestrator import CognitiveStabilityOrchestrator


def test_stability_high():

    orch = CognitiveStabilityOrchestrator()

    rec = orch.evaluate("s1", 0.9, 0.85)

    assert rec.stability_level == "HIGH"
    assert rec.instability_detected is False


def test_stability_low():

    orch = CognitiveStabilityOrchestrator()

    rec = orch.evaluate("s2", 0.2, 0.3)

    assert rec.instability_detected is True
