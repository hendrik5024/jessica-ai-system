from __future__ import annotations

from jessica.meta.meaning_engine import MeaningEngine


def test_default_graph_nodes_present():
    engine = MeaningEngine()
    nodes = engine.graph.nodes
    assert "user_well_being" in nodes
    assert "long_term_value" in nodes
    assert "trust" in nodes
    assert "growth" in nodes
    assert "creation" in nodes


def test_tradeoff_detection_short_vs_long_term():
    engine = MeaningEngine()
    decision = engine.evaluate_action(
        action="Take a short-term shortcut that harms long-term value",
        context="This is a short-term gain but long-term loss tradeoff",
    )
    assert any("Short-term" in tradeoff for tradeoff in decision.tradeoffs)


def test_choose_best_action_prefers_trust():
    engine = MeaningEngine()
    actions = [
        "Hide the issue to ship faster",
        "Be transparent and explain the risk",
    ]
    best_action, best_decision, scored = engine.choose_best_action(actions=actions)

    assert best_action == actions[1]
    assert best_decision.meaning_score >= scored[1][1].meaning_score
