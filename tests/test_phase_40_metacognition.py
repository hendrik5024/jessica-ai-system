from jessica.reasoning.metacognition_orchestrator import MetaCognitionOrchestrator


def test_meta_optimal():

    orch = MetaCognitionOrchestrator()

    rec = orch.evaluate(
        "m1",
        reasoning_score=0.9,
        consistency_score=0.9,
        stability_level="HIGH",
        drift_detected=False,
    )

    assert rec.overall_status == "OPTIMAL"


def test_meta_attention():

    orch = MetaCognitionOrchestrator()

    rec = orch.evaluate(
        "m2",
        reasoning_score=0.6,
        consistency_score=0.6,
        stability_level="LOW",
        drift_detected=True,
    )

    assert rec.overall_status == "ATTENTION_REQUIRED"
