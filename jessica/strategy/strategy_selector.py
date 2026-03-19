from dataclasses import dataclass
from enum import Enum


class StrategyType(Enum):
    LINEAR = "LINEAR"
    EXPLORATORY = "EXPLORATORY"
    RISK_MINIMIZED = "RISK_MINIMIZED"
    RESOURCE_OPTIMIZED = "RESOURCE_OPTIMIZED"


@dataclass(frozen=True)
class StrategyProfile:
    strategy_type: StrategyType
    reason: str
    confidence: float


@dataclass(frozen=True)
class Goal:
    goal_id: str
    description: str
    risk_level: str
    uncertainty: float
    resource_cost: float


class StrategySelector:

    def __init__(self, uncertainty_threshold: float = 0.6, resource_threshold: float = 0.7):
        self._uncertainty_threshold = uncertainty_threshold
        self._resource_threshold = resource_threshold

    def select_strategy(self, goal: Goal) -> StrategyProfile:
        if goal.risk_level == "HIGH":
            return StrategyProfile(
                strategy_type=StrategyType.RISK_MINIMIZED,
                reason="High risk level detected.",
                confidence=0.9,
            )

        if goal.uncertainty > self._uncertainty_threshold:
            return StrategyProfile(
                strategy_type=StrategyType.EXPLORATORY,
                reason="High uncertainty detected.",
                confidence=0.8,
            )

        if goal.resource_cost > self._resource_threshold:
            return StrategyProfile(
                strategy_type=StrategyType.RESOURCE_OPTIMIZED,
                reason="High resource cost detected.",
                confidence=0.8,
            )

        return StrategyProfile(
            strategy_type=StrategyType.LINEAR,
            reason="Default linear strategy applied.",
            confidence=0.7,
        )
