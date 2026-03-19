from __future__ import annotations

from jessica.meta.self_directed_evolution import SelfDirectedEvolutionEngine


def test_blocks_irreversible_without_approval():
    engine = SelfDirectedEvolutionEngine()
    candidates = [
        {"skill": "core model tuning", "avg_severity": 8.0, "failures": 12},
        {"skill": "documentation", "avg_severity": 3.0, "failures": 2},
    ]

    decision = engine.choose_learning_target(
        candidates=candidates,
        user_alignment_score=0.8,
        allow_irreversible=False,
    )

    assert decision.requires_approval is True
    assert decision.constraints_passed is False
    assert "irreversible_requires_approval" in decision.violated_constraints


def test_allows_reversible_with_alignment():
    engine = SelfDirectedEvolutionEngine()
    candidates = [
        {"skill": "prompt clarity", "avg_severity": 6.0, "failures": 5},
    ]

    decision = engine.choose_learning_target(
        candidates=candidates,
        user_alignment_score=0.7,
        allow_irreversible=False,
    )

    assert decision.constraints_passed is True
    assert decision.target_skill == "prompt clarity"
