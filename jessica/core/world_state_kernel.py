from __future__ import annotations

import time
from typing import Any


class WorldStateKernel:
    """
    Central aggregator for Jessica's runtime world/system state.

    Updated at the beginning and end of each cognitive cycle.
    """

    def __init__(self) -> None:
        self.cycle_state: dict[str, Any] = {}
        self.history: list[dict[str, Any]] = []

    def restore(self, cycle_state: Any, history: Any) -> None:
        """Restore in-memory world state from a persisted checkpoint payload."""
        if isinstance(cycle_state, dict):
            self.cycle_state = dict(cycle_state)
        else:
            self.cycle_state = {}

        if isinstance(history, list):
            restored: list[dict[str, Any]] = []
            for item in history:
                if isinstance(item, dict):
                    restored.append(dict(item))
            self.history = restored
        else:
            self.history = []

    def begin_cycle(self, cycle: int, goal: str | None = None) -> None:
        """Called at the start of every cycle."""
        self.cycle_state = {
            "cycle": cycle,
            "goal": goal,
            "start_time": time.time(),
            "events": [],
        }

    def record_event(self, name: str, payload: Any | None = None) -> None:
        """Record an event during the cycle."""
        self.cycle_state.setdefault("events", []).append(
            {
                "event": name,
                "payload": payload,
                "timestamp": time.time(),
            }
        )

    def end_cycle(self, status: str = "completed") -> None:
        """Finalize the cycle state."""
        if not self.cycle_state:
            self.cycle_state = {
                "cycle": -1,
                "goal": None,
                "start_time": time.time(),
                "events": [],
            }

        self.cycle_state["status"] = status
        self.cycle_state["end_time"] = time.time()
        start_time = self.cycle_state.get("start_time")
        if isinstance(start_time, (int, float)):
            start_value = float(start_time)
        else:
            start_value = float(self.cycle_state["end_time"])

        self.cycle_state["duration"] = (
            float(self.cycle_state["end_time"]) - start_value
        )

        self.history.append(self.cycle_state)

    def get_current_state(self) -> dict[str, Any]:
        return self.cycle_state

    def get_history(self, limit: int | None = None) -> list[dict[str, Any]]:
        if limit is None or limit <= 0:
            return self.history
        return self.history[-limit:]
