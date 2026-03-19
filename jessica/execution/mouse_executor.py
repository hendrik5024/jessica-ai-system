"""Mouse action executor for Phase 5.2 - minimal embodiment.

Executes mouse actions ONLY through approved Phase 5.1.5 intent pipelines.

- Single mouse action per execution (move, click, scroll)
- No dragging chains or multi-step operations
- Full audit trail
- Immediate return
- Reversible if possible
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    import mouse
    HAS_MOUSE = True
except ImportError:
    HAS_MOUSE = False

from jessica.execution.execution_tracker import ExecutionOutcome, ExecutionStatus


class MouseExecutor:
    """Executes mouse input actions with full approval gate integration."""

    def __init__(self, enabled: bool = True, tracker: Optional[Any] = None):
        """Initialize mouse executor.

        Args:
            enabled: Whether mouse execution is enabled (reversible disable flag)
            tracker: ExecutionTracker instance for audit trail
        """
        self.enabled = enabled
        self.tracker = tracker
        self.has_pyautogui = HAS_PYAUTOGUI
        self.has_mouse = HAS_MOUSE

        if not (self.has_pyautogui or self.has_mouse):
            print(
                "[MouseExecutor] WARNING: Neither 'pyautogui' nor 'mouse' library available. "
                "Install with: pip install pyautogui  OR  pip install mouse"
            )

    def execute_click(
        self,
        intent_id: str,
        x: int,
        y: int,
        button: str = "left",
        approval_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionOutcome:
        """Execute a single mouse click (atomic action).

        Args:
            intent_id: ID of intent authorizing this action
            x: X coordinate
            y: Y coordinate
            button: Mouse button ("left", "right", "middle")
            approval_id: ID of approval that authorized this
            context: Context info (target ui element, window, etc.)

        Returns:
            ExecutionOutcome with status and details
        """
        if not self.enabled:
            return ExecutionOutcome(
                status=ExecutionStatus.CANCELLED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error_message="MouseExecutor is disabled",
            )

        start_time = time.time()

        try:
            # Validate coordinates
            if x < 0 or y < 0:
                raise ValueError(f"Invalid coordinates: x={x}, y={y}")

            # Execute the click
            if self.has_pyautogui:
                pyautogui.click(x, y, button=button)
            elif self.has_mouse:
                mouse.move(x, y)
                mouse.click(button=button)
            else:
                raise RuntimeError("No mouse library available")

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                notes=f"Clicked {button} button at ({x}, {y})",
            )

            # Record in audit trail
            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="mouse_click",
                    action_params={"x": x, "y": y, "button": button},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=True,
                    undo_instructions=f"Click at ({x}, {y}) again with same button to potentially undo",
                    context=context or {},
                    metadata={"executor": "mouse", "button": button, "coords": (x, y)},
                )

            return outcome

        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                error_message=str(e),
                error_type=type(e).__name__,
            )

            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="mouse_click",
                    action_params={"x": x, "y": y, "button": button},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=False,
                    context=context or {},
                    metadata={"executor": "mouse", "error": str(e)},
                )

            return outcome

    def execute_move(
        self,
        intent_id: str,
        x: int,
        y: int,
        approval_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionOutcome:
        """Move mouse to position (atomic action).

        Args:
            intent_id: ID of intent authorizing this action
            x: Target X coordinate
            y: Target Y coordinate
            approval_id: ID of approval that authorized this
            context: Context info

        Returns:
            ExecutionOutcome with status and details
        """
        if not self.enabled:
            return ExecutionOutcome(
                status=ExecutionStatus.CANCELLED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error_message="MouseExecutor is disabled",
            )

        start_time = time.time()

        try:
            # Validate coordinates
            if x < 0 or y < 0:
                raise ValueError(f"Invalid coordinates: x={x}, y={y}")

            if self.has_pyautogui:
                pyautogui.moveTo(x, y)
            elif self.has_mouse:
                mouse.move(x, y)
            else:
                raise RuntimeError("No mouse library available")

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                notes=f"Moved mouse to ({x}, {y})",
            )

            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="mouse_move",
                    action_params={"x": x, "y": y},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=True,
                    undo_instructions="Move mouse back to previous position",
                    context=context or {},
                    metadata={"executor": "mouse", "coords": (x, y)},
                )

            return outcome

        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                error_message=str(e),
                error_type=type(e).__name__,
            )

            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="mouse_move",
                    action_params={"x": x, "y": y},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=False,
                    context=context or {},
                    metadata={"executor": "mouse", "error": str(e)},
                )

            return outcome

    def execute_scroll(
        self,
        intent_id: str,
        direction: str = "down",
        amount: int = 3,
        approval_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionOutcome:
        """Execute mouse scroll (atomic action).

        Args:
            intent_id: ID of intent authorizing this action
            direction: Scroll direction ("up" or "down")
            amount: Number of scroll clicks
            approval_id: ID of approval that authorized this
            context: Context info

        Returns:
            ExecutionOutcome with status and details
        """
        if not self.enabled:
            return ExecutionOutcome(
                status=ExecutionStatus.CANCELLED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error_message="MouseExecutor is disabled",
            )

        start_time = time.time()

        try:
            # Validate inputs
            if direction not in ("up", "down"):
                raise ValueError(f"Invalid scroll direction: {direction}")

            if amount < 1:
                raise ValueError(f"Invalid scroll amount: {amount}")

            # Convert to scroll amount for libraries (negative for up)
            scroll_amount = amount if direction == "down" else -amount

            if self.has_pyautogui:
                pyautogui.scroll(scroll_amount)
            elif self.has_mouse:
                mouse.wheel(scroll_amount)
            else:
                raise RuntimeError("No mouse library available")

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                notes=f"Scrolled {direction} {amount} clicks",
            )

            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="mouse_scroll",
                    action_params={"direction": direction, "amount": amount},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=True,
                    undo_instructions=f"Scroll {('up' if direction == 'down' else 'down')} {amount} times to undo",
                    context=context or {},
                    metadata={"executor": "mouse", "direction": direction, "amount": amount},
                )

            return outcome

        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                error_message=str(e),
                error_type=type(e).__name__,
            )

            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="mouse_scroll",
                    action_params={"direction": direction, "amount": amount},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=False,
                    context=context or {},
                    metadata={"executor": "mouse", "error": str(e)},
                )

            return outcome

    def execute_double_click(
        self,
        intent_id: str,
        x: int,
        y: int,
        approval_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionOutcome:
        """Execute double-click (atomic action).

        Args:
            intent_id: ID of intent authorizing this action
            x: X coordinate
            y: Y coordinate
            approval_id: ID of approval that authorized this
            context: Context info

        Returns:
            ExecutionOutcome with status and details
        """
        if not self.enabled:
            return ExecutionOutcome(
                status=ExecutionStatus.CANCELLED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error_message="MouseExecutor is disabled",
            )

        start_time = time.time()

        try:
            if x < 0 or y < 0:
                raise ValueError(f"Invalid coordinates: x={x}, y={y}")

            if self.has_pyautogui:
                pyautogui.click(x, y, clicks=2)
            elif self.has_mouse:
                mouse.move(x, y)
                mouse.double_click()
            else:
                raise RuntimeError("No mouse library available")

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                notes=f"Double-clicked at ({x}, {y})",
            )

            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="mouse_double_click",
                    action_params={"x": x, "y": y},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=True,
                    undo_instructions=f"Double-click at ({x}, {y}) again to potentially undo",
                    context=context or {},
                    metadata={"executor": "mouse", "coords": (x, y)},
                )

            return outcome

        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                error_message=str(e),
                error_type=type(e).__name__,
            )

            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="mouse_double_click",
                    action_params={"x": x, "y": y},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=False,
                    context=context or {},
                    metadata={"executor": "mouse", "error": str(e)},
                )

            return outcome

    def enable(self) -> None:
        """Enable mouse execution."""
        self.enabled = True

    def disable(self) -> None:
        """Disable mouse execution (reversible disable flag)."""
        self.enabled = False
