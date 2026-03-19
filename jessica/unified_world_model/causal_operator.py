"""
Minimal Causal Operator: DETECT_BOTTLENECK (domain-independent)

This operator identifies the lowest-throughput component in any system.
It requires ONLY:
  - A component inventory (list of named components)
  - A performance score for each (0-1 scale)
  - Optional: effect_on_total (relative impact multiplier)

All domain-specific knowledge is external; operator logic is invariant.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import time


@dataclass
class Component:
    """A single system component with performance score."""
    name: str
    throughput: float  # 0-1, where 1 is maximum performance
    effect_on_total: float = 1.0  # Relative importance (1.0 = equal weight)


@dataclass
class BottleneckResult:
    """Output of DETECT_BOTTLENECK operator."""
    bottleneck_component: str
    bottleneck_throughput: float
    severity_score: float  # 0-1, how much is this limiting?
    second_best_component: Optional[str]
    system_throughput_estimate: float  # Rough estimate of total system throughput
    improvement_potential: float  # If bottleneck is fixed, max system improvement
    trace: str  # Human-readable explanation
    domain_context: str


class DETECT_BOTTLENECK:
    """
    Domain-independent bottleneck detection.
    
    Invariant logic:
    - Bottleneck = component with lowest throughput weighted by effect_on_total
    - Severity = gap between bottleneck and next-best component
    - Improvement potential = (1 - bottleneck_throughput) * weighted_effect
    
    This logic applies identically whether components are:
    - Chess skills (opening, midgame, endgame, tactics)
    - Coding skills (syntax, debugging, design, systems)
    - Supply chain stages (fabrication, assembly, testing)
    - Medical systems (triage, diagnosis, treatment, recovery)
    """
    
    def __init__(self):
        self.last_execution = None
        self.execution_count = 0
    
    def execute(
        self,
        components: List[Component],
        domain_context: str = "unknown"
    ) -> BottleneckResult:
        """
        Execute bottleneck detection.
        
        Args:
            components: List of (name, throughput, effect_on_total) tuples
            domain_context: String describing domain (e.g., "chess", "coding")
        
        Returns:
            BottleneckResult with bottleneck identification and metrics
        """
        self.execution_count += 1
        self.last_execution = time.time()
        
        if not components:
            return BottleneckResult(
                bottleneck_component="<empty>",
                bottleneck_throughput=0.0,
                severity_score=0.0,
                second_best_component=None,
                system_throughput_estimate=0.0,
                improvement_potential=0.0,
                trace="No components provided",
                domain_context=domain_context
            )
        
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
        
        # Severity: gap between bottleneck and next-best (as % of next-best)
        if second_best_tp > 0:
            severity = (second_best_tp - bottleneck_tp) / second_best_tp
        else:
            severity = 1.0
        
        # System throughput: weighted average
        total_weight = sum(c[2] for c in scored)
        system_tp = sum(c[1] * c[2] for c in scored) / total_weight if total_weight > 0 else 0.0
        
        # Improvement potential: how much total throughput improves if bottleneck fixed
        if system_tp > 0:
            improvement_potential = (
                (system_tp - bottleneck_weighted) / system_tp
                if system_tp > 0 else 0.0
            )
        else:
            improvement_potential = bottleneck_effect
        
        trace = (
            f"Bottleneck: {bottleneck_name} (throughput={bottleneck_tp:.2f}). "
            f"Next-best: {second_best_name} (throughput={second_best_tp:.2f}). "
            f"Fixing {bottleneck_name} could improve system throughput by {improvement_potential:.1%}."
        )
        
        return BottleneckResult(
            bottleneck_component=bottleneck_name,
            bottleneck_throughput=bottleneck_tp,
            severity_score=severity,
            second_best_component=second_best_name,
            system_throughput_estimate=system_tp,
            improvement_potential=improvement_potential,
            trace=trace,
            domain_context=domain_context
        )


# Additional operators for composition

@dataclass
class ConstrainResult:
    """Output of CONSTRAIN operator."""
    resource_name: str
    limit_value: float
    violated: bool
    enforcement_strategy: str


class CONSTRAIN:
    """Apply hard limits to a resource."""
    
    def execute(self, resource: str, current_value: float, limit: float) -> ConstrainResult:
        """Enforce resource constraint."""
        violated = current_value > limit
        strategy = "truncate" if violated else "proceed"
        
        return ConstrainResult(
            resource_name=resource,
            limit_value=limit,
            violated=violated,
            enforcement_strategy=strategy
        )


@dataclass
class OptimizeResult:
    """Output of OPTIMIZE operator."""
    best_allocation: Dict[str, float]
    objective_value: float
    constraints_satisfied: bool
    tradeoff_explanation: str


class OPTIMIZE:
    """Choose best allocation within constraints."""
    
    def execute(
        self,
        objective_values: Dict[str, float],  # e.g., {"bottleneck": 0.4, "others": 0.7}
        constraints: Dict[str, float],  # e.g., {"budget": 100, "time": 8}
        budget: float,
        time_available: float
    ) -> OptimizeResult:
        """Allocate resources to maximize improvement of bottleneck."""
        # Greedy strategy: invest most in bottleneck
        bottleneck_allocation = budget * 0.6  # 60% to bottleneck
        other_allocation = budget * 0.4  # 40% to others
        
        # Simplified objective: improvement = allocation / (throughput_gap)
        bottleneck_improvement = bottleneck_allocation * (1 - 0.4) / 100
        
        return OptimizeResult(
            best_allocation={"bottleneck": bottleneck_allocation, "others": other_allocation},
            objective_value=bottleneck_improvement,
            constraints_satisfied=True,
            tradeoff_explanation="Prioritize bottleneck improvement; accept slower growth elsewhere"
        )


@dataclass
class SequenceResult:
    """Output of SEQUENCE operator."""
    executed: bool
    preconditions_met: bool
    postconditions_met: bool
    execution_trace: List[str]


class SEQUENCE:
    """Execute a plan if preconditions are met."""
    
    def execute(
        self,
        preconditions: Dict[str, bool],
        plan_name: str,
        success_criteria: Dict[str, float]
    ) -> SequenceResult:
        """Execute plan; verify preconditions and postconditions."""
        preconds_met = all(preconditions.values())
        
        if not preconds_met:
            return SequenceResult(
                executed=False,
                preconditions_met=False,
                postconditions_met=False,
                execution_trace=[f"Preconditions failed: {preconditions}"]
            )
        
        # Simulate execution
        trace = [f"Preconditions met: {preconditions}", f"Executing: {plan_name}"]
        
        # Assume plan execution succeeds (simplified)
        postconds_met = True
        
        return SequenceResult(
            executed=True,
            preconditions_met=True,
            postconditions_met=postconds_met,
            execution_trace=trace
        )


@dataclass
class AdaptResult:
    """Output of ADAPT operator."""
    adapted: bool
    new_plan: str
    goal_preservation_ratio: float
    fallback_explanation: str


class ADAPT:
    """Revise plan if execution fails."""
    
    def execute(
        self,
        original_goal: str,
        failure_reason: str,
        available_alternatives: List[str]
    ) -> AdaptResult:
        """Generate fallback plan if original fails."""
        if not available_alternatives:
            return AdaptResult(
                adapted=False,
                new_plan="none",
                goal_preservation_ratio=0.0,
                fallback_explanation="No alternatives available"
            )
        
        # Pick first alternative
        new_plan = available_alternatives[0]
        
        return AdaptResult(
            adapted=True,
            new_plan=new_plan,
            goal_preservation_ratio=0.7,  # Degraded but viable
            fallback_explanation=f"Original plan failed ({failure_reason}); switching to {new_plan}"
        )


@dataclass
class SubstituteResult:
    """Output of SUBSTITUTE operator."""
    can_substitute: bool
    cost_delta: float
    equivalence_justification: str


class SUBSTITUTE:
    """Find alternative resources with equivalent effect."""
    
    def execute(
        self,
        required_resource: str,
        available_alternatives: List[str],
        equivalence_class: str
    ) -> SubstituteResult:
        """Check if alternative resource can substitute."""
        if not available_alternatives:
            return SubstituteResult(
                can_substitute=False,
                cost_delta=float('inf'),
                equivalence_justification="No alternatives available"
            )
        
        # Simplified: assume first alternative is viable
        return SubstituteResult(
            can_substitute=True,
            cost_delta=-0.1,  # Slight cost saving
            equivalence_justification=f"{available_alternatives[0]} is equivalent in {equivalence_class}"
        )


# Singletons
detect_bottleneck_operator = DETECT_BOTTLENECK()
constrain_operator = CONSTRAIN()
optimize_operator = OPTIMIZE()
sequence_operator = SEQUENCE()
adapt_operator = ADAPT()
substitute_operator = SUBSTITUTE()
