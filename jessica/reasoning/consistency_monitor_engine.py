from .consistency_monitor_record import ConsistencyMonitorRecord


class ConsistencyMonitorEngine:

    def evaluate(
        self,
        monitor_id: str,
        qualities: list[float],
    ) -> ConsistencyMonitorRecord:

        if not qualities:
            return ConsistencyMonitorRecord(
                monitor_id,
                0,
                1.0,
                False,
                False,
                "No prior records",
            )

        avg = sum(qualities) / len(qualities)

        drift = max(qualities) - min(qualities) > 0.25
        contradiction = avg < 0.5

        return ConsistencyMonitorRecord(
            monitor_id,
            len(qualities),
            avg,
            contradiction,
            drift,
            "Consistency evaluated deterministically",
        )
