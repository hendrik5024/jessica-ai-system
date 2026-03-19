from jessica.reasoning.consistency_monitor_orchestrator import ConsistencyMonitorOrchestrator


def test_consistency_monitor_basic():

    orch = ConsistencyMonitorOrchestrator()

    rec = orch.monitor("c1", [0.8, 0.85, 0.82])

    assert rec.contradiction_detected is False
    assert rec.consistency_score > 0.7


def test_consistency_monitor_drift():

    orch = ConsistencyMonitorOrchestrator()

    rec = orch.monitor("c2", [0.2, 0.9])

    assert rec.drift_detected is True
