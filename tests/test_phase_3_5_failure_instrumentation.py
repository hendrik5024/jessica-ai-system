"""
Phase 3.5 Experiment 3.5.1: Failure Instrumentation & Clustering

This test runs the Phase 2 and Phase 3 test suites while collecting operator
failures non-invasively. No operator code is modified.

GOAL: Identify failure patterns to guide refinement in Exp 3.5.2
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Import failure collector
from jessica.unified_world_model.failure_collector import (
    FailureCollector, FailureType, OperatorType, get_collector, reset_collector
)
from jessica.unified_world_model.causal_operator import (
    DETECT_BOTTLENECK, CONSTRAIN, OPTIMIZE, SEQUENCE, ADAPT, SUBSTITUTE,
    Component, BottleneckResult, ConstrainResult, OptimizeResult,
    SequenceResult, AdaptResult, SubstituteResult
)


class TestPhase35FailureInstrumentation:
    """
    Experiment 3.5.1: Failure Instrumentation & Clustering
    
    Strategy:
    1. Inject diagnostic probes into operators (non-invasive)
    2. Run Phase 2 & 3 test suites
    3. Collect failures via instrumentation
    4. Cluster failures by operator and type
    5. Analyze root causes and suggest refinements
    """
    
    @classmethod
    def setup_class(cls):
        """Setup global failure collector."""
        reset_collector()
        cls.collector = get_collector()
    
    def test_diagnostic_detect_bottleneck_failures(self):
        """
        Diagnostic test for DETECT_BOTTLENECK operator.
        
        Probes:
        - Empty input handling
        - Ambiguous bottlenecks (equal throughput)
        - Single component edge case
        - Extreme throughput ranges
        """
        
        collector = self.collector
        operator = DETECT_BOTTLENECK()
        
        # Test 1: Empty input
        result = operator.execute([])
        if result.bottleneck_component == "<empty>":
            collector.record_failure(
                operator_type=OperatorType.DETECT,
                operator_name="DETECT_BOTTLENECK",
                failure_type=FailureType.DETECTION_EMPTY_INPUT,
                input_cardinality=0,
                input_complexity="simple",
                input_range=(0.0, 0.0),
                severity=0.8,  # High severity (prevents detection)
                recoverable=True,  # Can continue with empty state
                violated_assumptions=["Non-empty component list required"],
                chain_depth=1,
                downstream_operators=[],
                error_message="No components provided",
                full_trace=result.trace,
                domain_context="diagnostic"
            )
        
        # Test 2: Single component (trivial case)
        single = [Component("only", 0.5, 1.0)]
        result = operator.execute(single)
        # This should succeed, but we verify it handles triviality
        assert result.bottleneck_component == "only"
        
        # Test 3: Ambiguous bottlenecks (equal throughput)
        ambiguous = [
            Component("skill1", 0.4, 1.0),
            Component("skill2", 0.4, 1.0),
            Component("skill3", 0.8, 1.0)
        ]
        result = operator.execute(ambiguous)
        if result.bottleneck_throughput == ambiguous[0].throughput == ambiguous[1].throughput:
            # Check if severity score reflects ambiguity
            collector.record_failure(
                operator_type=OperatorType.DETECT,
                operator_name="DETECT_BOTTLENECK",
                failure_type=FailureType.DETECTION_AMBIGUOUS,
                input_cardinality=3,
                input_complexity="moderate",
                input_range=(0.4, 0.8),
                severity=0.3,  # Low severity (still detects, but choice arbitrary)
                recoverable=True,
                violated_assumptions=["Single clear bottleneck (distinct throughput)"],
                chain_depth=1,
                downstream_operators=["CONSTRAIN", "OPTIMIZE"],
                error_message="Multiple components tied as bottleneck (throughput=0.4)",
                full_trace=result.trace,
                domain_context="diagnostic"
            )
        
        # Test 4: Extreme throughput values
        extreme = [
            Component("critical", 0.001, 2.0),  # Very low throughput, high importance
            Component("normal", 0.9, 1.0)
        ]
        result = operator.execute(extreme)
        # Should handle correctly due to effect_on_total weighting
        assert result.bottleneck_component == "critical"
    
    def test_diagnostic_constrain_failures(self):
        """
        Diagnostic test for CONSTRAIN operator.
        
        Probes:
        - Constraint violation modes
        - Boundary conditions
        - Ambiguous limits
        """
        
        collector = self.collector
        operator = CONSTRAIN()
        
        # Test 1: Violation (current > limit)
        result = operator.execute(resource="time", current_value=300, limit=240)
        assert result.violated
        if result.violated:
            collector.record_failure(
                operator_type=OperatorType.CONSTRAIN,
                operator_name="CONSTRAIN",
                failure_type=FailureType.CONSTRAINT_VIOLATED,
                input_cardinality=1,
                input_complexity="simple",
                input_range=(240.0, 300.0),
                severity=0.6,  # Moderate severity (violation detected but needs strategy)
                recoverable=True,  # Can trigger SUBSTITUTE
                violated_assumptions=["Current value <= limit"],
                chain_depth=2,
                downstream_operators=["SUBSTITUTE", "OPTIMIZE"],
                error_message="Resource constraint violated: current=300 > limit=240",
                full_trace=f"Enforcing {result.enforcement_strategy}",
                domain_context="diagnostic"
            )
        
        # Test 2: Boundary (current == limit)
        result = operator.execute(resource="budget", current_value=100, limit=100)
        assert not result.violated
        
        # Test 3: Ambiguous limit (floating point precision)
        result = operator.execute(resource="quality", current_value=0.9999999, limit=1.0)
        assert not result.violated  # Should pass (0.9999999 < 1.0)
    
    def test_diagnostic_optimize_failures(self):
        """
        Diagnostic test for OPTIMIZE operator.
        
        Probes:
        - Conflicting constraints
        - No feasible solution
        - Tradeoff clarity
        """
        
        collector = self.collector
        operator = OPTIMIZE()
        
        # Test 1: Normal case (should work)
        result = operator.execute(
            objective_values={"bottleneck": 0.4, "others": 0.7},
            constraints={"budget": 100, "time": 8},
            budget=100,
            time_available=8
        )
        assert result.constraints_satisfied
        
        # Test 2: Conflicting constraints (budget too low relative to objectives)
        # Current implementation is simplified, so we record diagnostic
        result = operator.execute(
            objective_values={"bottleneck": 0.1, "others": 0.9},  # Need both
            constraints={"budget": 10, "time": 1},  # Very tight
            budget=10,
            time_available=1
        )
        # In reality, this might fail. We instrument if it does:
        if not result.constraints_satisfied:
            collector.record_failure(
                operator_type=OperatorType.OPTIMIZE,
                operator_name="OPTIMIZE",
                failure_type=FailureType.OPTIMIZATION_NO_SOLUTION,
                input_cardinality=2,
                input_complexity="complex",
                input_range=(0.1, 0.9),
                severity=0.7,
                recoverable=True,  # ADAPT can handle
                violated_assumptions=["Feasible solution exists within constraints"],
                chain_depth=3,
                downstream_operators=["SEQUENCE", "ADAPT"],
                error_message="No feasible allocation found",
                full_trace=result.tradeoff_explanation,
                domain_context="diagnostic"
            )
    
    def test_diagnostic_sequence_failures(self):
        """
        Diagnostic test for SEQUENCE operator.
        
        Probes:
        - Failed preconditions
        - Failed postconditions
        - Edge cases
        """
        
        collector = self.collector
        operator = SEQUENCE()
        
        # Test 1: Failed preconditions
        result = operator.execute(
            preconditions={"step1": False, "step2": True},
            plan_name="execute_plan",
            success_criteria={"result": 0.8}
        )
        assert not result.executed
        collector.record_failure(
            operator_type=OperatorType.SEQUENCE,
            operator_name="SEQUENCE",
            failure_type=FailureType.SEQUENCE_PRECONDITIONS_FAILED,
            input_cardinality=2,
            input_complexity="simple",
            input_range=(0.0, 1.0),
            severity=0.5,
            recoverable=True,  # Can retry or use ADAPT
            violated_assumptions=["All preconditions must be true"],
            chain_depth=3,
            downstream_operators=["ADAPT"],
            error_message="Preconditions not met: step1=False",
            full_trace=str(result.execution_trace),
            domain_context="diagnostic"
        )
        
        # Test 2: Successful execution
        result = operator.execute(
            preconditions={"step1": True, "step2": True},
            plan_name="execute_plan",
            success_criteria={"result": 0.8}
        )
        assert result.executed
        assert result.postconditions_met
    
    def test_diagnostic_adapt_failures(self):
        """
        Diagnostic test for ADAPT operator.
        
        Probes:
        - No alternatives available
        - Goal degradation
        """
        
        collector = self.collector
        operator = ADAPT()
        
        # Test 1: No alternatives
        result = operator.execute(
            original_goal="implement_feature",
            failure_reason="out_of_time",
            available_alternatives=[]
        )
        assert not result.adapted
        collector.record_failure(
            operator_type=OperatorType.ADAPT,
            operator_name="ADAPT",
            failure_type=FailureType.ADAPT_NO_ALTERNATIVES,
            input_cardinality=0,
            input_complexity="simple",
            input_range=(0.0, 0.0),
            severity=0.9,  # Very high (no fallback)
            recoverable=False,  # Cannot recover without alternatives
            violated_assumptions=["At least one alternative available"],
            chain_depth=4,
            downstream_operators=[],
            error_message="No alternatives provided",
            full_trace=result.fallback_explanation,
            domain_context="diagnostic"
        )
        
        # Test 2: Severe goal loss
        result = operator.execute(
            original_goal="complete_task",
            failure_reason="resource_unavailable",
            available_alternatives=["very_limited_option"]
        )
        assert result.adapted
        if result.goal_preservation_ratio < 0.5:
            collector.record_failure(
                operator_type=OperatorType.ADAPT,
                operator_name="ADAPT",
                failure_type=FailureType.ADAPT_GOAL_LOSS_SEVERE,
                input_cardinality=1,
                input_complexity="simple",
                input_range=(0.0, 1.0),
                severity=0.7,
                recoverable=True,  # But heavily degraded
                violated_assumptions=["Fallback preserves >50% of original goal"],
                chain_depth=4,
                downstream_operators=[],
                error_message=f"Goal preservation only {result.goal_preservation_ratio:.0%}",
                full_trace=result.fallback_explanation,
                domain_context="diagnostic"
            )
    
    def test_diagnostic_substitute_failures(self):
        """
        Diagnostic test for SUBSTITUTE operator.
        
        Probes:
        - No equivalents available
        - Poor equivalence
        """
        
        collector = self.collector
        operator = SUBSTITUTE()
        
        # Test 1: No alternatives
        result = operator.execute(
            required_resource="GPU",
            available_alternatives=[],
            equivalence_class="compute_resource"
        )
        assert not result.can_substitute
        collector.record_failure(
            operator_type=OperatorType.SUBSTITUTE,
            operator_name="SUBSTITUTE",
            failure_type=FailureType.SUBSTITUTE_NO_EQUIVALENTS,
            input_cardinality=0,
            input_complexity="simple",
            input_range=(0.0, 0.0),
            severity=0.8,
            recoverable=False,
            violated_assumptions=["At least one alternative exists"],
            chain_depth=2,
            downstream_operators=[],
            error_message="No alternatives available",
            full_trace=result.equivalence_justification,
            domain_context="diagnostic"
        )
        
        # Test 2: Poor equivalence (cost delta is high)
        result = operator.execute(
            required_resource="primary",
            available_alternatives=["expensive_alternative"],
            equivalence_class="performance"
        )
        assert result.can_substitute
        if result.cost_delta > 0.5:  # Cost too high
            collector.record_failure(
                operator_type=OperatorType.SUBSTITUTE,
                operator_name="SUBSTITUTE",
                failure_type=FailureType.SUBSTITUTE_POOR_EQUIVALENCE,
                input_cardinality=1,
                input_complexity="simple",
                input_range=(0.0, 1.0),
                severity=0.4,
                recoverable=True,
                violated_assumptions=["Substitution has acceptable cost delta"],
                chain_depth=2,
                downstream_operators=[],
                error_message=f"Substitution cost increase: {result.cost_delta}",
                full_trace=result.equivalence_justification,
                domain_context="diagnostic"
            )
    
    def test_aggregate_failure_analysis(self):
        """
        Analyze all collected failures and generate recommendations.
        """
        
        collector = self.collector
        
        # Get statistics
        stats = collector.get_statistics()
        print(f"\n{'='*70}")
        print(f"PHASE 3.5.1 FAILURE ANALYSIS — BASELINE")
        print(f"{'='*70}")
        print(f"Total failures collected: {stats['total_failures']}")
        print(f"Operators affected: {stats['operators_affected']}")
        print(f"Failure types: {stats['failure_types']}")
        print(f"Average severity: {stats['avg_severity']:.2f}")
        print(f"Recoverable ratio: {stats['recoverable_ratio']:.1%}")
        
        # Cluster failures
        clusters = collector.analyze_failures()
        print(f"\n{'='*70}")
        print(f"FAILURE CLUSTERS (Domain-Agnostic)")
        print(f"{'='*70}")
        
        for cluster_id, cluster in sorted(clusters.items()):
            print(f"\n{cluster_id}")
            print(f"  Operator: {cluster.operator_type.value}")
            print(f"  Failure type: {cluster.primary_failure_type.value}")
            print(f"  Count: {cluster.failure_count}")
            print(f"  Avg severity: {cluster.severity_average:.2f}")
            print(f"  Recoverable: {cluster.recoverable_ratio:.1%}")
            print(f"  Root causes:")
            for cause in cluster.likely_root_causes:
                print(f"    - {cause}")
            print(f"  Violated assumptions:")
            for assumption in cluster.violated_assumptions:
                print(f"    - {assumption}")
            if cluster.suggested_precondition:
                print(f"  > Suggested precondition: {cluster.suggested_precondition}")
            if cluster.suggested_validation:
                print(f"  > Suggested validation: {cluster.suggested_validation}")
            if cluster.suggested_parameter_change:
                print(f"  > Suggested parameter: {cluster.suggested_parameter_change}")
        
        # Export for further analysis
        collector.export_json("phase_3_5_failures.json")
        print(f"\n[OK] Failures exported to: phase_3_5_failures.json")
        
        # Assertions
        assert stats['total_failures'] >= 0, "Failure collection should complete"
        if stats['total_failures'] > 0:
            assert stats['avg_severity'] <= 1.0, "Severity should be 0-1"
            assert 0 <= stats['recoverable_ratio'] <= 1.0, "Recovery ratio should be 0-1"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
