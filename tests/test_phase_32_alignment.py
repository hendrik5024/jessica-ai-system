from jessica.reasoning.alignment_orchestrator import AlignmentOrchestrator


def test_alignment_detects_divergence():

    orch = AlignmentOrchestrator()

    answers = [
        "Paris",
        "London"
    ]

    report = orch.evaluate("a1", answers)

    assert report.aligned is False
    assert len(report.divergence_notes) > 0


def test_alignment_clean():

    orch = AlignmentOrchestrator()

    answers = [
        "Paris",
        "Paris"
    ]

    report = orch.evaluate("a2", answers)

    assert report.aligned is True
