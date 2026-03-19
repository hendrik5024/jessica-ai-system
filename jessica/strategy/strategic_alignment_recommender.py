from typing import List, Optional

from .strategic_coherence_record import StrategicCoherenceRecord


class StrategicAlignmentRecommender:

    def recommend(self, history: List[StrategicCoherenceRecord]) -> Optional[str]:

        if len(history) < 2:
            return None

        base = history[0]

        for rec in history[1:]:
            if rec.strategic_direction != base.strategic_direction:
                return (
                    f"Recommendation: review alignment to restore the original "
                    f"strategic direction '{base.strategic_direction}', "
                    f"as divergence was observed at checkpoint {rec.cycle_id}."
                )

        return None
