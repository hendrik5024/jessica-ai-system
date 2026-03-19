from dataclasses import FrozenInstanceError
from time import time

import pytest

from jessica.integrity.post_execution_integrity_verifier import PostExecutionIntegrityVerifier
from jessica.sandbox.repair_sandbox_executor import SandboxExecutionResult


def _result(log, success=True, violations=None):
    return SandboxExecutionResult(
        execution_id="exec-1",
        contract_id="c1",
        repair_plan_id="p1",
        start_timestamp=time(),
        end_timestamp=time(),
        execution_success=success,
        execution_log=log,
        sandbox_violations=violations or [],
    )


def test_successful_repair_passes_verification():

    verifier = PostExecutionIntegrityVerifier()
    result = _result([
        "Sandbox context initialized.",
        "Executing: step1",
        "Execution completed.",
    ])
    expected = {
        "required_actions": ["step1"],
        "allowed_actions": ["step1"],
    }

    report = verifier.verify_execution(result, expected)

    assert report.integrity_passed is True


def test_incomplete_repair_fails_verification():

    verifier = PostExecutionIntegrityVerifier()
    result = _result(["Sandbox context initialized.", "Executing: step1"]) 
    expected = {"required_actions": ["step1"]}

    report = verifier.verify_execution(result, expected)

    assert report.integrity_passed is False
    assert "Execution did not complete" in report.mismatches_detected


def test_unintended_changes_detected():

    verifier = PostExecutionIntegrityVerifier()
    result = _result([
        "Sandbox context initialized.",
        "Executing: step1",
        "Executing: extra",
        "Execution completed.",
    ])
    expected = {
        "required_actions": ["step1"],
        "allowed_actions": ["step1"],
    }

    report = verifier.verify_execution(result, expected)

    assert report.integrity_passed is False
    assert "Unintended action: extra" in report.mismatches_detected


def test_mismatches_logged():

    verifier = PostExecutionIntegrityVerifier()
    result = _result([
        "Sandbox context initialized.",
        "Execution completed.",
    ], success=False)
    expected = {"required_actions": ["step1"]}

    report = verifier.verify_execution(result, expected)

    assert "Execution not successful" in report.mismatches_detected
    assert "Missing required action: step1" in report.mismatches_detected


def test_verification_result_immutable():

    verifier = PostExecutionIntegrityVerifier()
    result = _result([
        "Sandbox context initialized.",
        "Executing: step1",
        "Execution completed.",
    ])
    expected = {"required_actions": ["step1"]}

    report = verifier.verify_execution(result, expected)

    with pytest.raises(FrozenInstanceError):
        report.integrity_passed = False


def test_governance_review_triggered_on_failure():

    verifier = PostExecutionIntegrityVerifier()
    result = _result([
        "Sandbox context initialized.",
        "Execution completed.",
    ], success=False)
    expected = {}

    report = verifier.verify_execution(result, expected)

    assert report.integrity_passed is False
    assert "governance review required" in report.verification_notes.lower()
