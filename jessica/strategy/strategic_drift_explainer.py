from typing import List, Optional

from .strategic_coherence_record import StrategicCoherenceRecord


class StrategicDriftExplainer:

    def explain(self, history: List[StrategicCoherenceRecord]) -> Optional[str]:

        if len(history) < 2:
            return None

        base = history[0]

        for rec in history[1:]:
            if rec.strategic_direction != base.strategic_direction:
                return (
                    f"Strategic drift detected: direction changed from "
                    f"'{base.strategic_direction}' to '{rec.strategic_direction}' "
                    f"between checkpoints {base.cycle_id} and {rec.cycle_id}."
                )

        return None
