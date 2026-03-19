from typing import List


class StrategicMemoryConsolidator:

    def consolidate_patterns(self, detected_patterns: List[str]) -> List[str]:
        """
        Converts repeated patterns into consolidation signals.
        """

        consolidated = []

        for pattern in detected_patterns:
            consolidated.append(f"Strategic memory signal: {pattern}")

        return consolidated
