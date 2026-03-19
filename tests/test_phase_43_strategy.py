from jessica.reasoning.strategy_orchestrator import ReasoningStrategyOrchestrator
from jessica.reasoning.equilibrium_record import CognitiveEquilibriumRecord


def test_strategy_unstable():

    orch = ReasoningStrategyOrchestrator()

    eq = CognitiveEquilibriumRecord("e1", "UNSTABLE", 0.4, "")

    rec = orch.recommend("s1", eq)

    assert rec.recommended_strategy == "INCREASE_VERIFICATION"


def test_strategy_stable():

    orch = ReasoningStrategyOrchestrator()

    eq = CognitiveEquilibriumRecord("e2", "STABLE", 0.95, "")

    rec = orch.recommend("s2", eq)

    assert rec.recommended_strategy == "OPTIMAL_OPERATION"
