from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional


class PersonalityInertia:
    """Cross-session personality drift control.

    Changes to the personality state require repeated confirmations
    before being accepted. This prevents sudden or chaotic shifts.
    """

    def __init__(self, state_path: str | None = None, threshold: int = 3) -> None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(os.path.dirname(base_dir), "data", "personality_inertia.json")
        self.state_path = state_path or default_path
        self.threshold = max(2, int(threshold))
        self.state: Dict[str, Any] = {
            "version": 1,
            "last_confirmed_state": None,
            "pending": None,
            "history": [],
            "threshold": self.threshold,
        }
        self._load()

    def stabilize_state(self, current_state: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Return a stabilized personality state.

        If a change is detected, it must be observed multiple times
        (across sessions or repeated reads) before being accepted.
        """
        if not current_state:
            return current_state

        if not self.state.get("last_confirmed_state"):
            self.state["last_confirmed_state"] = self._clone_state(current_state)
            self._save()
            return current_state

        confirmed = self.state.get("last_confirmed_state")
        if self._hash_state(current_state) == self._hash_state(confirmed):
            self.state["pending"] = None
            self._save()
            return current_state

        pending = self.state.get("pending")
        current_hash = self._hash_state(current_state)

        if pending and pending.get("hash") == current_hash:
            pending["count"] = int(pending.get("count", 1)) + 1
            if pending["count"] >= self.threshold:
                self._accept_change(current_state)
                return current_state
            self.state["pending"] = pending
            self._save()
            return self._clone_state(confirmed)

        # New change proposal
        self.state["pending"] = {
            "hash": current_hash,
            "count": 1,
            "proposed_state": self._clone_state(current_state),
            "first_seen": int(time.time()),
        }
        self._save()
        return self._clone_state(confirmed)

    def get_status(self) -> Dict[str, Any]:
        pending = self.state.get("pending") or {}
        return {
            "version": self.state.get("version", 1),
            "threshold": self.state.get("threshold", self.threshold),
            "pending_count": pending.get("count", 0),
            "pending_since": pending.get("first_seen"),
            "has_pending": bool(pending),
        }

    # -------------------------------------------------
    # Internals
    # -------------------------------------------------
    def _accept_change(self, new_state: Dict[str, List[str]]) -> None:
        self.state["last_confirmed_state"] = self._clone_state(new_state)
        self.state["pending"] = None
        self.state["version"] = int(self.state.get("version", 1)) + 1
        self.state.setdefault("history", []).append(
            {
                "ts": int(time.time()),
                "version": self.state["version"],
                "summary": self._summarize_change(new_state),
            }
        )
        self._save()

    def _summarize_change(self, state: Dict[str, List[str]]) -> str:
        counts = {k: len(v) for k, v in state.items()}
        return f"beliefs={counts.get('beliefs', 0)}, desires={counts.get('desires', 0)}, intentions={counts.get('intentions', 0)}"

    def _hash_state(self, state: Dict[str, List[str]]) -> str:
        payload = json.dumps(state, sort_keys=True)
        return str(hash(payload))

    def _clone_state(self, state: Dict[str, List[str]]) -> Dict[str, List[str]]:
        return {
            "beliefs": list(state.get("beliefs", [])),
            "desires": list(state.get("desires", [])),
            "intentions": list(state.get("intentions", [])),
        }

    def _load(self) -> None:
        try:
            if os.path.isfile(self.state_path):
                with open(self.state_path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
        except Exception:
            pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            self.state["threshold"] = self.threshold
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except Exception:
            pass
