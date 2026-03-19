from .consistency_monitor_engine import ConsistencyMonitorEngine
from .consistency_monitor_record import ConsistencyMonitorRecord


class ConsistencyMonitorOrchestrator:

    def __init__(self):
        self.engine = ConsistencyMonitorEngine()

    def monitor(
        self,
        monitor_id: str,
        qualities: list[float],
    ) -> ConsistencyMonitorRecord:

        return self.engine.evaluate(monitor_id, qualities)
