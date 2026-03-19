from jessica.strategy.strategic_coherence_orchestrator import StrategicCoherenceOrchestrator


def test_coherence_memory():

    orch = StrategicCoherenceOrchestrator()

    orch.record_direction("c1", "Build governance stability")

    history = orch.get_history()

    assert len(history) == 1
