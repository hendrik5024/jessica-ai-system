from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.planning.meta_planner import MetaPlanner, PlanCandidate, PlanEvaluation
from jessica.reasoning.goal_decomposer import Goal


def test_candidate_generation_deterministic():

    planner = MetaPlanner()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))

    first = planner.generate_candidates(goal)
    second = planner.generate_candidates(goal)

    assert first == second


def test_scoring_formula():

    candidate = PlanCandidate(
        "p1",
        estimated_success=0.8,
        estimated_cost=0.4,
        risk_score=0.2,
        description="Test",
    )

    planner = MetaPlanner()
    score = planner._score_candidate(candidate)

    expected = (0.8 * 0.6) - (0.2 * 0.3) - (0.4 * 0.1)
    assert score == expected


def test_best_plan_selection():

    planner = MetaPlanner()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))

    selected, evaluation = planner.select_plan(goal)

    assert selected.plan_id == evaluation.selected_plan_id


def test_dataclasses_frozen():

    candidate = PlanCandidate(
        "p1",
        estimated_success=0.8,
        estimated_cost=0.4,
        risk_score=0.2,
        description="Test",
    )
    evaluation = PlanEvaluation("p1", 0.3, "Test")

    with pytest.raises(FrozenInstanceError):
        candidate.description = "Change"

    with pytest.raises(FrozenInstanceError):
        evaluation.score = 0.5


def test_no_side_effects():

    planner = MetaPlanner()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))

    planner.select_plan(goal)

    assert goal.description == "Improve onboarding"
