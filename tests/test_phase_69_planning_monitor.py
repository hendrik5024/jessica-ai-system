from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from jessica.meta_cognition.planning_monitor import PlanningMetrics, PlanningPerformanceMonitor
from jessica.planning.meta_planner import PlanEvaluation
from jessica.reasoning.goal_decomposer import Goal


def test_record_creation_and_append_only():

    monitor = PlanningPerformanceMonitor()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))
    eval_one = PlanEvaluation("p1", 0.8, "Test")
    eval_two = PlanEvaluation("p2", 0.6, "Test")

    record_one = monitor.record_plan_selection(goal, eval_one)
    record_two = monitor.record_plan_selection(goal, eval_two)

    history = monitor.history()
    assert len(history) == 2
    assert history[0] == record_one
    assert history[1] == record_two

    history.append(record_one)
    assert len(monitor.history()) == 2


def test_deterministic_metrics():

    monitor = PlanningPerformanceMonitor()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))
    eval_one = PlanEvaluation("p1", 0.8, "Test")
    eval_two = PlanEvaluation("p2", 0.6, "Test")

    monitor.record_plan_selection(goal, eval_one)
    monitor.record_plan_selection(goal, eval_two)

    first = monitor.compute_metrics()
    second = monitor.compute_metrics()

    assert first == second


def test_frozen_dataclasses():

    metrics = PlanningMetrics(2, 0.7, 0.6)

    with pytest.raises(FrozenInstanceError):
        metrics.total_plans = 3


def test_reliability_computation():

    monitor = PlanningPerformanceMonitor()
    goal = Goal("g1", "Improve onboarding", 1, datetime(2026, 2, 10, 12, 0, 0))
    eval_one = PlanEvaluation("p1", 0.8, "Test")
    eval_two = PlanEvaluation("p2", 0.6, "Test")

    monitor.record_plan_selection(goal, eval_one)
    monitor.record_plan_selection(goal, eval_two)

    metrics = monitor.compute_metrics()

    assert metrics.total_plans == 2
    assert metrics.average_predicted_score == 0.7
    assert metrics.reliability_index > 0
