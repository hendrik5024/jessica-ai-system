from jessica.reasoning.integrity_orchestrator import IntegrityOrchestrator


def test_integrity_pass():

    orch = IntegrityOrchestrator()

    record = orch.verify("i1", "r1", True, True, True)

    assert record.integrity_passed is True


def test_integrity_fail():

    orch = IntegrityOrchestrator()

    record = orch.verify("i2", "r2", True, False, True)

    assert record.integrity_passed is False
