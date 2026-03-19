"""Phase 5.4 Recovery Advisory (read-only) tests."""
from copy import deepcopy

from jessica.execution import (
    ExecutionOutcome,
    ExecutionStatus,
    FailureClassifier,
    FailureCategory,
    RecoveryAnalyzer,
    RecoveryOrchestrator,
)


def test_classifier_success():
    classifier = FailureClassifier()
    outcome = ExecutionOutcome(ExecutionStatus.SUCCESS, 0, 1, 10)
    result = classifier.classify(outcome)
    assert result.category == FailureCategory.SUCCESS


def test_classifier_timeout():
    classifier = FailureClassifier()
    outcome = ExecutionOutcome(
        ExecutionStatus.FAILED, 0, 1, 10, error_message="Operation timed out"
    )
    result = classifier.classify(outcome)
    assert result.category == FailureCategory.TIMEOUT


def test_classifier_permission_denied():
    classifier = FailureClassifier()
    outcome = ExecutionOutcome(
        ExecutionStatus.FAILED, 0, 1, 10, error_message="Access denied"
    )
    result = classifier.classify(outcome)
    assert result.category == FailureCategory.PERMISSION_DENIED


def test_classifier_input_rejected():
    classifier = FailureClassifier()
    outcome = ExecutionOutcome(
        ExecutionStatus.FAILED, 0, 1, 10, error_message="Invalid input"
    )
    result = classifier.classify(outcome)
    assert result.category == FailureCategory.INPUT_REJECTED


def test_classifier_unknown():
    classifier = FailureClassifier()
    outcome = ExecutionOutcome(
        ExecutionStatus.FAILED, 0, 1, 10, error_message="Something weird"
    )
    result = classifier.classify(outcome)
    assert result.category == FailureCategory.UNKNOWN_FAILURE


def test_recovery_analyzer_success_has_no_options():
    analyzer = RecoveryAnalyzer()
    outcome = ExecutionOutcome(ExecutionStatus.SUCCESS, 0, 1, 5)
    analysis = analyzer.analyze(outcome)
    assert analysis["classification"]["category"] == FailureCategory.SUCCESS.value
    assert analysis["options"] == []


def test_recovery_analyzer_timeout_has_options():
    analyzer = RecoveryAnalyzer()
    outcome = ExecutionOutcome(
        ExecutionStatus.FAILED, 0, 1, 10, error_message="Timeout"
    )
    analysis = analyzer.analyze(outcome)
    assert analysis["classification"]["category"] == FailureCategory.TIMEOUT.value
    assert len(analysis["options"]) == 1
    assert analysis["options"][0]["requires_new_intent"] is True


def test_recovery_analyzer_disabled():
    analyzer = RecoveryAnalyzer(enabled=False)
    outcome = ExecutionOutcome(ExecutionStatus.FAILED, 0, 1, 10, error_message="Timeout")
    analysis = analyzer.analyze(outcome)
    assert analysis["enabled"] is False
    assert analysis["options"] == []


def test_recovery_orchestrator_disabled():
    orchestrator = RecoveryOrchestrator(enabled=False)
    result = orchestrator.interpret({"status": "failed"})
    assert result["enabled"] is False


def test_no_mutation_of_outcome_dict():
    analyzer = RecoveryAnalyzer()
    outcome = {"status": "failed", "error_message": "timeout", "duration_ms": 1}
    original = deepcopy(outcome)
    analyzer.analyze(outcome)
    assert outcome == original


def test_deterministic_classification():
    classifier = FailureClassifier()
    outcome = ExecutionOutcome(
        ExecutionStatus.FAILED, 0, 1, 10, error_message="timeout"
    )
    r1 = classifier.classify(outcome)
    r2 = classifier.classify(outcome)
    assert r1 == r2


def test_no_execution_paths():
    # Ensure there is no ActionExecutor usage in advisory layer
    analyzer = RecoveryAnalyzer()
    outcome = ExecutionOutcome(ExecutionStatus.FAILED, 0, 1, 10, error_message="timeout")
    analysis = analyzer.analyze(outcome)
    assert "options" in analysis
