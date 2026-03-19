from .alignment_analyzer import MultiAnswerAlignmentAnalyzer
from .alignment_record import AlignmentRecord


class AlignmentOrchestrator:

    def __init__(self):
        self.analyzer = MultiAnswerAlignmentAnalyzer()

    def evaluate(self, analysis_id: str, answers: list[str]) -> AlignmentRecord:
        return self.analyzer.analyze(analysis_id, answers)
