"""
Phase 84.5 — Inference Engine

Applies reasoning rules to facts.

NO LEARNING
DETERMINISTIC
"""

from typing import List
from .concept_registry import Fact


class InferenceEngine:
    """
    Applies logical rules to facts.
    """

    def infer(self, facts: List[Fact]) -> List[Fact]:
        new_facts = []

        for f in facts:
            # Rule 1: creator inference
            if f.relation == "created":
                new_facts.append(Fact(f.subject, "is_creator_of", f.object))

            # Rule 2: reverse creator
            if f.relation == "created":
                new_facts.append(Fact(f.object, "created_by", f.subject))

        return new_facts
