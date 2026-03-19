from jessica.strategy.strategic_correction_orchestrator import StrategicCorrectionOrchestrator


def test_correction_advisory():

    orch = StrategicCorrectionOrchestrator()

    record = orch.recommend("c1", "HIGH_LOAD")

    assert "reducing" in record.recommendation.lower()
