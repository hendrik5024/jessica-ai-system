"""
Phase 3.5 Experiment 3.5.2: Operator Refinement — DETECT_BOTTLENECK

REFINEMENT: Enhanced Empty Input Handling + Ambiguity Detection

RATIONALE:
  - Exp 3.5.1 identified 2 failure patterns in DETECT_BOTTLENECK:
    1. Empty input (severity 0.80) - no precondition check
    2. Ambiguous bottlenecks (severity 0.30) - no ambiguity flag

CHANGES:
  1. Add empty input precondition check (fail fast)
  2. Add ambiguity detection (flag equal throughputs)
  3. Enhanced trace logging
  4. New output field: ambiguity_detected (bool)

CONSTRAINTS:
  ✅ No new operators
  ✅ No domain-specific logic
  ✅ No learned parameters
  ✅ All changes fully explainable
  ✅ 100% backward compatible with valid inputs
  ❌ Empty inputs now caught earlier (earlier detection)

EXPECTED IMPROVEMENT:
  - Failure rate: 50% reduction on empty input cases
  - Ambiguity detection: 100% of equal-throughput cases flagged
  - Cross-domain: Improvement should transfer universally (structural fix)

ROLLBACK PLAN:
  - Replace refined operator with original
  - Revert causal_operator.py to Phase 3 state
  - Re-run regression tests
  - Expected restore time: <5 minutes
"""

from dataclasses import dataclass
from typing import List, Optional
import time


@dataclass
class Component:
    """A single system component with performance score."""
    name: str
    throughput: float  # 0-1, where 1 is maximum performance
    effect_on_total: float = 1.0  # Relative importance (1.0 = equal weight)


@dataclass
class BottleneckResult_Refined:
    """Output of refined DETECT_BOTTLENECK operator."""
    bottleneck_component: str
    bottleneck_throughput: float
    severity_score: float  # 0-1, how much is this limiting?
    second_best_component: Optional[str]
    system_throughput_estimate: float  # Rough estimate of total system throughput
    improvement_potential: float  # If bottleneck is fixed, max system improvement
    trace: str  # Human-readable explanation
    domain_context: str
    
    # REFINEMENT ADDITIONS
    ambiguity_detected: bool = False  # True if multiple components tied as bottleneck
    ambiguity_tolerance: float = 0.05  # Threshold: throughput difference < 5% = ambiguous
    empty_input_handled: bool = False  # True if input was empty (caught by precondition)


class DETECT_BOTTLENECK_REFINED:
    """
    REFINED: Domain-independent bottleneck detection with enhanced validation.
    
    CHANGES FROM ORIGINAL:
    1. Precondition check: Empty input detection (fail fast)
    2. Ambiguity detection: Flag when multiple components tied as bottleneck
    3. Enhanced tracing: Clear explanation of edge cases
    
    CORE LOGIC UNCHANGED: Bottleneck detection algorithm identical
    
    Invariant logic (unchanged):
    - Bottleneck = component with lowest throughput weighted by effect_on_total
    - Severity = gap between bottleneck and next-best component
    - Improvement potential = (1 - bottleneck_throughput) * weighted_effect
    
    Enhanced logic (new):
    - Ambiguity = multiple components with equal weighted throughput (diff < 5%)
    - Empty check = return early with clear indication if no components
    """
    
    def __init__(self):
        self.last_execution = None
        self.execution_count = 0
    
    def execute(
        self,
        components: List[Component],
        domain_context: str = "unknown"
    ) -> BottleneckResult_Refined:
        """
        Execute refined bottleneck detection with enhanced validation.
        
        PRECONDITION CHECK (new):
        - If components list is empty, return early with empty_input_handled=True
        - Downstream operators must handle empty state explicitly
        
        Args:
            components: List of (name, throughput, effect_on_total) tuples
            domain_context: String describing domain (e.g., "chess", "coding")
        
        Returns:
            BottleneckResult_Refined with optional ambiguity and empty-input flags
        """
        self.execution_count += 1
        self.last_execution = time.time()
        
        # PRECONDITION CHECK (REFINEMENT #1)
        # Fail fast if empty input detected
        if not components:
            return BottleneckResult_Refined(
                bottleneck_component="<empty>",
                bottleneck_throughput=0.0,
                severity_score=0.0,
                second_best_component=None,
                system_throughput_estimate=0.0,
                improvement_potential=0.0,
                trace="[PRECONDITION FAILURE] Empty component list provided. Upstream should validate input before calling DETECT.",
                domain_context=domain_context,
                ambiguity_detected=False,
                empty_input_handled=True  # NEW: Flag that empty input was caught
            )
        
        # Core logic (identical to original)
        # Sort by weighted throughput
        scored = [
            (c.name, c.throughput, c.effect_on_total, c.throughput * c.effect_on_total)
            for c in components
        ]
        scored.sort(key=lambda x: x[3])  # Sort by weighted score (ascending)
        
        bottleneck_name, bottleneck_tp, bottleneck_effect, bottleneck_weighted = scored[0]
        
        # Second-best for comparison
        second_best_name = scored[1][0] if len(scored) > 1 else None
        second_best_tp = scored[1][1] if len(scored) > 1 else 1.0
        second_best_weighted = scored[1][3] if len(scored) > 1 else 1.0
        
        # Severity: gap between bottleneck and next-best (as % of next-best)
        if second_best_tp > 0:
            severity = (second_best_tp - bottleneck_tp) / second_best_tp
        else:
            severity = 1.0
        
        # System throughput: weighted average
        total_weight = sum(c[2] for c in scored)
        system_tp = sum(c[1] * c[2] for c in scored) / total_weight if total_weight > 0 else 0.0
        
        # Improvement potential
        if system_tp > 0:
            improvement_potential = (
                (system_tp - bottleneck_weighted) / system_tp
                if system_tp > 0 else 0.0
            )
        else:
            improvement_potential = bottleneck_effect
        
        # AMBIGUITY DETECTION (REFINEMENT #2)
        # Check if multiple components tied as bottleneck (throughput difference < 5%)
        ambiguity_tolerance = 0.05
        ambiguity_detected = False
        ambiguous_components = [bottleneck_name]
        
        if len(scored) > 1:
            # Check how many components are within tolerance of bottleneck
            for name, tp, effect, weighted in scored[1:]:
                throughput_diff = tp - bottleneck_tp
                if throughput_diff < ambiguity_tolerance:
                    ambiguous_components.append(name)
                    ambiguity_detected = True
                else:
                    break  # Sorted, so can stop after first non-ambiguous
        
        # Build trace with optional ambiguity note
        trace_base = (
            f"Bottleneck: {bottleneck_name} (throughput={bottleneck_tp:.2f}). "
            f"Next-best: {second_best_name} (throughput={second_best_tp:.2f}). "
            f"Fixing {bottleneck_name} could improve system throughput by {improvement_potential:.1%}."
        )
        
        if ambiguity_detected:
            trace_ambiguity = (
                f" [AMBIGUITY DETECTED] Components tied as bottleneck (diff < {ambiguity_tolerance:.0%}): "
                f"{', '.join(ambiguous_components)}. Downstream should break ties or reconsider problem structure."
            )
            trace = trace_base + trace_ambiguity
        else:
            trace = trace_base
        
        return BottleneckResult_Refined(
            bottleneck_component=bottleneck_name,
            bottleneck_throughput=bottleneck_tp,
            severity_score=severity,
            second_best_component=second_best_name,
            system_throughput_estimate=system_tp,
            improvement_potential=improvement_potential,
            trace=trace,
            domain_context=domain_context,
            ambiguity_detected=ambiguity_detected,  # NEW: Flag ambiguous cases
            ambiguity_tolerance=ambiguity_tolerance,
            empty_input_handled=False
        )


# Singleton instance
detect_bottleneck_refined_operator = DETECT_BOTTLENECK_REFINED()

