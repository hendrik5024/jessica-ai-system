from dataclasses import dataclass


@dataclass(frozen=True)
class ReasoningStrategyRecord:
    strategy_id: str
    recommended_strategy: str
    reasoning_mode: str
    advisory: str
