"""
Phase 84.5 — Concept Registry

Stores symbolic facts and relationships.

NO LEARNING
NO AUTONOMY
DETERMINISTIC
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Fact:
    subject: str
    relation: str
    object: str


class ConceptRegistry:
    """
    Stores facts in memory.
    """

    def __init__(self):
        self._facts: List[Fact] = []

    def add_fact(self, subject: str, relation: str, obj: str):
        fact = Fact(subject.lower(), relation.lower(), obj.lower())
        if fact not in self._facts:
            self._facts.append(fact)

    def get_facts(self) -> List[Fact]:
        return list(self._facts)

    def find(self, subject: str = None, relation: str = None, obj: str = None) -> List[Fact]:
        results = []

        for f in self._facts:
            if subject and f.subject != subject.lower():
                continue
            if relation and f.relation != relation.lower():
                continue
            if obj and f.object != obj.lower():
                continue
            results.append(f)

        return results
