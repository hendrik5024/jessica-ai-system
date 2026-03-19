from dataclasses import FrozenInstanceError
from datetime import datetime
import pytest

from jessica.strategy.active_goal_set import ActiveGoalSet
from jessica.strategy.conflict_registry import ConflictRegistry
from jessica.strategy.goal_conflict_detector import GoalConflictDetector
from jessica.strategy.goal_record import GoalRecord


def test_goal_record_immutable():

    goal = GoalRecord(
        "g1",
        "Stabilize operations",
        ("budget",),
        1,
        datetime(2026, 2, 10, 12, 0, 0),
    )

    with pytest.raises(FrozenInstanceError):
        goal.description = "Change"


def test_conflict_detection_deterministic():

    detector = GoalConflictDetector()

    goal_a = GoalRecord(
        "g1",
        "Reduce costs",
        ("budget", "staff"),
        1,
        datetime(2026, 2, 10, 12, 0, 0),
    )
    goal_b = GoalRecord(
        "g2",
        "Scale marketing",
        ("budget",),
        2,
        datetime(2026, 2, 10, 12, 1, 0),
    )

    active_set = ActiveGoalSet(
        "set1",
        (goal_a, goal_b),
        datetime(2026, 2, 10, 12, 2, 0),
    )

    first = detector.detect_conflicts(active_set)
    second = detector.detect_conflicts(active_set)

    assert first == second


def test_conflict_pairs_reported():

    detector = GoalConflictDetector()

    goal_a = GoalRecord(
        "g1",
        "Reduce costs",
        ("budget",),
        1,
        datetime(2026, 2, 10, 12, 0, 0),
    )
    goal_b = GoalRecord(
        "g2",
        "Expand",
        ("budget",),
        2,
        datetime(2026, 2, 10, 12, 1, 0),
    )

    active_set = ActiveGoalSet(
        "set1",
        (goal_a, goal_b),
        datetime(2026, 2, 10, 12, 2, 0),
    )

    assessment = detector.detect_conflicts(active_set)

    assert assessment.conflict_detected is True
    assert assessment.conflicting_goal_pairs == (("g1", "g2"),)


def test_registry_append_only():

    registry = ConflictRegistry()

    goal = GoalRecord(
        "g1",
        "Reduce costs",
        ("budget",),
        1,
        datetime(2026, 2, 10, 12, 0, 0),
    )

    active_set = ActiveGoalSet(
        "set1",
        (goal,),
        datetime(2026, 2, 10, 12, 2, 0),
    )

    detector = GoalConflictDetector()
    assessment = detector.detect_conflicts(active_set)

    registry.add(assessment)
    registry.add(assessment)

    history = registry.history()
    assert len(history) == 2

    history.append(assessment)
    assert len(registry.history()) == 2


def test_disable_flag_returns_no_conflict():

    detector = GoalConflictDetector()
    detector.disable()

    goal_a = GoalRecord(
        "g1",
        "Reduce costs",
        ("budget",),
        1,
        datetime(2026, 2, 10, 12, 0, 0),
    )
    goal_b = GoalRecord(
        "g2",
        "Expand",
        ("budget",),
        2,
        datetime(2026, 2, 10, 12, 1, 0),
    )

    active_set = ActiveGoalSet(
        "set1",
        (goal_a, goal_b),
        datetime(2026, 2, 10, 12, 2, 0),
    )

    assessment = detector.detect_conflicts(active_set)

    assert assessment.conflict_detected is False
    assert assessment.conflicting_goal_pairs == ()
    assert assessment.explanation == "Conflict detection disabled."
