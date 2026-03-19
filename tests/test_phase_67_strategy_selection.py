from dataclasses import FrozenInstanceError

import pytest

from jessica.strategy.strategy_selector import Goal, StrategyProfile, StrategySelector, StrategyType


def test_deterministic_selection():

    selector = StrategySelector()
    goal = Goal("g1", "Improve onboarding", "LOW", 0.2, 0.2)

    first = selector.select_strategy(goal)
    second = selector.select_strategy(goal)

    assert first == second


def test_rule_mapping_risk():

    selector = StrategySelector()
    goal = Goal("g1", "Improve onboarding", "HIGH", 0.2, 0.2)

    profile = selector.select_strategy(goal)

    assert profile.strategy_type == StrategyType.RISK_MINIMIZED


def test_rule_mapping_uncertainty():

    selector = StrategySelector()
    goal = Goal("g1", "Improve onboarding", "LOW", 0.9, 0.2)

    profile = selector.select_strategy(goal)

    assert profile.strategy_type == StrategyType.EXPLORATORY


def test_rule_mapping_resource_cost():

    selector = StrategySelector()
    goal = Goal("g1", "Improve onboarding", "LOW", 0.2, 0.9)

    profile = selector.select_strategy(goal)

    assert profile.strategy_type == StrategyType.RESOURCE_OPTIMIZED


def test_profile_frozen():

    profile = StrategyProfile(StrategyType.LINEAR, "Default", 0.7)

    with pytest.raises(FrozenInstanceError):
        profile.reason = "Change"


def test_no_side_effects():

    selector = StrategySelector()
    goal = Goal("g1", "Improve onboarding", "LOW", 0.2, 0.2)

    selector.select_strategy(goal)

    assert goal.description == "Improve onboarding"
    assert goal.risk_level == "LOW"
