"""
Phase 76 — World State

Persistent disk-backed world model.

Responsibilities:
- Load belief graph from disk
- Save belief graph to disk
- Provide structured access layer
- Never mutate implicitly
"""

import json
from pathlib import Path
from typing import Optional

from .belief_graph import BeliefGraph


DEFAULT_WORLD_FILE = Path("jessica_world_state.json")


class WorldState:
    """
    Persistent world state container.
    """

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or DEFAULT_WORLD_FILE
        self.belief_graph = BeliefGraph()

        self._load()

    # ---------- Persistence ----------

    def _load(self) -> None:
        if not self.file_path.exists():
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "belief_graph" in data:
                self.belief_graph = BeliefGraph.from_dict(data["belief_graph"])

        except Exception:
            # Fail safe — never crash boot
            self.belief_graph = BeliefGraph()

    def save(self) -> None:
        data = {
            "belief_graph": self.belief_graph.to_dict(),
        }

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ---------- Belief API ----------

    def set_fact(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 1.0,
    ) -> None:
        self.belief_graph.add_or_update_belief(
            subject,
            predicate,
            obj,
            confidence,
        )
        self.save()

    def get_fact(self, subject: str, predicate: str):
        belief = self.belief_graph.get_belief(subject, predicate)
        return belief.obj if belief else None

    def all_facts(self):
        return self.belief_graph.all_beliefs()
