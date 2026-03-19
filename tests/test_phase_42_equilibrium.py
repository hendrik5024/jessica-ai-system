from jessica.reasoning.equilibrium_orchestrator import CognitiveEquilibriumOrchestrator
from jessica.reasoning.guardrail_record import GuardrailRecord
from jessica.reasoning.metacognition_record import MetaCognitionRecord


def test_equilibrium_unstable():

    orch = CognitiveEquilibriumOrchestrator()

    meta = MetaCognitionRecord("m1", 0.5, 0.5, "LOW", True, "ATTENTION_REQUIRED", "")
    guard = GuardrailRecord("g1", "HIGH", True, True, "")

    rec = orch.evaluate("e1", meta, guard)

    assert rec.equilibrium_state == "UNSTABLE"


def test_equilibrium_stable():

    orch = CognitiveEquilibriumOrchestrator()

    meta = MetaCognitionRecord("m2", 0.95, 0.95, "HIGH", False, "OPTIMAL", "")
    guard = GuardrailRecord("g2", "LOW", False, False, "")

    rec = orch.evaluate("e2", meta, guard)

    assert rec.equilibrium_state == "STABLE"
