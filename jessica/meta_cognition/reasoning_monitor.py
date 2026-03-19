from dataclasses import dataclass
from statistics import mean
from time import time
from typing import List


@dataclass(frozen=True)
class ReasoningRecord:
    record_id: str
    reasoning_id: str
    confidence_score: float
    step_count: int
    timestamp: float


@dataclass(frozen=True)
class ReasoningMetrics:
    total_reasonings: int
    average_confidence: float
    reasoning_depth_index: float


class ReasoningQualityMonitor:

    def __init__(self):
        self._records: List[ReasoningRecord] = []

    def record_reasoning(self, reasoning_trace) -> ReasoningRecord:
        record = ReasoningRecord(
            record_id=f"record-{reasoning_trace.reasoning_id}-{len(self._records) + 1}",
            reasoning_id=reasoning_trace.reasoning_id,
            confidence_score=reasoning_trace.final_confidence,
            step_count=len(reasoning_trace.steps),
            timestamp=time(),
        )
        self._records.append(record)
        return record

    def compute_metrics(self) -> ReasoningMetrics:
        if not self._records:
            return ReasoningMetrics(
                total_reasonings=0,
                average_confidence=0.0,
                reasoning_depth_index=0.0,
            )

        confidences = [record.confidence_score for record in self._records]
        depths = [record.step_count for record in self._records]

        return ReasoningMetrics(
            total_reasonings=len(self._records),
            average_confidence=mean(confidences),
            reasoning_depth_index=mean(depths),
        )

    def history(self) -> List[ReasoningRecord]:
        return list(self._records)
