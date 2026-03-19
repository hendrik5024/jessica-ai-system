"""Phase 16 — Skill Acquisition Planning Layer: skill planner."""

from __future__ import annotations

from typing import Dict, List
from datetime import datetime

from jessica.skill_definition import SkillDefinition


class SkillPlanner:
    """Deterministic skill planning engine (advisory only)."""

    def generate_skill_plan(self, capability_gap: str) -> Dict:
        plan_id = f"plan_{capability_gap.replace(' ', '_')}"
        return {
            "plan_id": plan_id,
            "capability_gap": capability_gap,
            "steps": [
                f"define scope for {capability_gap}",
                f"research prerequisites for {capability_gap}",
                f"practice {capability_gap} in controlled examples",
                f"validate {capability_gap} with tests",
            ],
            "created_at": datetime(2026, 2, 9, 12, 0, 0),
        }

    def estimate_learning_steps(self, skill: SkillDefinition) -> List[str]:
        return [
            f"review prerequisites: {', '.join(skill.prerequisites) or 'none'}",
            f"study {skill.name} fundamentals",
            f"apply {skill.name} in small tasks",
            "validate with tests",
        ]

    def generate_learning_sequence(self, skill: SkillDefinition) -> List[str]:
        return self.estimate_learning_steps(skill)
