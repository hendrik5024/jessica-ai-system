# Phase 7.2 Quick Start Guide — Proposal-Bound Execution

## Overview

Phase 7.2 enables Jessica to execute approved action proposals with strict human-in-the-loop control. Once a proposal is approved by a human (Phase 7.1), Phase 7.2 executes only the approved actions with immutable audit trails and single-use enforcement.

## Basic Usage

### 1. Create Execution Request from Approved Proposal

```python
from jessica.execution import create_execution_request

# From Phase 7.1 approved proposal
proposal = ActionProposal(
    proposal_id="prop_123",
    requested_action="send_email",
    approved_actions=["send_email"],
    immutable_parameters={"recipient": "user@example.com", "subject": "Hi"},
    approval_status=ProposalStatus.APPROVED,
    approved_by="human_user",
    approval_timestamp=datetime.now(),
)

# Create immutable execution request
request = create_execution_request(
    proposal_id=proposal.proposal_id,
    approved_actions=proposal.approved_actions,
    immutable_parameters=proposal.immutable_parameters,
)

# Check if execution window still valid
if request.is_expired():
    print("Execution window expired")
else:
    print(f"Time remaining: {request.time_remaining()} seconds")
```

### 2. Validate Execution Against Proposal

```python
from jessica.execution import ExecutionValidator

validator = ExecutionValidator(enabled=True)

# Validate request matches proposal
validation_result = validator.validate_execution_request(request, proposal)

if validation_result.valid:
    print("✓ Execution request validated")
else:
    print(f"✗ Validation failed: {validation_result.error}")
```

### 3. Execute with Orchestrator (Recommended)

```python
from jessica.execution import ExecutionOrchestrator

orchestrator = ExecutionOrchestrator(enabled=True)

# Single entry point for execution
outcome, error = orchestrator.execute_proposal(request, proposal)

if error:
    print(f"Execution failed: {error}")
else:
    print(f"✓ Executed: {outcome.action}")
    print(f"  Status: {outcome.status.value}")
    print(f"  Result: {outcome.result}")
```

### 4. Dry-Run Validation (Optional)

```python
# Check if execution possible without executing
can_execute, error = orchestrator.can_execute(request, proposal)

if can_execute:
    print("✓ Ready to execute")
else:
    print(f"✗ Cannot execute: {error}")
```

### 5. Audit Trail

```python
# Get audit entry for execution
audit_entry = orchestrator.get_execution_audit(request.execution_id)

if audit_entry:
    print(f"Execution ID: {audit_entry.execution_id}")
    print(f"Proposal ID: {audit_entry.proposal_id}")
    print(f"Status: {audit_entry.execution_result.status.value}")
    print(f"Time: {audit_entry.timestamp}")
    print(f"Execution time: {audit_entry.execution_time_ms}ms")

# Get all audit trail for proposal
audit_trail = orchestrator.get_audit_trail_for_proposal(proposal.proposal_id)
print(f"Total executions for proposal: {len(audit_trail)}")
```

## Advanced Usage

### Check Single-Use Enforcement

```python
# Check if already executed (prevents re-execution)
if orchestrator.has_executed(request.execution_id):
    print("✗ Already executed (single-use only)")
else:
    print("✓ Not yet executed")
```

### Manual Execution (Not Recommended)

```python
from jessica.execution import ExecutionEngine, ExecutionAudit

# Not recommended - use orchestrator instead
engine = ExecutionEngine(enabled=True)
audit = ExecutionAudit(enabled=True)

# Manual flow (orchestrator does this automatically)
outcome, error = engine.execute(request)
if not error:
    audit.record_execution(request, outcome, proposal.proposal_id)
```

### Disable Execution (Safety Switch)

```python
# Global safety switch (reversible)
orchestrator.disable()
print("Execution disabled")

# Re-enable if needed
orchestrator.enable()
print("Execution enabled")
```

## API Reference

### ExecutionRequest

```python
# Factory
request = create_execution_request(
    proposal_id: str,
    approved_actions: list[str],
    immutable_parameters: dict,
    execution_window_seconds: int = 3600,  # 1 hour default
) -> ExecutionRequest

# Properties
request.execution_id              # UUID
request.proposal_id               # From proposal
request.approved_actions          # Approved action names
request.immutable_parameters      # Locked parameters
request.execution_expiry          # Expiration time
request.approved_by               # Approver ID
request.created_at                # Creation timestamp

# Methods
request.is_expired()              # bool
request.time_remaining()          # int (seconds)
request.to_dict()                 # dict (read-only)
```

### ExecutionValidator

```python
from jessica.execution import ExecutionValidator, ValidationResult

validator = ExecutionValidator(enabled=True)

# Main validation
result = validator.validate_execution_request(
    execution_request: ExecutionRequest,
    proposal: ActionProposal,
) -> ValidationResult

# Quick checks
result = validator.validate_proposal_exists_and_approved(
    proposal_id: str,
) -> ValidationResult

# Specific validations
result = validator.validate_execution_window_not_expired(
    request: ExecutionRequest,
) -> ValidationResult

result = validator.validate_parameters_match(
    request: ExecutionRequest,
    proposal: ActionProposal,
) -> ValidationResult

# Safety switches
validator.disable()
validator.enable()

# Check result
if result.valid:
    print("✓ Validated")
else:
    print(f"✗ Error: {result.error}")
```

### ExecutionEngine

```python
from jessica.execution import ExecutionEngine, ExecutionResult, ExecutionResultStatus

engine = ExecutionEngine(enabled=True)

# Execute
outcome, error = engine.execute(
    execution_request: ExecutionRequest,
) -> tuple[Optional[ExecutionResult], Optional[str]]

# Get status
status = engine.get_execution_status(
    execution_id: str,
) -> Optional[ExecutionResultStatus]

# Get outcome
outcome = engine.get_execution_outcome(
    execution_id: str,
) -> Optional[ExecutionResult]

# Check if executed
if engine.has_executed(execution_id):
    print("Already executed")

# Get history
history = engine.get_execution_history() -> Dict[str, ExecutionResult]

# Safety switches
engine.disable()
engine.enable()

# ExecutionResultStatus values
ExecutionResultStatus.SUCCESS   # Successful execution
ExecutionResultStatus.FAILED    # Execution failed
ExecutionResultStatus.REJECTED  # Validation rejected
ExecutionResultStatus.EXPIRED   # Execution window expired

# ExecutionResult fields
outcome.execution_id            # UUID
outcome.status                  # ExecutionResultStatus
outcome.action                  # Action name
outcome.outcome_timestamp       # When executed
outcome.result                  # Result dict (if any)
outcome.error                   # Error message (if any)
outcome.metadata                # Additional context
```

### ExecutionAudit

```python
from jessica.execution import ExecutionAudit, AuditEntry

audit = ExecutionAudit(enabled=True)

# Record execution
error = audit.record_execution(
    execution_request: ExecutionRequest,
    execution_result: ExecutionResult,
    proposal_id: str,
    notes: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Optional[str]

# Query by execution ID
entries = audit.get_entries_for_execution(
    execution_id: str,
) -> List[AuditEntry]

# Query by proposal ID
entries = audit.get_entries_for_proposal(
    proposal_id: str,
) -> List[AuditEntry]

# Filter by status
entries = audit.get_entries_by_status(
    status: ExecutionResultStatus,
) -> List[AuditEntry]

# Get all entries (chronological)
all_entries = audit.get_all_entries() -> List[AuditEntry]

# Statistics
counts = audit.count_by_status() -> Dict[ExecutionResultStatus, int]
stats = audit.get_audit_stats() -> Dict[str, Any]

# Safety switches
audit.disable()
audit.enable()

# AuditEntry fields (all immutable)
entry.audit_id                  # UUID
entry.execution_id              # UUID
entry.proposal_id               # Proposal ID
entry.execution_request         # Frozen copy
entry.execution_result          # Frozen copy
entry.executor                  # Who executed
entry.timestamp                 # When recorded
entry.execution_time_ms         # Duration
entry.notes                     # Optional notes
entry.metadata                  # Optional context
```

### ExecutionOrchestrator

```python
from jessica.execution import ExecutionOrchestrator

orchestrator = ExecutionOrchestrator(enabled=True)

# Main entry point (ONLY way to execute)
outcome, error = orchestrator.execute_proposal(
    execution_request: ExecutionRequest,
    proposal: ActionProposal,
) -> tuple[Optional[ExecutionResult], Optional[str]]

# Dry-run validation
can_execute, error = orchestrator.can_execute(
    execution_request: ExecutionRequest,
    proposal: ActionProposal,
) -> tuple[bool, Optional[str]]

# Check if already executed
if orchestrator.has_executed(
    execution_id: str,
) -> bool:
    print("Already executed (single-use)")

# Get audit entry
entry = orchestrator.get_execution_audit(
    execution_id: str,
) -> Optional[AuditEntry]

# Get audit trail for proposal
trail = orchestrator.get_audit_trail_for_proposal(
    proposal_id: str,
) -> List[AuditEntry]

# Statistics
stats = orchestrator.get_execution_stats() -> Dict[str, Any]

# Safety switches
orchestrator.disable()
orchestrator.enable()
```

## Common Patterns

### Pattern 1: Complete Flow

```python
from jessica.execution import (
    create_execution_request,
    ExecutionValidator,
    ExecutionOrchestrator,
)

# 1. Create request from approved proposal
request = create_execution_request(
    proposal.proposal_id,
    proposal.approved_actions,
    proposal.immutable_parameters,
)

# 2. Validate against proposal
validator = ExecutionValidator()
result = validator.validate_execution_request(request, proposal)
if not result.valid:
    print(f"Validation failed: {result.error}")
    return

# 3. Execute via orchestrator
orchestrator = ExecutionOrchestrator()
outcome, error = orchestrator.execute_proposal(request, proposal)

if error:
    print(f"Execution failed: {error}")
else:
    print(f"✓ Executed: {outcome.action}")
    print(f"  Status: {outcome.status.value}")
```

### Pattern 2: Audit Query

```python
orchestrator = ExecutionOrchestrator()

# Get all executions for proposal
audit_trail = orchestrator.get_audit_trail_for_proposal("prop_123")

# Filter successful executions
successful = [
    entry for entry in audit_trail
    if entry.execution_result.status.value == "success"
]

print(f"Successful executions: {len(successful)}")
for entry in successful:
    print(f"  - {entry.execution_id}: {entry.execution_result.action}")
```

### Pattern 3: Error Recovery

```python
request = create_execution_request(...)
orchestrator = ExecutionOrchestrator()

# Check if can execute before executing
can_execute, error = orchestrator.can_execute(request, proposal)

if not can_execute:
    print(f"Cannot execute: {error}")
    if "expired" in error.lower():
        print("Execution window expired, request new approval")
    elif "mismatch" in error.lower():
        print("Parameters do not match proposal")
    return

# Safe to execute
outcome, error = orchestrator.execute_proposal(request, proposal)
```

## Constraint Guarantees

| Constraint | Guarantee |
|-----------|-----------|
| One execution per approval | Single-use enforcement via orchestrator |
| Human remains in loop | Per execution window, proposal-bound |
| Immutable audit trail | Append-only AuditEntry (frozen dataclass) |
| No re-execution | orchestrator.has_executed() prevents it |
| Scope enforcement | Validator checks actions exact match |
| Hard-fail validation | Validator rejects any mismatch (no corrections) |
| Parameter locking | immutable_parameters frozen at request time |
| Time window | execution_expiry enforced, 1-hour default |

## Testing

```python
import pytest
from jessica.execution import create_execution_request, ExecutionOrchestrator

def test_execution():
    # Create request
    request = create_execution_request(
        proposal_id="test_prop",
        approved_actions=["test_action"],
        immutable_parameters={},
    )
    
    # Execute
    orchestrator = ExecutionOrchestrator()
    outcome, error = orchestrator.execute_proposal(request, proposal)
    
    # Verify
    assert error is None
    assert outcome is not None
    assert not orchestrator.has_executed(request.execution_id)  # Before execution
    assert orchestrator.has_executed(request.execution_id)      # After execution (prevented)
```

## Troubleshooting

### Execution rejected with "Validation failed"
- Check proposal is in APPROVED status
- Check execution window not expired
- Check actions match proposal exactly
- Check parameters match proposal exactly

### "Already executed (single-use only)"
- Each execution_id can only execute once
- Request new approval for another execution
- Create new ExecutionRequest for retry

### "Execution window expired"
- Execution must occur within 1 hour of request creation
- Request new approval and create new ExecutionRequest

### "Engine is disabled"
- Check orchestrator.enabled is True
- Call orchestrator.enable() if disabled
- Check engine.enabled is True

## Best Practices

1. **Always use ExecutionOrchestrator** — Don't call engine/audit directly
2. **Check dry-run first** — Use can_execute() before execute_proposal()
3. **Audit trail review** — Check get_audit_trail_for_proposal() after execution
4. **Time windows** — Create requests close to execution time
5. **Error messages** — Read validation errors carefully (they explain failures)
6. **Single-use** — Don't assume execution_id can be reused
7. **Immutability** — Don't try to modify requests after creation

## See Also

- [Phase 7.1 Action Proposals](PHASE_7_1_QUICK_START.md)
- [Phase 6 Decision Support](../jessica/execution/test_phase_6_decision_support.py)
- [Phase 5.2 Action Execution](../jessica/execution/test_phase_5_2_execution.py)
- [PHASE_7_2_COMPLETION_REPORT.md](PHASE_7_2_COMPLETION_REPORT.md)
