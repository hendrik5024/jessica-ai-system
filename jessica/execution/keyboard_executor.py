"""Keyboard action executor for Phase 5.2 - minimal embodiment.

Executes keyboard actions ONLY through approved Phase 5.1.5 intent pipelines.

- Single keypress or key sequence per execution
- No chaining or automation
- Full audit trail
- Immediate return (no blocking)
- Reversible if possible (recording for manual undo)
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

from jessica.execution.execution_tracker import ExecutionOutcome, ExecutionStatus


class KeyboardExecutor:
    """Executes keyboard input actions with full approval gate integration."""

    def __init__(self, enabled: bool = True, tracker: Optional[Any] = None):
        """Initialize keyboard executor.

        Args:
            enabled: Whether keyboard execution is enabled (reversible disable flag)
            tracker: ExecutionTracker instance for audit trail
        """
        self.enabled = enabled
        self.tracker = tracker
        self.has_keyboard_lib = HAS_KEYBOARD
        self.has_pyautogui = HAS_PYAUTOGUI

        if not (self.has_keyboard_lib or self.has_pyautogui):
            print(
                "[KeyboardExecutor] WARNING: Neither 'keyboard' nor 'pyautogui' library available. "
                "Install with: pip install keyboard  OR  pip install pyautogui"
            )

    def execute_key(
        self,
        intent_id: str,
        key: str,
        approval_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionOutcome:
        """Execute a single keypress (atomic action).

        Args:
            intent_id: ID of intent authorizing this action
            key: Key name (e.g., "a", "return", "ctrl+c")
            approval_id: ID of approval that authorized this
            context: Context info (target app, ui state, etc.)

        Returns:
            ExecutionOutcome with status and details
        """
        if not self.enabled:
            return ExecutionOutcome(
                status=ExecutionStatus.CANCELLED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error_message="KeyboardExecutor is disabled",
            )

        start_time = time.time()

        try:
            # Normalize key name
            key_normalized = self._normalize_key(key)

            # Execute the keypress
            if self.has_keyboard_lib:
                keyboard.press_and_release(key_normalized)
            elif self.has_pyautogui:
                pyautogui.press(key_normalized)
            else:
                raise RuntimeError("No keyboard library available")

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                notes=f"Pressed key: {key_normalized}",
            )

            # Record in audit trail
            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="keyboard_single",
                    action_params={"key": key},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=True,
                    undo_instructions=f"Press '{key_normalized}' again to undo if applicable",
                    context=context or {},
                    metadata={"executor": "keyboard", "key_normalized": key_normalized},
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

            # Record failure in audit trail
            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="keyboard_single",
                    action_params={"key": key},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=False,
                    context=context or {},
                    metadata={"executor": "keyboard", "error": str(e)},
                )

            return outcome

    def execute_type(
        self,
        intent_id: str,
        text: str,
        approval_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        interval: float = 0.05,
    ) -> ExecutionOutcome:
        """Type text (atomic action).

        Args:
            intent_id: ID of intent authorizing this action
            text: Text to type
            approval_id: ID of approval that authorized this
            context: Context info
            interval: Delay between keystrokes (seconds)

        Returns:
            ExecutionOutcome with status and details
        """
        if not self.enabled:
            return ExecutionOutcome(
                status=ExecutionStatus.CANCELLED,
                start_time=time.time(),
                end_time=time.time(),
                duration_ms=0,
                error_message="KeyboardExecutor is disabled",
            )

        start_time = time.time()

        try:
            if self.has_pyautogui:
                pyautogui.write(text, interval=interval)
            elif self.has_keyboard_lib:
                keyboard.write(text)
            else:
                raise RuntimeError("No keyboard library available")

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                notes=f"Typed {len(text)} characters",
            )

            # Record in audit trail
            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="keyboard_type",
                    action_params={"text": text, "length": len(text)},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=True,
                    undo_instructions=f"Select all text (Ctrl+A) and delete to undo",
                    context=context or {},
                    metadata={"executor": "keyboard", "char_count": len(text)},
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
                    action_type="keyboard_type",
                    action_params={"text": text, "length": len(text)},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=False,
                    context=context or {},
                    metadata={"executor": "keyboard", "error": str(e)},
                )

            return outcome

    def execute_hotkey(
        self,
        intent_id: str,
        keys: list,
        approval_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionOutcome:
        """Execute hotkey combination (e.g., Ctrl+C, Alt+Tab).

        Args:
            intent_id: ID of intent authorizing this action
            keys: List of keys to press together (e.g., ["ctrl", "c"])
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
                error_message="KeyboardExecutor is disabled",
            )

        start_time = time.time()

        try:
            # Normalize key names
            keys_normalized = [self._normalize_key(k) for k in keys]

            if self.has_pyautogui:
                pyautogui.hotkey(*keys_normalized)
            elif self.has_keyboard_lib:
                keyboard.press_and_release("+".join(keys_normalized))
            else:
                raise RuntimeError("No keyboard library available")

            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            hotkey_str = "+".join(keys)

            outcome = ExecutionOutcome(
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                notes=f"Pressed hotkey: {hotkey_str}",
            )

            if self.tracker:
                self.tracker.record_execution(
                    intent_id=intent_id,
                    action_type="keyboard_hotkey",
                    action_params={"keys": keys},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=True,
                    undo_instructions=f"Press '{hotkey_str}' again to undo if applicable",
                    context=context or {},
                    metadata={"executor": "keyboard", "keys": keys_normalized},
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
                    action_type="keyboard_hotkey",
                    action_params={"keys": keys},
                    approval_id=approval_id,
                    outcome=outcome,
                    reversible=False,
                    context=context or {},
                    metadata={"executor": "keyboard", "error": str(e)},
                )

            return outcome

    @staticmethod
    def _normalize_key(key: str) -> str:
        """Normalize key name for library compatibility.

        Args:
            key: Key name (e.g., "return", "enter", "ctrl", "control")

        Returns:
            Normalized key name
        """
        # Map common key name variations
        mapping = {
            "enter": "return",
            "control": "ctrl",
            "command": "cmd",
            "option": "alt",
            "windows": "win",
            "meta": "win",
        }

        normalized = key.lower().strip()
        return mapping.get(normalized, normalized)

    def enable(self) -> None:
        """Enable keyboard execution."""
        self.enabled = True

    def disable(self) -> None:
        """Disable keyboard execution (reversible disable flag)."""
        self.enabled = False
