"""Phase 5.4 Recovery Orchestrator (advisory-only)."""
from __future__ import annotations

from typing import Any, Dict

from .recovery_analyzer import RecoveryAnalyzer


class RecoveryOrchestrator:
    """Coordinator for recovery advisory analysis (read-only)."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.analyzer = RecoveryAnalyzer(enabled=enabled)

    def interpret(self, outcome: Dict[str, Any]):
        if not self.enabled:
            return {
                "enabled": False,
                "analysis": None,
            }

        analysis = self.analyzer.analyze(outcome)
        return {
            "enabled": True,
            "analysis": analysis,
        }

    def enable(self) -> None:
        self.enabled = True
        self.analyzer.enable()

    def disable(self) -> None:
        self.enabled = False
        self.analyzer.disable()
