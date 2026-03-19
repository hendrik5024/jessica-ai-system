"""
Phase 3.5: Failure Instrumentation & Clustering

This module collects operator-level failures non-invasively during test execution.
Failures are analyzed to identify refinement opportunities.

CONSTRAINTS:
- Domain-agnostic: no domain labels used in clustering
- Non-invasive: zero changes to operator logic
- Auditable: every failure logged with full context
- Reversible: can be disabled at any time
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
from datetime import datetime


class FailureType(Enum):
    """Categories of operator failures (domain-agnostic)."""
    
    # Detection failures
    DETECTION_EMPTY_INPUT = "detection_empty_input"
    DETECTION_AMBIGUOUS = "detection_ambiguous"
    DETECTION_INVALID_INPUT = "detection_invalid_input"
    
    # Constraint failures
    CONSTRAINT_VIOLATED = "constraint_violated"
    CONSTRAINT_AMBIGUOUS_LIMIT = "constraint_ambiguous_limit"
    
    # Optimization failures
    OPTIMIZATION_NO_SOLUTION = "optimization_no_solution"
    OPTIMIZATION_TRADEOFF_UNCLEAR = "optimization_tradeoff_unclear"
    
    # Sequencing failures
    SEQUENCE_PRECONDITIONS_FAILED = "sequence_preconditions_failed"
    SEQUENCE_POSTCONDITIONS_FAILED = "sequence_postconditions_failed"
    
    # Adaptation failures
    ADAPT_NO_ALTERNATIVES = "adapt_no_alternatives"
    ADAPT_GOAL_LOSS_SEVERE = "adapt_goal_loss_severe"
    
    # Substitution failures
    SUBSTITUTE_NO_EQUIVALENTS = "substitute_no_equivalents"
    SUBSTITUTE_POOR_EQUIVALENCE = "substitute_poor_equivalence"
    
    # Structural failures
    OPERATOR_CHAIN_INVALID = "operator_chain_invalid"
    OPERATOR_CHAIN_TIMEOUT = "operator_chain_timeout"


class OperatorType(Enum):
    """Operator classes (domain-agnostic categorization)."""
    DETECT = "DETECT"
    CONSTRAIN = "CONSTRAIN"
    OPTIMIZE = "OPTIMIZE"
    SEQUENCE = "SEQUENCE"
    ADAPT = "ADAPT"
    SUBSTITUTE = "SUBSTITUTE"


@dataclass
class FailureContext:
    """Full context of an operator failure."""
    
    failure_id: str  # Unique identifier
    operator_type: OperatorType
    operator_name: str
    failure_type: FailureType
    
    # Input characteristics (domain-agnostic)
    input_cardinality: int  # Number of input items
    input_complexity: str  # "simple", "moderate", "complex"
    input_range: Tuple[float, float]  # Min/max values observed
    
    # Failure severity
    severity: float  # 0-1, how much did this impact downstream?
    recoverable: bool  # Can fallback handle this?
    
    # Violated assumptions (operator-specific but domain-agnostic)
    violated_assumptions: List[str]
    
    # Affected chain
    chain_depth: int  # How far into the chain?
    downstream_operators: List[str]  # What operators depend on this?
    
    # Trace information
    error_message: str
    full_trace: str
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    domain_context: Optional[str] = None  # For reference, but NOT used in clustering


@dataclass
class FailureCluster:
    """A group of similar failures."""
    
    cluster_id: str
    operator_type: OperatorType
    primary_failure_type: FailureType
    
    # Failure statistics
    failure_count: int
    severity_average: float
    recoverable_ratio: float  # % of failures recoverable
    
    # Violated assumptions (for refinement)
    violated_assumptions: List[str]  # Most common violated assumptions
    assumption_frequency: Dict[str, int]
    
    # Root cause analysis (domain-agnostic)
    likely_root_causes: List[str]
    
    # Refinement recommendations
    suggested_precondition: Optional[str] = None
    suggested_validation: Optional[str] = None
    suggested_parameter_change: Optional[str] = None
    
    # Evidence
    sample_failures: List[FailureContext] = field(default_factory=list)


class FailureCollector:
    """
    Non-invasive failure collection during operator execution.
    
    Usage:
        collector = FailureCollector()
        # ... run tests ...
        clusters = collector.analyze_failures()
    """
    
    def __init__(self):
        self.failures: Dict[str, FailureContext] = {}
        self.failure_sequence: List[str] = []  # Temporal order
        self._failure_counter = 0
        self._enabled = True
    
    def record_failure(
        self,
        operator_type: OperatorType,
        operator_name: str,
        failure_type: FailureType,
        input_cardinality: int,
        input_complexity: str,
        input_range: Tuple[float, float],
        severity: float,
        recoverable: bool,
        violated_assumptions: List[str],
        chain_depth: int,
        downstream_operators: List[str],
        error_message: str,
        full_trace: str,
        domain_context: Optional[str] = None
    ) -> str:
        """
        Record an operator failure.
        
        Returns:
            failure_id for reference
        """
        if not self._enabled:
            return ""
        
        self._failure_counter += 1
        failure_id = f"FAIL_{self._failure_counter:05d}"
        
        failure = FailureContext(
            failure_id=failure_id,
            operator_type=operator_type,
            operator_name=operator_name,
            failure_type=failure_type,
            input_cardinality=input_cardinality,
            input_complexity=input_complexity,
            input_range=input_range,
            severity=severity,
            recoverable=recoverable,
            violated_assumptions=violated_assumptions,
            chain_depth=chain_depth,
            downstream_operators=downstream_operators,
            error_message=error_message,
            full_trace=full_trace,
            domain_context=domain_context
        )
        
        self.failures[failure_id] = failure
        self.failure_sequence.append(failure_id)
        
        return failure_id
    
    def analyze_failures(self) -> Dict[str, FailureCluster]:
        """
        Cluster failures by operator type + failure type.
        
        Returns:
            Dict[cluster_id] → FailureCluster
        """
        clusters: Dict[str, FailureCluster] = {}
        
        # Group by (operator_type, failure_type)
        failure_groups: Dict[Tuple, List[FailureContext]] = {}
        
        for failure in self.failures.values():
            key = (failure.operator_type, failure.failure_type)
            if key not in failure_groups:
                failure_groups[key] = []
            failure_groups[key].append(failure)
        
        # Create clusters
        for (op_type, fail_type), group in failure_groups.items():
            cluster_id = f"CLUSTER_{op_type.value}_{fail_type.value}"
            
            # Aggregate assumptions
            all_assumptions: Dict[str, int] = {}
            for failure in group:
                for assumption in failure.violated_assumptions:
                    all_assumptions[assumption] = all_assumptions.get(assumption, 0) + 1
            
            # Sort by frequency
            sorted_assumptions = sorted(all_assumptions.items(), key=lambda x: x[1], reverse=True)
            
            # Recoverable ratio
            recoverable_count = sum(1 for f in group if f.recoverable)
            recoverable_ratio = recoverable_count / len(group) if group else 0.0
            
            # Average severity
            avg_severity = sum(f.severity for f in group) / len(group) if group else 0.0
            
            # Root cause analysis (domain-agnostic)
            likely_causes = self._infer_root_causes(op_type, group)
            
            # Refinement suggestions
            precond, validation, param = self._suggest_refinement(op_type, group, sorted_assumptions)
            
            cluster = FailureCluster(
                cluster_id=cluster_id,
                operator_type=op_type,
                primary_failure_type=fail_type,
                failure_count=len(group),
                severity_average=avg_severity,
                recoverable_ratio=recoverable_ratio,
                violated_assumptions=[a for a, _ in sorted_assumptions],
                assumption_frequency={a: f for a, f in sorted_assumptions},
                likely_root_causes=likely_causes,
                suggested_precondition=precond,
                suggested_validation=validation,
                suggested_parameter_change=param,
                sample_failures=group[:3]  # First 3 as examples
            )
            
            clusters[cluster_id] = cluster
        
        return clusters
    
    def _infer_root_causes(
        self,
        operator_type: OperatorType,
        failures: List[FailureContext]
    ) -> List[str]:
        """Infer domain-agnostic root causes."""
        
        causes = []
        
        # DETECT operator failures
        if operator_type == OperatorType.DETECT:
            empty_inputs = sum(1 for f in failures if f.failure_type == FailureType.DETECTION_EMPTY_INPUT)
            ambiguous = sum(1 for f in failures if f.failure_type == FailureType.DETECTION_AMBIGUOUS)
            
            if empty_inputs > 0:
                causes.append(f"Empty input handling: {empty_inputs} cases")
            if ambiguous > 0:
                causes.append(f"Ambiguous components (equal throughput): {ambiguous} cases")
        
        # CONSTRAIN operator failures
        elif operator_type == OperatorType.CONSTRAIN:
            violations = sum(1 for f in failures if f.failure_type == FailureType.CONSTRAINT_VIOLATED)
            causes.append(f"Constraint violations: {violations} cases")
        
        # OPTIMIZE operator failures
        elif operator_type == OperatorType.OPTIMIZE:
            no_solution = sum(1 for f in failures if f.failure_type == FailureType.OPTIMIZATION_NO_SOLUTION)
            if no_solution > 0:
                causes.append(f"No feasible solution: {no_solution} cases")
        
        # SEQUENCE operator failures
        elif operator_type == OperatorType.SEQUENCE:
            preconds_failed = sum(1 for f in failures if f.failure_type == FailureType.SEQUENCE_PRECONDITIONS_FAILED)
            if preconds_failed > 0:
                causes.append(f"Precondition failures: {preconds_failed} cases")
        
        # ADAPT operator failures
        elif operator_type == OperatorType.ADAPT:
            no_alts = sum(1 for f in failures if f.failure_type == FailureType.ADAPT_NO_ALTERNATIVES)
            severe_loss = sum(1 for f in failures if f.failure_type == FailureType.ADAPT_GOAL_LOSS_SEVERE)
            if no_alts > 0:
                causes.append(f"No alternatives available: {no_alts} cases")
            if severe_loss > 0:
                causes.append(f"Severe goal degradation: {severe_loss} cases")
        
        # SUBSTITUTE operator failures
        elif operator_type == OperatorType.SUBSTITUTE:
            no_equiv = sum(1 for f in failures if f.failure_type == FailureType.SUBSTITUTE_NO_EQUIVALENTS)
            poor_equiv = sum(1 for f in failures if f.failure_type == FailureType.SUBSTITUTE_POOR_EQUIVALENCE)
            if no_equiv > 0:
                causes.append(f"No equivalent alternatives: {no_equiv} cases")
            if poor_equiv > 0:
                causes.append(f"Poor equivalence matches: {poor_equiv} cases")
        
        return causes
    
    def _suggest_refinement(
        self,
        operator_type: OperatorType,
        failures: List[FailureContext],
        assumptions: List[Tuple[str, int]]
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Suggest refinements (precondition, validation, parameter).
        
        Returns:
            (suggested_precondition, suggested_validation, suggested_parameter_change)
        """
        
        precond = None
        validation = None
        param = None
        
        # DETECT operator refinement
        if operator_type == OperatorType.DETECT:
            empty_failures = sum(1 for f in failures if f.failure_type == FailureType.DETECTION_EMPTY_INPUT)
            if empty_failures > len(failures) * 0.3:
                precond = "Check input cardinality > 0 before execution"
                validation = "Return early if components list is empty with clear explanation"
            
            ambiguous_failures = sum(1 for f in failures if f.failure_type == FailureType.DETECTION_AMBIGUOUS)
            if ambiguous_failures > len(failures) * 0.2:
                validation = "Flag ambiguous cases (throughput difference < 5%) for tie-breaking"
        
        # CONSTRAIN operator refinement
        elif operator_type == OperatorType.CONSTRAIN:
            violation_pct = sum(1 for f in failures if f.failure_type == FailureType.CONSTRAINT_VIOLATED) / len(failures)
            if violation_pct > 0.1:
                param = "Add incremental constraint relaxation (10% buffer) before hard limit"
        
        # OPTIMIZE operator refinement
        elif operator_type == OperatorType.OPTIMIZE:
            no_solution_pct = sum(1 for f in failures if f.failure_type == FailureType.OPTIMIZATION_NO_SOLUTION) / len(failures)
            if no_solution_pct > 0.1:
                param = "Improve solver with constraint relaxation backoff (start 100%, reduce to 50%)"
        
        # SEQUENCE operator refinement
        elif operator_type == OperatorType.SEQUENCE:
            preconds_pct = sum(1 for f in failures if f.failure_type == FailureType.SEQUENCE_PRECONDITIONS_FAILED) / len(failures)
            if preconds_pct > 0.2:
                validation = "Validate all preconditions before plan execution; return detailed failure reason"
        
        return precond, validation, param
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall failure statistics."""
        
        if not self.failures:
            return {
                "total_failures": 0,
                "operators_affected": [],
                "failure_types": [],
                "avg_severity": 0.0,
                "recoverable_ratio": 0.0
            }
        
        operators = {}
        failure_types = {}
        total_severity = 0.0
        recoverable_count = 0
        
        for failure in self.failures.values():
            op_name = failure.operator_name
            operators[op_name] = operators.get(op_name, 0) + 1
            
            fail_type = failure.failure_type.value
            failure_types[fail_type] = failure_types.get(fail_type, 0) + 1
            
            total_severity += failure.severity
            if failure.recoverable:
                recoverable_count += 1
        
        return {
            "total_failures": len(self.failures),
            "operators_affected": sorted(operators.items()),
            "failure_types": sorted(failure_types.items()),
            "avg_severity": total_severity / len(self.failures) if self.failures else 0.0,
            "recoverable_ratio": recoverable_count / len(self.failures) if self.failures else 0.0
        }
    
    def export_json(self, filepath: str) -> None:
        """Export all failures to JSON for analysis."""
        
        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_failures": len(self.failures),
                "statistics": self.get_statistics()
            },
            "failures": [
                {
                    "failure_id": f.failure_id,
                    "operator_type": f.operator_type.value,
                    "operator_name": f.operator_name,
                    "failure_type": f.failure_type.value,
                    "severity": f.severity,
                    "recoverable": f.recoverable,
                    "violated_assumptions": f.violated_assumptions,
                    "chain_depth": f.chain_depth,
                    "timestamp": f.timestamp
                }
                for f in self.failures.values()
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Global collector instance
_global_collector = FailureCollector()


def get_collector() -> FailureCollector:
    """Get global failure collector."""
    return _global_collector


def reset_collector() -> None:
    """Reset global collector (for test isolation)."""
    global _global_collector
    _global_collector = FailureCollector()
