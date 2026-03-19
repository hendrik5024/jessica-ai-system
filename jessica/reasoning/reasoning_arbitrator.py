from .arbitration_record import ArbitrationRecord


class ReasoningArbitrator:

    def arbitrate(
        self,
        arbitration_id: str,
        candidate_answers: list[str],
        alignment_score: float,
        confidence_scores: list[float],
    ) -> ArbitrationRecord:

        if not candidate_answers:
            raise ValueError("No candidate answers provided")

        best_index = 0
        best_score = confidence_scores[0]

        for i, score in enumerate(confidence_scores):
            if score > best_score:
                best_index = i
                best_score = score

        selected = candidate_answers[best_index]

        return ArbitrationRecord(
            arbitration_id=arbitration_id,
            selected_answer=selected,
            competing_answers=len(candidate_answers),
            alignment_score=alignment_score,
            confidence_score=best_score,
            arbitration_reason="Highest confidence selected deterministically",
        )
