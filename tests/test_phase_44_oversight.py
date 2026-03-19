from jessica.executive.oversight_orchestrator import ExecutiveOversightOrchestrator
from jessica.reasoning.guardrail_reflex_record import GuardrailReflexRecord
from jessica.reasoning.equilibrium_record import CognitiveEquilibriumRecord
from jessica.reasoning.strategy_record import ReasoningStrategyRecord


def test_oversight_generation():

    orch = ExecutiveOversightOrchestrator()

    guard = GuardrailReflexRecord("g1", "ACTIVE", "risk observed")
    eq = CognitiveEquilibriumRecord("e1", "MODERATE", 0.6, "")
    strat = ReasoningStrategyRecord("s1", "MAINTAIN_BALANCE", "NORMAL", "")

    record = orch.generate("o1", guard, eq, strat)

    assert record.guardrail_state == "ACTIVE"
    assert record.strategy_state == "MAINTAIN_BALANCE"
