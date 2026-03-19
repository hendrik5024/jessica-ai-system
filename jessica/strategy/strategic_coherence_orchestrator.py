from .strategic_coherence_registry import StrategicCoherenceRegistry
from .strategic_coherence_record import StrategicCoherenceRecord


class StrategicCoherenceOrchestrator:

    def __init__(self):
        self.registry = StrategicCoherenceRegistry()

    def record_direction(self, cycle_id: str, strategic_direction: str):
        rec = StrategicCoherenceRecord(cycle_id, strategic_direction)
        self.registry.add(rec)
        return rec

    def get_history(self):
        return self.registry.history()
