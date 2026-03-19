from typing import List


class StrategicDirectionPersistence:

    def __init__(self):
        self._last_priorities: List[str] = []

    def persist_priorities(self, priorities: List[str]) -> None:
        """
        Stores latest strategic priority ordering.
        """
        self._last_priorities = list(priorities)

    def get_last_priorities(self) -> List[str]:
        """
        Returns previously persisted priorities.
        """
        return list(self._last_priorities)
