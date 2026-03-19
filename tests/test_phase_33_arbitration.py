from jessica.reasoning.arbitration_orchestrator import ArbitrationOrchestrator


def test_arbitration_selects_highest_confidence():

    orch = ArbitrationOrchestrator()

    answers = ["Paris", "London", "Rome"]
    confidence = [0.5, 0.9, 0.6]

    record = orch.decide("arb1", answers, 1.0, confidence)

    assert record.selected_answer == "London"


def test_arbitration_single_answer():

    orch = ArbitrationOrchestrator()

    answers = ["Paris"]
    confidence = [0.8]

    record = orch.decide("arb2", answers, 1.0, confidence)

    assert record.selected_answer == "Paris"
