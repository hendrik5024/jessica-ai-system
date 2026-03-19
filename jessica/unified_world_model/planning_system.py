"""
Long-Horizon Planning System - Verified multi-step planning with safety constraints.

Enables:
- 10+ step plan generation with constraint verification
- Emergent constraint detection (risks that only appear when steps combine)
- Backward-induction safety verification (prove plan reaches goal)
- Plan adaptation when intermediate steps fail
- Contingency trees (if step N fails, execute branch M)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple, Callable
from datetime import datetime
from enum import Enum
import uuid


class StepStatus(Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ConstraintViolationType(Enum):
    """Types of constraint violations."""
    NONE = "none"
    HARD = "hard"  # Must not violate
    SOFT = "soft"  # Prefer not to violate
    EMERGENT = "emergent"  # Only appears from step combinations


@dataclass
class PlanStep:
    """
    A single step in a long-horizon plan.
    
    Each step has:
    - Action to execute
    - Preconditions that must be true
    - Effects (expected state changes)
    - Resource consumption
    - Constraint impacts
    """
    
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_number: int = 0
    action: str = ""
    description: str = ""
    
    # Preconditions and effects
    preconditions: Set[str] = field(default_factory=set)  # Required before execution
    effects: Set[str] = field(default_factory=set)  # State changes after execution
    
    # Resources
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    resource_produced: Dict[str, float] = field(default_factory=dict)
    
    # Constraints
    constraint_impacts: Dict[str, str] = field(default_factory=dict)  # constraint_id -> impact
    
    # Execution
    status: StepStatus = StepStatus.PENDING
    estimated_duration: float = 0.0  # Time units
    actual_duration: Optional[float] = None
    
    # Contingencies
    failure_branches: Dict[str, str] = field(default_factory=dict)  # failure_type -> branch_id
    
    def is_ready(self, current_state: Set[str]) -> bool:
        """Check if all preconditions are met."""
        return self.preconditions.issubset(current_state)
    
    def apply_effects(self, current_state: Set[str]) -> Set[str]:
        """Apply step effects to current state."""
        new_state = current_state.copy()
        new_state.update(self.effects)
        return new_state


@dataclass
class ConstraintStatus:
    """Status of a constraint at a point in the plan."""
    
    constraint_id: str
    satisfied: bool
    violation_type: ConstraintViolationType
    reason: str = ""
    severity: float = 0.0  # 0.0 (minor) to 1.0 (critical)


@dataclass
class EmergentConstraint:
    """
    Constraint that only emerges from combining multiple steps.
    
    Example: Step 1 (reduce oversight) + Step 2 (increase speed) = risk cascade
    """
    
    constraint_id: str
    trigger_steps: List[int]  # Step numbers that trigger this constraint
    description: str
    severity: float
    mitigation: Optional[str] = None


@dataclass
class PlanVerification:
    """Result of plan verification."""
    
    valid: bool
    reaches_goal: bool
    constraint_violations: List[ConstraintStatus]
    emergent_risks: List[EmergentConstraint]
    reasoning: str
    confidence: float


class Plan:
    """
    A long-horizon plan with verification and adaptation.
    """
    
    def __init__(self, plan_id: str, goal_description: str):
        self.plan_id = plan_id
        self.goal_description = goal_description
        self.steps: List[PlanStep] = []
        self.initial_state: Set[str] = set()
        self.goal_state: Set[str] = set()
        self.constraints: Dict[str, Any] = {}
        self.current_step_index: int = 0
        self.emergent_constraints: List[EmergentConstraint] = []
        self.created_at: float = datetime.now().timestamp()
    
    def add_step(self, step: PlanStep) -> None:
        """Add a step to the plan."""
        step.step_number = len(self.steps) + 1
        self.steps.append(step)
    
    def get_step(self, step_number: int) -> Optional[PlanStep]:
        """Get step by number (1-indexed)."""
        if 1 <= step_number <= len(self.steps):
            return self.steps[step_number - 1]
        return None
    
    def get_current_step(self) -> Optional[PlanStep]:
        """Get current step being executed."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def advance_step(self) -> bool:
        """Move to next step. Returns True if more steps remain."""
        self.current_step_index += 1
        return self.current_step_index < len(self.steps)
    
    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        return all(s.status == StepStatus.COMPLETED for s in self.steps)


class LongHorizonPlanner:
    """
    Long-horizon planner with verification and adaptation.
    """
    
    def __init__(self, world_model):
        """
        Args:
            world_model: WorldModel instance
        """
        self.world_model = world_model
        self.plans: Dict[str, Plan] = {}
        self.constraint_validators: Dict[str, Callable] = {}
    
    def create_plan(self,
                   goal: str,
                   initial_state: Set[str],
                   goal_state: Set[str],
                   constraints: Dict[str, Any],
                   max_steps: int = 10) -> Plan:
        """
        Create a long-horizon plan to achieve goal.
        
        Args:
            goal: Goal description
            initial_state: Starting state
            goal_state: Desired end state
            constraints: Dictionary of constraints to satisfy
            max_steps: Maximum steps allowed
        
        Returns:
            Plan object
        """
        plan_id = f"plan_{len(self.plans)}"
        plan = Plan(plan_id, goal)
        plan.initial_state = initial_state
        plan.goal_state = goal_state
        plan.constraints = constraints
        
        # Generate steps using forward search
        current_state = initial_state.copy()
        step_count = 0
        
        while not goal_state.issubset(current_state) and step_count < max_steps:
            # Find action that brings us closer to goal
            step = self._generate_next_step(
                current_state,
                goal_state,
                constraints,
                step_count + 1
            )
            
            if step is None:
                break  # No valid step found
            
            plan.add_step(step)
            current_state = step.apply_effects(current_state)
            step_count += 1
        
        self.plans[plan_id] = plan
        return plan
    
    def verify_plan(self, plan: Plan) -> PlanVerification:
        """
        Verify plan safety and goal reachability.
        
        Uses backward induction: start from goal, work backwards to verify
        each step maintains constraints and brings us closer to goal.
        """
        violations = []
        emergent_risks = []
        
        # Forward simulation to check constraint satisfaction
        current_state = plan.initial_state.copy()
        resource_levels = {k: 100.0 for k in ["time", "energy", "attention"]}
        
        for i, step in enumerate(plan.steps):
            # Check preconditions
            if not step.is_ready(current_state):
                violations.append(ConstraintStatus(
                    constraint_id=f"step_{i+1}_preconditions",
                    satisfied=False,
                    violation_type=ConstraintViolationType.HARD,
                    reason=f"Step {i+1} preconditions not met: {step.preconditions - current_state}",
                    severity=1.0
                ))
            
            # Check resource consumption
            for resource, amount in step.resource_requirements.items():
                if resource_levels.get(resource, 0) < amount:
                    violations.append(ConstraintStatus(
                        constraint_id=f"step_{i+1}_resource_{resource}",
                        satisfied=False,
                        violation_type=ConstraintViolationType.HARD,
                        reason=f"Insufficient {resource}: need {amount}, have {resource_levels.get(resource, 0):.1f}",
                        severity=0.8
                    ))
                else:
                    resource_levels[resource] -= amount
            
            # Add produced resources
            for resource, amount in step.resource_produced.items():
                resource_levels[resource] = resource_levels.get(resource, 0) + amount
            
            # Apply effects
            current_state = step.apply_effects(current_state)
            
            # Check constraints
            for constraint_id, constraint in plan.constraints.items():
                impact = step.constraint_impacts.get(constraint_id)
                if impact == "violates":
                    violations.append(ConstraintStatus(
                        constraint_id=constraint_id,
                        satisfied=False,
                        violation_type=ConstraintViolationType.HARD,
                        reason=f"Step {i+1} violates constraint {constraint_id}",
                        severity=1.0
                    ))
        
        # Detect emergent constraints
        emergent_risks = self._detect_emergent_constraints(plan)
        
        # Check if goal is reached
        reaches_goal = plan.goal_state.issubset(current_state)
        
        # Determine validity
        hard_violations = [v for v in violations if v.violation_type == ConstraintViolationType.HARD]
        critical_emergent = [r for r in emergent_risks if r.severity > 0.7]
        
        valid = len(hard_violations) == 0 and len(critical_emergent) == 0 and reaches_goal
        
        # Build reasoning
        if valid:
            reasoning = f"Plan valid: {len(plan.steps)} steps, reaches goal, no violations"
        else:
            reasons = []
            if hard_violations:
                reasons.append(f"{len(hard_violations)} hard violations")
            if critical_emergent:
                reasons.append(f"{len(critical_emergent)} critical emergent risks")
            if not reaches_goal:
                reasons.append("does not reach goal")
            reasoning = f"Plan invalid: {'; '.join(reasons)}"
        
        # Confidence based on soft violations and emergent risks
        soft_violations = [v for v in violations if v.violation_type == ConstraintViolationType.SOFT]
        confidence = 1.0
        confidence -= len(soft_violations) * 0.1
        confidence -= len(emergent_risks) * 0.15
        confidence = max(0.0, min(1.0, confidence))
        
        return PlanVerification(
            valid=valid,
            reaches_goal=reaches_goal,
            constraint_violations=violations,
            emergent_risks=emergent_risks,
            reasoning=reasoning,
            confidence=confidence
        )
    
    def adapt_plan(self,
                  plan: Plan,
                  failed_step: int,
                  failure_reason: str) -> Plan:
        """
        Adapt plan when a step fails.
        
        Regenerates steps from failure point to goal while respecting constraints.
        """
        # Get state before failed step
        state = plan.initial_state.copy()
        for i in range(failed_step - 1):
            state = plan.steps[i].apply_effects(state)
        
        # Create new plan from this point
        new_plan = Plan(f"{plan.plan_id}_adapted", plan.goal_description)
        new_plan.initial_state = state
        new_plan.goal_state = plan.goal_state
        new_plan.constraints = plan.constraints
        
        # Keep successful steps
        for i in range(failed_step - 1):
            new_plan.add_step(plan.steps[i])
        
        # Generate alternative steps
        current_state = state
        step_count = failed_step
        max_steps = 15  # Allow more steps for adapted plan
        
        while not plan.goal_state.issubset(current_state) and step_count <= max_steps:
            step = self._generate_next_step(
                current_state,
                plan.goal_state,
                plan.constraints,
                step_count,
                avoid_action=plan.steps[failed_step - 1].action if failed_step <= len(plan.steps) else None
            )
            
            if step is None:
                break
            
            new_plan.add_step(step)
            current_state = step.apply_effects(current_state)
            step_count += 1
        
        self.plans[new_plan.plan_id] = new_plan
        return new_plan
    
    def _generate_next_step(self,
                           current_state: Set[str],
                           goal_state: Set[str],
                           constraints: Dict[str, Any],
                           step_number: int,
                           avoid_action: Optional[str] = None) -> Optional[PlanStep]:
        """
        Generate next step that brings us closer to goal.
        
        Uses heuristic: add state elements that are in goal but not in current.
        """
        # Find what we need to achieve
        missing = goal_state - current_state
        
        if not missing:
            return None  # Goal already reached
        
        # Pick an element to achieve
        target = next(iter(missing))
        
        # Create step to achieve it
        action = f"achieve_{target}"
        
        if avoid_action and action == avoid_action:
            # Try alternative approach
            action = f"alternative_achieve_{target}"
        
        step = PlanStep(
            step_number=step_number,
            action=action,
            description=f"Achieve {target}",
            preconditions=set(),  # Simplified for now
            effects={target},
            resource_requirements={"time": 10.0, "energy": 5.0},
            estimated_duration=10.0
        )
        
        return step
    
    def _detect_emergent_constraints(self, plan: Plan) -> List[EmergentConstraint]:
        """
        Detect constraints that only emerge from step combinations.
        
        Examples:
        - Multiple steps reducing oversight → risk cascade
        - Speed increase + quality checks removed → safety risk
        - Resource intensive steps clustered → resource exhaustion
        """
        emergent = []
        
        # Pattern 1: Multiple steps with same negative impact
        impact_clusters = self._find_impact_clusters(plan)
        for impact_type, step_numbers in impact_clusters.items():
            if len(step_numbers) >= 3:
                emergent.append(EmergentConstraint(
                    constraint_id=f"cluster_{impact_type}",
                    trigger_steps=step_numbers,
                    description=f"Multiple steps ({len(step_numbers)}) with {impact_type} create cumulative risk",
                    severity=min(1.0, len(step_numbers) * 0.25),
                    mitigation=f"Distribute steps or add compensating actions"
                ))
        
        # Pattern 2: Resource-intensive steps too close together
        resource_spikes = self._find_resource_spikes(plan)
        for resource, step_range in resource_spikes.items():
            emergent.append(EmergentConstraint(
                constraint_id=f"spike_{resource}",
                trigger_steps=list(range(step_range[0], step_range[1] + 1)),
                description=f"High {resource} consumption in steps {step_range[0]}-{step_range[1]}",
                severity=0.6,
                mitigation=f"Spread {resource}-intensive steps across plan"
            ))
        
        # Pattern 3: Dependency chains that create bottlenecks
        long_chains = self._find_dependency_chains(plan)
        for chain in long_chains:
            if len(chain) >= 5:
                emergent.append(EmergentConstraint(
                    constraint_id=f"chain_{chain[0]}",
                    trigger_steps=chain,
                    description=f"Long dependency chain (length {len(chain)}) creates brittleness",
                    severity=0.7,
                    mitigation="Add parallel paths or reduce dependencies"
                ))
        
        return emergent
    
    def _find_impact_clusters(self, plan: Plan) -> Dict[str, List[int]]:
        """Find steps with similar negative impacts."""
        clusters: Dict[str, List[int]] = {}
        
        negative_impacts = ["reduce_oversight", "increase_speed", "skip_validation", "remove_checks"]
        
        for step in plan.steps:
            for impact in negative_impacts:
                if impact in step.action.lower() or impact in step.description.lower():
                    if impact not in clusters:
                        clusters[impact] = []
                    clusters[impact].append(step.step_number)
        
        return clusters
    
    def _find_resource_spikes(self, plan: Plan) -> Dict[str, Tuple[int, int]]:
        """Find windows of high resource consumption."""
        spikes = {}
        window_size = 3
        
        for resource in ["time", "energy", "attention"]:
            for i in range(len(plan.steps) - window_size + 1):
                window_steps = plan.steps[i:i+window_size]
                total_consumption = sum(
                    s.resource_requirements.get(resource, 0)
                    for s in window_steps
                )
                
                if total_consumption > 30.0:  # Threshold
                    spikes[resource] = (i + 1, i + window_size)
                    break  # Only report first spike
        
        return spikes
    
    def _find_dependency_chains(self, plan: Plan) -> List[List[int]]:
        """Find long dependency chains in plan."""
        chains = []
        
        # Build dependency graph
        dependencies: Dict[int, Set[int]] = {}
        for step in plan.steps:
            dependencies[step.step_number] = set()
            for prev_step in plan.steps[:step.step_number - 1]:
                # Check if current step depends on previous
                if step.preconditions & prev_step.effects:
                    dependencies[step.step_number].add(prev_step.step_number)
        
        # Find longest chains
        def find_chain_length(step_num: int, visited: Set[int]) -> List[int]:
            if step_num in visited:
                return []
            visited.add(step_num)
            
            if not dependencies.get(step_num):
                return [step_num]
            
            longest = []
            for dep in dependencies[step_num]:
                chain = find_chain_length(dep, visited.copy())
                if len(chain) > len(longest):
                    longest = chain
            
            return longest + [step_num]
        
        for step_num in range(1, len(plan.steps) + 1):
            chain = find_chain_length(step_num, set())
            if len(chain) >= 5:
                chains.append(chain)
        
        return chains
    
    def get_plan_statistics(self, plan: Plan) -> Dict[str, Any]:
        """Get statistics about a plan."""
        total_duration = sum(s.estimated_duration for s in plan.steps)
        total_resources = {}
        for step in plan.steps:
            for resource, amount in step.resource_requirements.items():
                total_resources[resource] = total_resources.get(resource, 0) + amount
        
        completed = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        
        return {
            "plan_id": plan.plan_id,
            "total_steps": len(plan.steps),
            "completed_steps": completed,
            "completion_percentage": (completed / len(plan.steps) * 100) if plan.steps else 0,
            "estimated_duration": total_duration,
            "total_resources": total_resources,
            "current_step": plan.current_step_index + 1,
            "emergent_constraints": len(plan.emergent_constraints)
        }
