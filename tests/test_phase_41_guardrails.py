from jessica.reasoning.guardrail_orchestrator import GuardrailOrchestrator
from jessica.reasoning.metacognition_record import MetaCognitionRecord


def test_guardrail_high():

    orch = GuardrailOrchestrator()

    meta = MetaCognitionRecord(
        "m1", 0.5, 0.5, "LOW", True, "ATTENTION_REQUIRED", ""
    )

    rec = orch.evaluate("g1", meta)

    assert rec.reflex_level == "HIGH"
    assert rec.monitoring_escalated is True


def test_guardrail_low():

    orch = GuardrailOrchestrator()

    meta = MetaCognitionRecord(
        "m2", 0.95, 0.95, "HIGH", False, "OPTIMAL", ""
    )

    rec = orch.evaluate("g2", meta)

    assert rec.reflex_level == "LOW"
