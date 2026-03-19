from jessica.cognition.telemetry import queue_insight


class InsightManager:

    def add_insight(self, insight):
        return queue_insight(insight)