"""Action executor coordinator for Phase 5.2 - minimal embodiment.

Master coordinator that manages the complete execution flow:
1. Receive approved intent pipeline from Phase 5.1.5
2. Route to appropriate executor (keyboard/mouse)
3. Execute atomic action
4. Return outcome immediately
5. Maintain audit trail

Constraints:
- ONE intent → ONE atomic action → immediate return
- NO chaining, loops, or automation
- NO background execution
- ALL actions require explicit human approval
- FULL reversibility required
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Union

from jessica.execution.execution_tracker import ExecutionTracker, ExecutionOutcome, ExecutionStatus
from jessica.execution.keyboard_executor import KeyboardExecutor
from jessica.execution.mouse_executor import MouseExecutor


class ActionExecutor:
    """Master action coordinator for Phase 5.2 minimal embodiment."""

    def __init__(self, enabled: bool = True):
        """Initialize action executor.

        Args:
            enabled: Whether execution is enabled (reversible disable flag)
        """
        self.enabled = enabled
        self.tracker = ExecutionTracker(enabled=enabled)
        self.keyboard = KeyboardExecutor(enabled=enabled, tracker=self.tracker)
        self.mouse = MouseExecutor(enabled=enabled, tracker=self.tracker)

    def execute_from_pipeline(
        self,
        pipeline: Dict[str, Any],
    ) -> ExecutionOutcome:
        """Execute action from approved Phase 5.1.5 intent pipeline.

        Args:
            pipeline: Approved intent pipeline dict with structure:
                {
                    "pipeline_id": str,
                    "intent": {...},  # Intent object
                    "approval_result": {
                        "approval_id": str,
                        "decision": "approved",
                    },
                    "dry_run_result": {...},  # Dry-run simulation result
                    "status": "approved",  # Must be "approved"
                }

        Returns:
            ExecutionOutcome with execution status and details
        """
        if not self.enabled:
            return ExecutionOutcome(
                status=ExecutionStatus.CANCELLED,
                start_time=0,
                end_time=0,
                duration_ms=0,
                error_message="ActionExecutor is disabled",
            )

        # Validate pipeline
        if not self._validate_pipeline(pipeline):
            return ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=0,
                end_time=0,
                duration_ms=0,
                error_message="Invalid pipeline structure or not approved",
            )

        intent = pipeline.get("intent", {})
        intent_id = intent.get("intent_id", "unknown")
        action_name = intent.get("action_name", "unknown")
        parameters = intent.get("parameters", {})
        approval_id = pipeline.get("approval_result", {}).get("approval_id")

        # Route to appropriate executor based on action type
        if action_name.startswith("key_") or action_name in ("press_key", "type_text", "hotkey"):
            return self._execute_keyboard_action(
                intent_id, action_name, parameters, approval_id
            )
        elif action_name.startswith("mouse_") or action_name in ("click", "move", "scroll", "double_click"):
            return self._execute_mouse_action(
                intent_id, action_name, parameters, approval_id
            )
        else:
            return ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=0,
                end_time=0,
                duration_ms=0,
                error_message=f"Unknown action type: {action_name}",
            )

    def _execute_keyboard_action(
        self,
        intent_id: str,
        action_name: str,
        parameters: Dict[str, Any],
        approval_id: Optional[str],
    ) -> ExecutionOutcome:
        """Execute keyboard action through approved pipeline.

        Args:
            intent_id: ID of intent
            action_name: Name of action (press_key, type_text, hotkey)
            parameters: Action parameters
            approval_id: Approval ID

        Returns:
            ExecutionOutcome
        """
        context = {
            "action_type": "keyboard",
            "action_name": action_name,
        }

        if action_name in ("press_key", "key_press"):
            key = parameters.get("key", parameters.get("k"))
            if not key:
                return ExecutionOutcome(
                    status=ExecutionStatus.FAILED,
                    start_time=0,
                    end_time=0,
                    duration_ms=0,
                    error_message="Missing required parameter: key",
                )
            return self.keyboard.execute_key(intent_id, key, approval_id, context)

        elif action_name == "type_text":
            text = parameters.get("text", parameters.get("t"))
            if not text:
                return ExecutionOutcome(
                    status=ExecutionStatus.FAILED,
                    start_time=0,
                    end_time=0,
                    duration_ms=0,
                    error_message="Missing required parameter: text",
                )
            interval = parameters.get("interval", 0.05)
            return self.keyboard.execute_type(intent_id, text, approval_id, context, interval)

        elif action_name == "hotkey":
            keys = parameters.get("keys", [])
            if not keys:
                return ExecutionOutcome(
                    status=ExecutionStatus.FAILED,
                    start_time=0,
                    end_time=0,
                    duration_ms=0,
                    error_message="Missing required parameter: keys",
                )
            return self.keyboard.execute_hotkey(intent_id, keys, approval_id, context)

        else:
            return ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=0,
                end_time=0,
                duration_ms=0,
                error_message=f"Unknown keyboard action: {action_name}",
            )

    def _execute_mouse_action(
        self,
        intent_id: str,
        action_name: str,
        parameters: Dict[str, Any],
        approval_id: Optional[str],
    ) -> ExecutionOutcome:
        """Execute mouse action through approved pipeline.

        Args:
            intent_id: ID of intent
            action_name: Name of action (click, move, scroll, double_click)
            parameters: Action parameters
            approval_id: Approval ID

        Returns:
            ExecutionOutcome
        """
        context = {
            "action_type": "mouse",
            "action_name": action_name,
        }

        if action_name == "click":
            x = parameters.get("x")
            y = parameters.get("y")
            if x is None or y is None:
                return ExecutionOutcome(
                    status=ExecutionStatus.FAILED,
                    start_time=0,
                    end_time=0,
                    duration_ms=0,
                    error_message="Missing required parameters: x, y",
                )
            button = parameters.get("button", "left")
            return self.mouse.execute_click(intent_id, x, y, button, approval_id, context)

        elif action_name == "move":
            x = parameters.get("x")
            y = parameters.get("y")
            if x is None or y is None:
                return ExecutionOutcome(
                    status=ExecutionStatus.FAILED,
                    start_time=0,
                    end_time=0,
                    duration_ms=0,
                    error_message="Missing required parameters: x, y",
                )
            return self.mouse.execute_move(intent_id, x, y, approval_id, context)

        elif action_name == "scroll":
            direction = parameters.get("direction", "down")
            amount = parameters.get("amount", 3)
            return self.mouse.execute_scroll(
                intent_id, direction, amount, approval_id, context
            )

        elif action_name == "double_click":
            x = parameters.get("x")
            y = parameters.get("y")
            if x is None or y is None:
                return ExecutionOutcome(
                    status=ExecutionStatus.FAILED,
                    start_time=0,
                    end_time=0,
                    duration_ms=0,
                    error_message="Missing required parameters: x, y",
                )
            return self.mouse.execute_double_click(intent_id, x, y, approval_id, context)

        else:
            return ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=0,
                end_time=0,
                duration_ms=0,
                error_message=f"Unknown mouse action: {action_name}",
            )

    @staticmethod
    def _validate_pipeline(pipeline: Dict[str, Any]) -> bool:
        """Validate that pipeline is properly structured and approved.

        Args:
            pipeline: Pipeline dict to validate

        Returns:
            True if valid and approved, False otherwise
        """
        # Check structure
        if not isinstance(pipeline, dict):
            return False

        if "intent" not in pipeline:
            return False

        if "approval_result" not in pipeline:
            return False

        # Check approval status
        approval_result = pipeline.get("approval_result", {})
        if approval_result.get("decision") != "approved":
            return False

        # Check intent structure
        intent = pipeline.get("intent", {})
        if "intent_id" not in intent:
            return False

        if "action_name" not in intent:
            return False

        # All checks passed
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics.

        Returns:
            Dict with execution stats
        """
        return self.tracker.get_statistics()

    def get_execution_history(
        self, intent_id: Optional[str] = None, limit: Optional[int] = None
    ) -> list:
        """Get execution history.

        Args:
            intent_id: Filter by intent (optional)
            limit: Limit number of records

        Returns:
            List of execution records
        """
        return self.tracker.get_execution_history(intent_id, limit)

    def enable(self) -> None:
        """Enable action execution."""
        self.enabled = True
        self.tracker.enable()
        self.keyboard.enable()
        self.mouse.enable()

    def disable(self) -> None:
        """Disable action execution (reversible disable flag)."""
        self.enabled = False
        self.tracker.disable()
        self.keyboard.disable()
        self.mouse.disable()
