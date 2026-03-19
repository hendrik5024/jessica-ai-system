"""Phase 16 — Skill Acquisition Planning Layer: capability gap analyzer."""

from __future__ import annotations

from typing import Dict, List


class CapabilityGapAnalyzer:
    """Deterministic analyzer for capability gaps."""

    def analyze_task_failure(self, task_metadata: Dict) -> List[str]:
        return self.detect_missing_capabilities(task_metadata)

    def detect_missing_capabilities(self, task_metadata: Dict) -> List[str]:
        caps = task_metadata.get("missing_capabilities", []) if task_metadata else []
        return list(caps)

    def rank_capability_gaps(self, gap_list: List[str]) -> List[str]:
        return sorted(gap_list)
