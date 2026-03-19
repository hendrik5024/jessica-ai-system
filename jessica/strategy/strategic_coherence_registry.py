from typing import List

from .strategic_coherence_record import StrategicCoherenceRecord


class StrategicCoherenceRegistry:

    def __init__(self):
        self.records: List[StrategicCoherenceRecord] = []

    def add(self, record: StrategicCoherenceRecord):
        self.records.append(record)

    def history(self):
        return list(self.records)
