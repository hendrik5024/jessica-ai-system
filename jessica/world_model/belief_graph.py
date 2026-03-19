"""
Phase 76 — Belief Graph

Persistent structured belief system.

Represents Jessica's internal understanding of:
- Entities
- Facts
- Relationships
- Confidence levels

STRICT CONSTRAINTS:
- Deterministic
- No learning heuristics
- Explicit updates only
- Serializable
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple
from datetime import datetime


@dataclass
class Belief:
    subject: str
    predicate: str
    obj: str
    confidence: float
    updated_at: datetime


class BeliefGraph:
    """
    Directed belief graph.
    """

    def __init__(self):
        # (subject, predicate) -> Belief
        self._beliefs: Dict[Tuple[str, str], Belief] = {}

    # ---------- Core Operations ----------

    def add_or_update_belief(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 1.0,
    ) -> None:
        key = (subject, predicate)

        self._beliefs[key] = Belief(
            subject=subject,
            predicate=predicate,
            obj=obj,
            confidence=confidence,
            updated_at=datetime.utcnow(),
        )

    def get_belief(self, subject: str, predicate: str) -> Belief | None:
        return self._beliefs.get((subject, predicate))

    def all_beliefs(self) -> Dict[Tuple[str, str], Belief]:
        return dict(self._beliefs)

    # ---------- Serialization ----------

    def to_dict(self) -> dict:
        return {
            f"{k[0]}::{k[1]}": {
                "subject": v.subject,
                "predicate": v.predicate,
                "object": v.obj,
                "confidence": v.confidence,
                "updated_at": v.updated_at.isoformat(),
            }
            for k, v in self._beliefs.items()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BeliefGraph":
        graph = cls()

        for key, value in data.items():
            subject, predicate = key.split("::")

            graph._beliefs[(subject, predicate)] = Belief(
                subject=subject,
                predicate=predicate,
                obj=value["object"],
                confidence=value["confidence"],
                updated_at=datetime.fromisoformat(value["updated_at"]),
            )

        return graph
