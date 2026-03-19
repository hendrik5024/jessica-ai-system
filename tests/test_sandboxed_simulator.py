from __future__ import annotations

import statistics

from jessica.brain.dual_mind import DualMindEngine
from jessica.brain.sandboxed_simulator import SandboxedRealitySimulator


def test_simulation_count_clamps():
    simulator = SandboxedRealitySimulator(seed=7)

    low_result = simulator.simulate(
        context="Minor adjustment to documentation",
        action="Update documentation wording",
        num_simulations=3,
        seed=1,
    )
    assert len(low_result.trajectories) == simulator.min_simulations

    high_result = simulator.simulate(
        context="Large scale system overhaul",
        action="Rewrite core engine",
        num_simulations=500,
        seed=1,
    )
    assert len(high_result.trajectories) == simulator.max_simulations


def test_recommended_has_highest_score():
    simulator = SandboxedRealitySimulator(seed=11)
    result = simulator.simulate(
        context="Improve reliability of the pipeline",
        action="Refactor the scheduling system for stability",
        num_simulations=25,
        seed=2,
    )

    scores = [t.scores.combined for t in result.trajectories]
    assert result.recommended.scores.combined == max(scores)


def test_high_risk_actions_reduce_safety():
    simulator = SandboxedRealitySimulator(seed=5)

    safe_result = simulator.simulate(
        context="Review and clarify a process",
        action="Clarify logging strategy",
        num_simulations=20,
        seed=4,
    )
    risky_result = simulator.simulate(
        context="Production database action",
        action="Delete legacy data tables",
        num_simulations=20,
        seed=4,
    )

    safe_avg = statistics.mean(t.scores.safety for t in safe_result.trajectories)
    risky_avg = statistics.mean(t.scores.safety for t in risky_result.trajectories)

    assert safe_avg > risky_avg


def test_dual_mind_integration_simulates_recommendation():
    engine = DualMindEngine()
    simulator = SandboxedRealitySimulator(seed=3)

    user_model = {
        "values": ["stability", "clarity"],
        "goals": ["maintain reliability", "reduce cognitive load"],
        "preferences": {"tone": "concise"},
    }

    result = simulator.simulate_dual_mind_decision(
        engine=engine,
        context="We need to restructure a fragile codebase.",
        user_model=user_model,
        question="What is the safest refactor strategy?",
        num_simulations=15,
        seed=9,
    )

    assert result.dual_mind_response is not None
    assert "dual_mind_recommendation" in result.metadata
    assert result.recommended.scores.combined >= 0
