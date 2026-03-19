from .consistency_record import ConsistencyRecord


class ReasoningConsistencyValidator:

    def validate(self, reasoning_id: str, reasoning_steps: list[str]) -> ConsistencyRecord:
        contradictions = []

        seen = set()

        for step in reasoning_steps:
            if step in seen:
                continue
            if f"not {step}" in reasoning_steps:
                contradictions.append(f"Contradiction detected: {step}")

            seen.add(step)

        return ConsistencyRecord(
            reasoning_id=reasoning_id,
            contradictions_found=len(contradictions) > 0,
            contradiction_descriptions=contradictions,
            confidence_score=1.0 if not contradictions else 0.5,
        )
