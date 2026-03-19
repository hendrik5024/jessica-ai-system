from dataclasses import dataclass
from statistics import mean
from time import time
from typing import List

from .reasoning_monitor import ReasoningRecord


@dataclass(frozen=True)
class ReasoningDriftReport:
    drift_detected: bool
    confidence_trend: float
    depth_trend: float
    records_analyzed: int
    timestamp: float


class ReasoningDriftDetector:

    def __init__(self, window_size: int = 20):
        self._window_size = window_size

    def detect_drift(self, records: List[ReasoningRecord]) -> ReasoningDriftReport:
        window = records[-self._window_size :]
        if len(window) < 2:
            return ReasoningDriftReport(
                drift_detected=False,
                confidence_trend=0.0,
                depth_trend=0.0,
                records_analyzed=len(window),
                timestamp=time(),
            )

        mid = len(window) // 2
        earlier = window[:mid]
        later = window[mid:]

        earlier_conf = mean(record.confidence_score for record in earlier)
        later_conf = mean(record.confidence_score for record in later)
        confidence_trend = later_conf - earlier_conf

        earlier_depth = mean(record.step_count for record in earlier)
        later_depth = mean(record.step_count for record in later)
        depth_trend = later_depth - earlier_depth

        drift_detected = confidence_trend < -0.05 or depth_trend < -0.05

        return ReasoningDriftReport(
            drift_detected=drift_detected,
            confidence_trend=confidence_trend,
            depth_trend=depth_trend,
            records_analyzed=len(window),
            timestamp=time(),
        )
