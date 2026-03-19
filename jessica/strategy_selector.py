"""Phase 15 — Cognitive Strategy Layer: selector engine."""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from jessica.strategy_registry import StrategyRegistry
from jessica.strategy_audit import StrategyAudit


class StrategySelector:
    def __init__(self, registry: StrategyRegistry, audit: StrategyAudit) -> None:
        self.registry = registry
        self.audit = audit

    def analyze_task(self, task_input: str) -> Dict:
        metadata = self.derive_task_metadata(task_input)
        return metadata

    def derive_task_metadata(self, task_input: str) -> Dict:
        text = (task_input or "").strip().lower()
        if any(token in text for token in ["calculate", "sum", "math", "+", "-"]):
            return {"type": "math"}
        if any(token in text for token in ["plan", "steps", "workflow"]):
            return {"type": "planning"}
        return {"type": "general"}

    def choose_strategy(self, task_metadata: Dict):
        return self.registry.select_strategy(task_metadata)

    def log_strategy_selection(self, strategy_id: str, task_id: str) -> None:
        self.audit.record_strategy_use(task_id, strategy_id, datetime.now())
