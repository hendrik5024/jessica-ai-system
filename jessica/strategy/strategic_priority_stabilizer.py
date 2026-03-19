from typing import Dict, List


class StrategicPriorityStabilizer:

    def stabilize_priorities(self, weights: Dict[str, int]) -> List[str]:
        """
        Produces stable priority ordering based on reinforcement weights.
        """

        sorted_priorities = sorted(
            weights.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [p[0] for p in sorted_priorities]
