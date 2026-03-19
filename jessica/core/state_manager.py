import json
import os
from typing import Any


class CognitiveStateManager:

    def __init__(self, path: str = "jessica/state.json") -> None:
        self.path = path

        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

        if not os.path.exists(self.path):
            self.save_state({
                "cycle": 0,
                "goals": [],
                "task_queue": [],
                "task_history": {},
                "last_telemetry": None,
                "world_state_current": {},
                "world_state_history": [],
                "observation_snapshot": None,
            })

    def load_state(self) -> dict[str, Any]:

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_state(self, state: dict[str, Any]) -> None:

        tmp_path = f"{self.path}.tmp"

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        # Atomic replace keeps the checkpoint valid even on abrupt interruption.
        os.replace(tmp_path, self.path)
