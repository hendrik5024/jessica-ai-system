from .alignment_record import AlignmentRecord


class MultiAnswerAlignmentAnalyzer:

    def analyze(self, analysis_id: str, candidate_answers: list[str]) -> AlignmentRecord:

        if len(candidate_answers) <= 1:
            return AlignmentRecord(
                analysis_id=analysis_id,
                answers_compared=len(candidate_answers),
                aligned=True,
                divergence_notes=[],
                alignment_score=1.0,
            )

        base = candidate_answers[0].strip().lower()

        divergence = []

        for ans in candidate_answers[1:]:
            if ans.strip().lower() != base:
                divergence.append(f"Divergent answer: {ans}")

        aligned = len(divergence) == 0

        return AlignmentRecord(
            analysis_id=analysis_id,
            answers_compared=len(candidate_answers),
            aligned=aligned,
            divergence_notes=divergence,
            alignment_score=1.0 if aligned else 0.5,
        )
