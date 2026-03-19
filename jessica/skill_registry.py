"""Phase 16 — Skill Acquisition Planning Layer: skill registry."""

from __future__ import annotations

from typing import Dict, List

from jessica.skill_definition import SkillDefinition


class SkillRegistry:
    def __init__(self) -> None:
        self._known: Dict[str, SkillDefinition] = {}
        self._proposed: Dict[str, SkillDefinition] = {}
        self._known_order: List[str] = []
        self._proposed_order: List[str] = []

    def register_skill(self, skill_definition: SkillDefinition, proposed: bool = False) -> None:
        target = self._proposed if proposed else self._known
        order = self._proposed_order if proposed else self._known_order
        if skill_definition.skill_id in target:
            raise ValueError("Skill already registered")
        target[skill_definition.skill_id] = skill_definition
        order.append(skill_definition.skill_id)

    def get_skill(self, skill_id: str) -> SkillDefinition | None:
        return self._known.get(skill_id) or self._proposed.get(skill_id)

    def list_known_skills(self) -> List[SkillDefinition]:
        return [self._known[sid] for sid in self._known_order]

    def list_proposed_skills(self) -> List[SkillDefinition]:
        return [self._proposed[sid] for sid in self._proposed_order]
