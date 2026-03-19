"""Phase 5.4 Recovery Analyzer (advisory-only, read-only)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from .execution_tracker import ExecutionOutcome, ExecutionStatus
from .failure_classifier import FailureClassifier, FailureCategory, ClassificationResult
from .recovery_option import RecoveryOption, RecoveryRisk

_logger = logging.getLogger(__name__)


class RecoveryAnalyzer:
    """Analyzes ExecutionOutcome data and proposes recovery options (advisory only)."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.classifier = FailureClassifier()

    def analyze(self, outcome: ExecutionOutcome | Dict[str, Any]) -> Dict[str, Any]:
        """Analyze outcome and propose recovery options.

        Returns read-only analysis dict with classification and options.
        """
        if not self.enabled:
            return {
                "enabled": False,
                "classification": None,
                "options": [],
            }

        classification = self.classifier.classify(outcome)
        options = self._generate_options(classification)

        analysis = {
            "enabled": True,
            "classification": {
                "category": classification.category.value,
                "reason": classification.reason,
                "confidence": classification.confidence,
            },
            "options": [self._option_to_dict(o) for o in options],
        }

        _logger.info("[RecoveryAnalyzer] classification=%s options=%d", classification.category.value, len(options))
        return analysis

    def _generate_options(self, classification: ClassificationResult) -> List[RecoveryOption]:
        """Generate advisory recovery options (deterministic, no execution)."""
        category = classification.category

        if category == FailureCategory.SUCCESS:
            return []

        if category == FailureCategory.TIMEOUT:
            return [
                RecoveryOption(
                    description="Check system responsiveness and try again if appropriate.",
                    suggested_manual_action="Verify the app is responsive; if so, create a NEW intent to retry.",
                    risk_level=RecoveryRisk.MEDIUM,
                    reversibility_score=0.8,
                    requires_new_intent=True,
                ),
            ]

        if category == FailureCategory.UI_MISMATCH:
            return [
                RecoveryOption(
                    description="UI may have changed or target element not present.",
                    suggested_manual_action="Confirm the UI state manually and adjust intent parameters.",
                    risk_level=RecoveryRisk.LOW,
                    reversibility_score=0.9,
                    requires_new_intent=True,
                ),
            ]

        if category == FailureCategory.FOCUS_LOST:
            return [
                RecoveryOption(
                    description="Target window may not have focus.",
                    suggested_manual_action="Bring the target window to front and create a NEW intent.",
                    risk_level=RecoveryRisk.LOW,
                    reversibility_score=0.9,
                    requires_new_intent=True,
                ),
            ]

        if category == FailureCategory.PERMISSION_DENIED:
            return [
                RecoveryOption(
                    description="Insufficient permissions for the requested action.",
                    suggested_manual_action="Check permissions or run the app with appropriate rights, then create a NEW intent.",
                    risk_level=RecoveryRisk.HIGH,
                    reversibility_score=0.6,
                    requires_new_intent=True,
                ),
            ]

        if category == FailureCategory.INPUT_REJECTED:
            return [
                RecoveryOption(
                    description="Input may be invalid or rejected by the target application.",
                    suggested_manual_action="Validate the input manually and create a NEW intent with corrected parameters.",
                    risk_level=RecoveryRisk.MEDIUM,
                    reversibility_score=0.8,
                    requires_new_intent=True,
                ),
            ]

        if category == FailureCategory.SYSTEM_INTERRUPTION:
            return [
                RecoveryOption(
                    description="Execution was interrupted.",
                    suggested_manual_action="Resolve the interruption and create a NEW intent if needed.",
                    risk_level=RecoveryRisk.MEDIUM,
                    reversibility_score=0.7,
                    requires_new_intent=True,
                ),
            ]

        return [
            RecoveryOption(
                description="Unknown failure occurred.",
                suggested_manual_action="Review the error and decide whether to create a NEW intent.",
                risk_level=RecoveryRisk.MEDIUM,
                reversibility_score=0.7,
                requires_new_intent=True,
            )
        ]

    @staticmethod
    def _option_to_dict(option: RecoveryOption) -> Dict[str, Any]:
        return {
            "description": option.description,
            "suggested_manual_action": option.suggested_manual_action,
            "risk_level": option.risk_level.value,
            "reversibility_score": option.reversibility_score,
            "requires_new_intent": option.requires_new_intent,
        }

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False
