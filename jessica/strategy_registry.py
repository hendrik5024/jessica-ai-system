"""Phase 15 — Cognitive Strategy Layer: strategy registry."""

from __future__ import annotations

from typing import Dict, List

from jessica.strategy_definition import StrategyDefinition


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: Dict[str, StrategyDefinition] = {}
        self._order: List[str] = []

    def register_strategy(self, strategy: StrategyDefinition) -> None:
        if strategy.strategy_id in self._strategies:
            raise ValueError("Strategy already exists")
        self._strategies[strategy.strategy_id] = strategy
        self._order.append(strategy.strategy_id)

    def get_strategy(self, strategy_id: str) -> StrategyDefinition | None:
        return self._strategies.get(strategy_id)

    def list_strategies(self) -> List[StrategyDefinition]:
        return [self._strategies[sid] for sid in self._order]

    def select_strategy(self, task_metadata: Dict) -> StrategyDefinition | None:
        task_type = (task_metadata or {}).get("type")
        for sid in self._order:
            strategy = self._strategies[sid]
            match_type = strategy.selection_rules.get("type")
            if match_type and match_type == task_type:
                return strategy
        return self._strategies[self._order[0]] if self._order else None
