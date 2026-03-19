from jessica.reasoning.consistency_orchestrator import ReasoningConsistencyOrchestrator


def test_reasoning_consistency_detection():

    orchestrator = ReasoningConsistencyOrchestrator()

    steps = [
        "earth is round",
        "not earth is round"
    ]

    report = orchestrator.analyze("test1", steps)

    assert report.contradictions_found is True
    assert len(report.contradiction_descriptions) > 0


def test_reasoning_consistency_clean():

    orchestrator = ReasoningConsistencyOrchestrator()

    steps = [
        "earth is round",
        "earth rotates"
    ]

    report = orchestrator.analyze("test2", steps)

    assert report.contradictions_found is False
