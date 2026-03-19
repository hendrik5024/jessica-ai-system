from typing import List

from .strategic_coherence_record import StrategicCoherenceRecord


class StrategicDriftDetector:

    def detect(self, history: List[StrategicCoherenceRecord]):

        if len(history) < 2:
            return False

        base_direction = history[0].strategic_direction

        for rec in history[1:]:
            if rec.strategic_direction != base_direction:
                return True

        return False
