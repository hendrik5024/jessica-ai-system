from typing import Dict, List


class StrategicPatternReinforcer:

    def reinforce_patterns(self, signals: List[str]) -> Dict[str, int]:
        """
        Assigns reinforcement weight to strategic signals.
        """

        weights = {}

        for signal in signals:
            weights[signal] = weights.get(signal, 0) + 1

        return weights
