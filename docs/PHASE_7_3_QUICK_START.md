# Phase 7.3: Reflective Intelligence Layer - QUICK START GUIDE

**Purpose:** Read-only, advisory-only reflection on completed executions and proposals

**Key Principle:** Analyze the past, inform the human, never execute or influence decisions

---

## 5-Minute Quick Start

### Basic Execution Reflection

```python
from jessica.execution import ReflectionOrchestrator

# Initialize
orchestrator = ReflectionOrchestrator()

# Reflect on execution
execution_data = {
    "execution_id": "exec_123",
    "action": "send_email",
    "status": "success",
    "parameters": {"to": "user@example.com"},
}

reflection, error = orchestrator.reflect_on_execution(execution_data)

if reflection:
    print(f"Summary: {reflection.summary}")
    print(f"Risks: {reflection.risk_count()}")
    print(f"Confidence: {reflection.confidence_level.value}")
```

### Basic Proposal Reflection

```python
# Reflect on proposal
proposal_data = {
    "proposal_id": "prop_456",
    "requested_action": "delete_file",
    "approval_status": "denied",
    "risk_level": "high",
}

reflection, error = orchestrator.reflect_on_proposal(proposal_data)

if reflection:
    print(f"Summary: {reflection.summary}")
    if reflection.has_risks():
        print(f"Risks: {reflection.identified_risks}")
```

---

## Core Concepts

### 1. Reflection Records

**Immutable records** of analysis results:

```python
from jessica.execution import create_reflection_record, SourceType, ConfidenceLevel

record = create_reflection_record(
    source_type=SourceType.EXECUTION,
    source_id="exec_123",
    summary="Execution completed successfully",
    identified_risks=["Network latency detected"],
    anomalies=[],
    confidence_level=ConfidenceLevel.HIGH,
    notes="All parameters validated",
)

# Records are frozen (immutable)
print(record.reflection_id)  # Auto-generated: "refl_..."
print(record.has_risks())     # True
print(record.risk_count())    # 1
```

### 2. Deterministic Factory

**Same input always produces same reflection:**

```python
from jessica.execution import ReflectionFactory

factory = ReflectionFactory()

# Reflect on execution
reflection1, _ = factory.reflect_on_execution({
    "execution_id": "exec_123",
    "action": "test",
    "status": "success",
})

reflection2, _ = factory.reflect_on_execution({
    "execution_id": "exec_123",
    "action": "test",
    "status": "success",
})

# Identical results (deterministic)
assert reflection1.summary == reflection2.summary
assert reflection1.identified_risks == reflection2.identified_risks
```

### 3. Read-Only Analyzer

**Analyze reflections without mutating data:**

```python
from jessica.execution import ReflectionAnalyzer, SourceType

analyzer = ReflectionAnalyzer()

# Single reflection analysis
analysis = analyzer.analyze_single_reflection(reflection)
print(f"Risk level: {analysis['risk_level']}")      # low/medium/high
print(f"Issue count: {analysis['issue_count']}")    # Total risks + anomalies

# Aggregate multiple reflections
reflections = orchestrator.get_all_reflections()
aggregation = analyzer.aggregate_reflections(reflections)
print(f"Total: {aggregation['total_reflections']}")
print(f"Total risks: {aggregation['total_risks']}")

# Filtering (returns new list, never mutates)
exec_only = analyzer.filter_by_source_type(reflections, SourceType.EXECUTION)
with_risks = analyzer.filter_with_risks(reflections)

# Sorting (returns new list)
sorted_by_risk = analyzer.sort_by_risk_count(reflections, descending=True)
```

### 4. Append-Only Registry

**Store reflections, never delete:**

```python
from jessica.execution import ReflectionRegistry

registry = ReflectionRegistry()

# Add reflections (append-only)
error = registry.add_reflection(reflection)
if error:
    print(f"Duplicate or invalid: {error}")

# Query by various criteria
by_id = registry.get_reflection_by_id("refl_123")
by_source = registry.get_reflections_by_source_id("exec_123")
with_risks = registry.get_reflections_with_risks()
all_reflections = registry.get_all_reflections()  # Chronological order

# Statistics
stats = registry.get_registry_stats()
print(f"Total: {stats['total_reflections']}")
print(f"With risks: {stats['with_risks']}")
print(f"By type: {stats['by_source_type']}")
```

### 5. Orchestrator (Single Entry Point)

**Coordinates factory + registry:**

```python
orchestrator = ReflectionOrchestrator()

# Complete workflow: validate → generate → store → return
reflection, error = orchestrator.reflect_on_execution(execution_data)

# Query delegation
all_reflections = orchestrator.get_all_reflections()
reflections_for_source = orchestrator.get_reflections_for_source("exec_123")
has_reflection = orchestrator.has_reflection_for_source("exec_123")

# Statistics
count = orchestrator.count_reflections()
stats = orchestrator.get_reflection_stats()
```

---

## Common Patterns

### Pattern 1: Post-Execution Analysis

```python
# After Phase 7.2 execution completes
execution_result, error = execution_orchestrator.execute_proposal(proposal)

# Reflect on result
reflection_data = {
    "execution_id": execution_result.execution_id,
    "action": execution_result.action,
    "status": execution_result.status.value,
    "parameters": execution_result.parameters,
    "result": execution_result.result,
    "error": execution_result.error,
}

reflection, error = reflection_orchestrator.reflect_on_execution(reflection_data)

# Human reviews
if reflection and reflection.has_risks():
    print(f"⚠️ Risks identified: {reflection.identified_risks}")
```

### Pattern 2: Proposal Review Analysis

```python
# After Phase 7.1 proposal is approved/denied
proposal = proposal_registry.get_proposal_by_id("prop_123")

# Reflect on decision
reflection_data = {
    "proposal_id": proposal.proposal_id,
    "requested_action": proposal.requested_action,
    "approval_status": proposal.approval_status.value,
    "denial_reason": proposal.denial_reason,
}

reflection, error = reflection_orchestrator.reflect_on_proposal(reflection_data)

# Human reviews
print(f"Confidence: {reflection.confidence_level.value}")
```

### Pattern 3: Batch Analysis

```python
# Reflect on multiple executions
executions = [
    {"execution_id": f"exec_{i}", "action": "test", "status": "success"}
    for i in range(10)
]

reflections = []
for exec_data in executions:
    reflection, error = orchestrator.reflect_on_execution(exec_data)
    if reflection:
        reflections.append(reflection)

# Aggregate analysis
aggregation = analyzer.aggregate_reflections(reflections)
print(f"Success rate: {aggregation['by_status']['success'] / len(reflections):.2%}")
print(f"Average risks: {aggregation['averages']['risks_per_reflection']:.2f}")
```

### Pattern 4: Risk Trending

```python
# Get all reflections
reflections = orchestrator.get_all_reflections()

# Filter high-risk reflections
high_risk = [r for r in reflections if r.risk_count() >= 3]

# Sort by risk count
sorted_by_risk = analyzer.sort_by_risk_count(reflections, descending=True)

# Risk summary
risk_summary = analyzer.get_risk_summary(reflections)
print(f"Most common risk: {risk_summary['most_common_risk']}")
print(f"Risk frequency: {risk_summary['risk_frequency']}")
```

### Pattern 5: Confidence Analysis

```python
from jessica.execution import ConfidenceLevel

# Filter by confidence level
reflections = orchestrator.get_all_reflections()

high_confidence = analyzer.filter_by_confidence(
    reflections,
    ConfidenceLevel.HIGH,
)

low_confidence = analyzer.filter_by_confidence(
    reflections,
    ConfidenceLevel.LOW,
)

print(f"High confidence: {len(high_confidence)}")
print(f"Low confidence: {len(low_confidence)} (needs review)")
```

---

## Safety Controls

### Disable All Reflection

```python
# Temporarily disable
orchestrator.disable()

reflection, error = orchestrator.reflect_on_execution(execution_data)
print(error)  # "ReflectionOrchestrator is disabled"

# Re-enable
orchestrator.enable()
reflection, error = orchestrator.reflect_on_execution(execution_data)
```

### Generate Without Storing

```python
# Generate reflection but don't store in registry
reflection, error = orchestrator.reflect_on_execution(
    execution_data,
    store_in_registry=False,
)

# Reflection created, but not in registry
print(orchestrator.has_reflection_for_source("exec_123"))  # False
```

---

## API Reference

### ReflectionOrchestrator

**Main entry point for reflection:**

```python
class ReflectionOrchestrator:
    def __init__(self):
        """Initialize with factory and registry"""
    
    # Workflow methods
    def reflect_on_execution(
        self,
        execution_data: dict,
        store_in_registry: bool = True,
    ) -> Tuple[Optional[ReflectionRecord], Optional[str]]:
        """
        Reflect on completed execution.
        
        Required fields:
        - execution_id: str
        - action: str
        - status: str (success/failure)
        
        Optional fields:
        - parameters: dict
        - result: any
        - error: str
        """
    
    def reflect_on_proposal(
        self,
        proposal_data: dict,
        store_in_registry: bool = True,
    ) -> Tuple[Optional[ReflectionRecord], Optional[str]]:
        """
        Reflect on completed proposal.
        
        Required fields:
        - proposal_id: str
        - requested_action: str
        - approval_status: str (approved/denied)
        
        Optional fields:
        - approved_actions: list
        - denial_reason: str
        - risk_level: str
        """
    
    # Query methods (delegate to registry)
    def get_reflection_by_id(self, reflection_id: str) -> Optional[ReflectionRecord]:
        """Get reflection by ID"""
    
    def get_reflections_for_source(self, source_id: str) -> List[ReflectionRecord]:
        """Get all reflections for a source (execution or proposal)"""
    
    def has_reflection_for_source(self, source_id: str) -> bool:
        """Check if reflections exist for source"""
    
    def get_all_reflections(self) -> List[ReflectionRecord]:
        """Get all reflections in chronological order"""
    
    def get_reflections_by_type(self, source_type: SourceType) -> List[ReflectionRecord]:
        """Get reflections by source type"""
    
    def get_reflections_with_risks(self) -> List[ReflectionRecord]:
        """Get reflections that have identified risks"""
    
    def get_reflections_with_anomalies(self) -> List[ReflectionRecord]:
        """Get reflections that have detected anomalies"""
    
    def get_reflection_stats(self) -> Dict[str, any]:
        """Get comprehensive statistics"""
    
    def count_reflections(self) -> int:
        """Get total reflection count"""
    
    # Safety methods
    def disable(self):
        """Disable all reflection generation"""
    
    def enable(self):
        """Re-enable reflection generation"""
```

### ReflectionRecord

**Immutable reflection record:**

```python
@dataclass(frozen=True)
class ReflectionRecord:
    reflection_id: str          # Auto-generated UUID
    source_type: SourceType     # EXECUTION or PROPOSAL
    source_id: str              # execution_id or proposal_id
    summary: str                # Human-readable summary
    identified_risks: List[str] # List of identified risks
    anomalies: List[str]        # List of detected anomalies
    confidence_level: ConfidenceLevel  # LOW, MEDIUM, HIGH
    created_at: datetime        # Timestamp
    notes: Optional[str]        # Optional notes
    
    # Helper methods
    def has_risks(self) -> bool
    def has_anomalies(self) -> bool
    def risk_count(self) -> int
    def anomaly_count(self) -> int
    def to_dict(self) -> Dict[str, any]
```

### Enums

```python
class SourceType(Enum):
    EXECUTION = "execution"
    PROPOSAL = "proposal"

class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

---

## Error Handling

### Common Errors

```python
# 1. Missing required fields
reflection, error = orchestrator.reflect_on_execution({})
print(error)  # "execution_id is required"

# 2. Orchestrator disabled
orchestrator.disable()
reflection, error = orchestrator.reflect_on_execution(execution_data)
print(error)  # "ReflectionOrchestrator is disabled"

# 3. Duplicate reflection
registry.add_reflection(reflection)
error = registry.add_reflection(reflection)
print(error)  # "Reflection refl_... already exists"

# 4. Invalid reflection ID
reflection = orchestrator.get_reflection_by_id("invalid_id")
print(reflection)  # None
```

### Best Practices

1. **Always check errors:**
   ```python
   reflection, error = orchestrator.reflect_on_execution(execution_data)
   if error:
       print(f"Failed: {error}")
       return
   ```

2. **Validate input data:**
   ```python
   if not execution_data.get("execution_id"):
       print("Missing execution_id")
       return
   ```

3. **Use disable/enable for testing:**
   ```python
   # Test mode: generate but don't store
   reflection, _ = orchestrator.reflect_on_execution(
       execution_data,
       store_in_registry=False,
   )
   ```

---

## Constraints

### What Phase 7.3 CAN Do

- ✅ Reflect on completed executions
- ✅ Reflect on completed proposals
- ✅ Identify risks deterministically
- ✅ Detect anomalies deterministically
- ✅ Aggregate statistics (read-only)
- ✅ Filter and sort reflections
- ✅ Store in append-only registry

### What Phase 7.3 CANNOT Do

- ❌ Execute actions
- ❌ Generate proposals
- ❌ Influence decisions
- ❌ Learn or adapt (stateless)
- ❌ Run autonomously
- ❌ Chain reflections
- ❌ Predict future outcomes
- ❌ Modify or delete reflections

---

## Testing

### Quick Test

```python
# Test complete workflow
orchestrator = ReflectionOrchestrator()

execution_data = {
    "execution_id": "test_123",
    "action": "test_action",
    "status": "success",
}

reflection, error = orchestrator.reflect_on_execution(execution_data)

assert error is None
assert reflection is not None
assert reflection.source_type == SourceType.EXECUTION
assert orchestrator.has_reflection_for_source("test_123")

print("✅ Phase 7.3 working correctly")
```

### Run Full Test Suite

```bash
# Phase 7.3 tests only
python -m pytest tests/test_phase_7_3_reflection.py --tb=no -q

# Expected: 34 passed

# Full execution layer tests
python -m pytest jessica/execution/ --tb=no -q

# Expected: 109 passed

# Full system tests
python -m pytest --tb=no -q

# Expected: 844 passed, 27 skipped
```

---

## Troubleshooting

### Issue: "ReflectionOrchestrator is disabled"

**Cause:** Orchestrator was disabled via `disable()`

**Solution:**
```python
orchestrator.enable()
```

### Issue: Duplicate reflection error

**Cause:** Same reflection added twice to registry

**Solution:** Registry rejects duplicates by design (append-only). This is expected behavior.

### Issue: Empty reflections list

**Cause:** No reflections generated or `store_in_registry=False`

**Solution:**
```python
# Ensure storing in registry
reflection, error = orchestrator.reflect_on_execution(
    execution_data,
    store_in_registry=True,  # Default
)
```

### Issue: Determinism not working

**Cause:** Different input data (even slight differences)

**Solution:** Ensure exact same input:
```python
# Must be identical
data1 = {"execution_id": "exec_1", "action": "test", "status": "success"}
data2 = {"execution_id": "exec_1", "action": "test", "status": "success"}

r1, _ = factory.reflect_on_execution(data1)
r2, _ = factory.reflect_on_execution(data2)

assert r1.summary == r2.summary  # Should pass
```

---

## Performance Tips

1. **Batch queries:** Use `get_all_reflections()` once instead of multiple queries
2. **Use filters:** Filter in-memory with `ReflectionAnalyzer` instead of repeated queries
3. **Index lookups:** Use `get_reflections_for_source()` for fast indexed access
4. **Disable if not needed:** Use `disable()` to skip reflection generation entirely

---

## Next Steps

1. **Integrate with Phase 7.2:** Add reflection after execution
2. **Integrate with Phase 7.1:** Add reflection after proposal approval/denial
3. **Build dashboards:** Use aggregation and statistics for human review
4. **Pattern recognition:** Use `ReflectionAnalyzer` to identify trends (Phase 7.4 candidate)

---

## Complete Example

```python
from jessica.execution import (
    ReflectionOrchestrator,
    ReflectionAnalyzer,
    SourceType,
    ConfidenceLevel,
)

# Initialize
orchestrator = ReflectionOrchestrator()
analyzer = ReflectionAnalyzer()

# Simulate multiple executions
executions = [
    {"execution_id": "exec_1", "action": "send_email", "status": "success"},
    {"execution_id": "exec_2", "action": "delete_file", "status": "failure", "error": "Permission denied"},
    {"execution_id": "exec_3", "action": "read_file", "status": "success"},
]

# Reflect on each
for exec_data in executions:
    reflection, error = orchestrator.reflect_on_execution(exec_data)
    if error:
        print(f"Error: {error}")
    else:
        print(f"Reflected on {exec_data['execution_id']}: {reflection.summary}")

# Aggregate analysis
reflections = orchestrator.get_all_reflections()
aggregation = analyzer.aggregate_reflections(reflections)

print(f"\nTotal reflections: {aggregation['total_reflections']}")
print(f"Total risks: {aggregation['total_risks']}")
print(f"By source type: {aggregation['by_source_type']}")
print(f"Average risks: {aggregation['averages']['risks_per_reflection']:.2f}")

# Filter high-risk
with_risks = analyzer.filter_with_risks(reflections)
print(f"\nHigh-risk reflections: {len(with_risks)}")

for reflection in with_risks:
    print(f"  - {reflection.source_id}: {reflection.identified_risks}")

# Risk summary
risk_summary = analyzer.get_risk_summary(reflections)
if risk_summary['most_common_risk']:
    print(f"\nMost common risk: {risk_summary['most_common_risk']}")
```

---

**Documentation Version:** 1.0
**Last Updated:** 2025-06-XX
**Phase Status:** Production Ready
