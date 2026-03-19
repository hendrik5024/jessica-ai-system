"""
AGI Evaluation Harness - Distinguishes narrow AI from generally intelligent systems.

Tests require:
- Cross-domain transfer (explicit pattern mapping)
- Multi-step planning (≥10 steps with dependencies)
- Adaptation to failure (plan revision within 1-2 steps)
- Explanation of reasoning (causal chains, not narratives)

Each task includes automatic failure injection and scoring against thresholds.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid
from datetime import datetime


class FailureType(Enum):
    """Types of failures that can be injected."""
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    CONSTRAINT_CHANGE = "constraint_change"
    UNEXPECTED_OUTCOME = "unexpected_outcome"
    TIMING_VIOLATION = "timing_violation"
    ASSUMPTION_INVALIDATED = "assumption_invalidated"


class ScoringDimension(Enum):
    """Dimensions for evaluating general intelligence."""
    CROSS_DOMAIN_TRANSFER = "cross_domain_transfer"
    MULTI_STEP_PLANNING = "multi_step_planning"
    ADAPTATION_TO_FAILURE = "adaptation_to_failure"
    EXPLANATION_QUALITY = "explanation_quality"


@dataclass
class FailureInjection:
    """A failure to inject during task execution."""
    failure_id: str
    failure_type: FailureType
    step_number: int
    description: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainMapping:
    """Explicit mapping between source and target domain concepts."""
    source_domain: str
    target_domain: str
    source_concept: str
    target_concept: str
    causal_justification: str
    confidence: float


@dataclass
class EvaluationPlanStep:
    """A step in a multi-step plan for evaluation tasks."""
    step_id: str
    step_number: int
    action: str
    preconditions: List[str]
    effects: List[str]
    resources_required: List[str]
    dependencies: List[str]  # step_ids that must complete first


@dataclass
class CausalExplanation:
    """Causal explanation for a decision or plan."""
    decision: str
    causal_chain: List[str]  # sequence of cause→effect
    tradeoffs: List[str]
    counterfactuals: List[str]  # "if not X, then Y"
    confidence: float


@dataclass
class TaskResponse:
    """Response from a system attempting an evaluation task."""
    task_id: str
    plan: List[EvaluationPlanStep]
    domain_mappings: List[DomainMapping]
    explanation: CausalExplanation
    adaptation_steps: List[EvaluationPlanStep] = field(default_factory=list)  # after failure
    adaptation_time_ms: float = 0.0


@dataclass
class EvaluationScore:
    """Scores across all dimensions."""
    cross_domain_transfer: float  # 0-1
    multi_step_planning: float  # 0-1
    adaptation_to_failure: float  # 0-1
    explanation_quality: float  # 0-1
    overall: float  # 0-1
    passed: bool
    reasoning: Dict[str, str]


@dataclass
class EvaluationTask:
    """An evaluation task."""
    task_id: str
    title: str
    description: str
    domains_required: List[str]
    constraints: List[str]
    goal: str
    failure_injection: FailureInjection
    success_criteria: Dict[str, Any]
    minimum_steps: int = 10


class AGIEvaluationScorer:
    """Scores task responses against AGI criteria."""
    
    def __init__(self):
        self.thresholds = {
            ScoringDimension.CROSS_DOMAIN_TRANSFER: 0.7,
            ScoringDimension.MULTI_STEP_PLANNING: 0.8,
            ScoringDimension.ADAPTATION_TO_FAILURE: 0.75,
            ScoringDimension.EXPLANATION_QUALITY: 0.7
        }
    
    def score_cross_domain_transfer(self, response: TaskResponse, task: EvaluationTask) -> float:
        """Score quality of cross-domain transfer."""
        mappings = response.domain_mappings
        
        if not mappings:
            return 0.0
        
        # Check for explicit mappings between required domains
        domains_covered = set(m.source_domain for m in mappings) | set(m.target_domain for m in mappings)
        coverage = len(domains_covered & set(task.domains_required)) / len(task.domains_required)
        
        # Check for causal justifications
        justified = sum(1 for m in mappings if len(m.causal_justification) > 20) / len(mappings)
        
        # Check confidence
        avg_confidence = sum(m.confidence for m in mappings) / len(mappings)
        
        return (coverage * 0.5) + (justified * 0.3) + (avg_confidence * 0.2)
    
    def score_multi_step_planning(self, response: TaskResponse, task: EvaluationTask) -> float:
        """Score quality of multi-step planning."""
        plan = response.plan
        
        if not plan:
            return 0.0
        
        # Check step count
        step_count_score = min(1.0, len(plan) / task.minimum_steps)
        
        # Check dependencies
        has_dependencies = sum(1 for s in plan if s.dependencies) / max(1, len(plan))
        
        # Check preconditions and effects
        has_preconditions = sum(1 for s in plan if s.preconditions) / max(1, len(plan))
        has_effects = sum(1 for s in plan if s.effects) / max(1, len(plan))
        
        # Check constraint satisfaction
        constraint_violations = self._check_constraints(plan, task.constraints)
        constraint_score = max(0.0, 1.0 - (constraint_violations * 0.2))
        
        return (step_count_score * 0.3) + (has_dependencies * 0.2) + \
               (has_preconditions * 0.15) + (has_effects * 0.15) + (constraint_score * 0.2)
    
    def score_adaptation_to_failure(self, response: TaskResponse, task: EvaluationTask) -> float:
        """Score quality of adaptation after failure injection."""
        if not response.adaptation_steps:
            return 0.0
        
        # Check adaptation speed
        speed_score = 1.0 if response.adaptation_time_ms < 2000 else \
                     0.5 if response.adaptation_time_ms < 5000 else 0.2
        
        # Check if adaptation preserves constraints
        constraint_violations = self._check_constraints(
            response.adaptation_steps, 
            task.constraints
        )
        constraint_score = max(0.0, 1.0 - (constraint_violations * 0.3))
        
        # Check if adaptation addresses failure
        addresses_failure = self._check_failure_addressed(
            response.adaptation_steps,
            task.failure_injection
        )
        
        # Check if original goal still achievable
        goal_preserved = len(response.adaptation_steps) >= task.minimum_steps * 0.7
        
        return (speed_score * 0.25) + (constraint_score * 0.25) + \
               (addresses_failure * 0.3) + (goal_preserved * 0.2)
    
    def score_explanation_quality(self, response: TaskResponse, task: EvaluationTask) -> float:
        """Score quality of causal explanation."""
        explanation = response.explanation
        
        if not explanation:
            return 0.0
        
        # Check causal chain depth
        chain_score = min(1.0, len(explanation.causal_chain) / 5)
        
        # Check tradeoffs identified
        tradeoff_score = min(1.0, len(explanation.tradeoffs) / 3)
        
        # Check counterfactuals
        counterfactual_score = min(1.0, len(explanation.counterfactuals) / 2)
        
        # Check confidence calibration
        confidence_score = explanation.confidence
        
        return (chain_score * 0.3) + (tradeoff_score * 0.25) + \
               (counterfactual_score * 0.25) + (confidence_score * 0.2)
    
    def _check_constraints(self, steps: List[EvaluationPlanStep], constraints: List[str]) -> int:
        """Count constraint violations (simplified)."""
        violations = 0
        
        # Check resource constraints
        resource_usage = {}
        for step in steps:
            for resource in step.resources_required:
                resource_usage[resource] = resource_usage.get(resource, 0) + 1
        
        # Simple heuristic: if resource used more than 5 times, might be violation
        for resource, count in resource_usage.items():
            if count > 5:
                violations += 1
        
        return violations
    
    def _check_failure_addressed(self, steps: List[EvaluationPlanStep], failure: FailureInjection) -> float:
        """Check if adaptation addresses the failure."""
        # Check if plan mentions failure context
        failure_keywords = failure.description.lower().split()
        
        mentions = 0
        for step in steps:
            step_text = (step.action + " ".join(step.preconditions) + " ".join(step.effects)).lower()
            if any(kw in step_text for kw in failure_keywords):
                mentions += 1
        
        return min(1.0, mentions / 2)
    
    def evaluate(self, response: TaskResponse, task: EvaluationTask) -> EvaluationScore:
        """Full evaluation across all dimensions."""
        scores = {
            ScoringDimension.CROSS_DOMAIN_TRANSFER: self.score_cross_domain_transfer(response, task),
            ScoringDimension.MULTI_STEP_PLANNING: self.score_multi_step_planning(response, task),
            ScoringDimension.ADAPTATION_TO_FAILURE: self.score_adaptation_to_failure(response, task),
            ScoringDimension.EXPLANATION_QUALITY: self.score_explanation_quality(response, task)
        }
        
        overall = sum(scores.values()) / len(scores)
        
        passed = all(scores[dim] >= self.thresholds[dim] for dim in scores)
        
        reasoning = {}
        for dim, score in scores.items():
            threshold = self.thresholds[dim]
            status = "PASS" if score >= threshold else "FAIL"
            reasoning[dim.value] = f"{status}: {score:.2f} (threshold: {threshold:.2f})"
        
        return EvaluationScore(
            cross_domain_transfer=scores[ScoringDimension.CROSS_DOMAIN_TRANSFER],
            multi_step_planning=scores[ScoringDimension.MULTI_STEP_PLANNING],
            adaptation_to_failure=scores[ScoringDimension.ADAPTATION_TO_FAILURE],
            explanation_quality=scores[ScoringDimension.EXPLANATION_QUALITY],
            overall=overall,
            passed=passed,
            reasoning=reasoning
        )


class AGIEvaluationHarness:
    """Main test harness for AGI evaluation tasks."""
    
    def __init__(self, world_model):
        self.world_model = world_model
        self.scorer = AGIEvaluationScorer()
        self.tasks = self._initialize_tasks()
    
    def _initialize_tasks(self) -> List[EvaluationTask]:
        """Initialize the 10 evaluation tasks."""
        return [
            EvaluationTask(
                task_id="task_1_emergency_logistics",
                title="Emergency Logistics + Negotiation + Resource Scheduling",
                description="Plan 10-step response to city power outage with negotiation and resource allocation",
                domains_required=["logistics", "negotiation", "scheduling"],
                constraints=["time_limit", "budget", "stakeholder_agreement"],
                goal="Restore minimum service level with all constraints satisfied",
                failure_injection=FailureInjection(
                    failure_id="f1",
                    failure_type=FailureType.RESOURCE_UNAVAILABLE,
                    step_number=5,
                    description="Key supplier backs out; time window shrinks by 30%"
                ),
                success_criteria={"service_restored": True, "constraints_met": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_2_cooking_chemistry_budget",
                title="Cooking + Chemistry + Budgeting",
                description="Create 3-course meal under budget with dietary constraints and taste profile",
                domains_required=["cooking", "chemistry", "finance"],
                constraints=["budget_limit", "dietary_restrictions", "taste_balance"],
                goal="Deliver meal meeting all criteria",
                failure_injection=FailureInjection(
                    failure_id="f2",
                    failure_type=FailureType.RESOURCE_UNAVAILABLE,
                    step_number=4,
                    description="Two key ingredients unavailable"
                ),
                success_criteria={"meal_complete": True, "budget_ok": True, "taste_ok": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_3_robotics_assembly",
                title="Robotics Assembly + Project Management",
                description="Build assembly plan for robot kit with dependencies and tool constraints",
                domains_required=["robotics", "project_management"],
                constraints=["tool_availability", "dependency_order", "safety"],
                goal="Complete assembly safely within constraints",
                failure_injection=FailureInjection(
                    failure_id="f3",
                    failure_type=FailureType.RESOURCE_UNAVAILABLE,
                    step_number=4,
                    description="Primary tool breaks"
                ),
                success_criteria={"assembly_complete": True, "safe": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_4_chess_business",
                title="Chess → Business Strategy Transfer",
                description="Create market entry plan using chess principles",
                domains_required=["chess", "business"],
                constraints=["budget", "timing", "competition"],
                goal="Market entry with competitive advantage",
                failure_injection=FailureInjection(
                    failure_id="f4",
                    failure_type=FailureType.UNEXPECTED_OUTCOME,
                    step_number=3,
                    description="Competitor launches early"
                ),
                success_criteria={"market_entered": True, "advantage_preserved": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_5_medical_triage",
                title="Medical Triage + Ethics + Scheduling",
                description="Prioritize treatment with time/resource constraints and ethical rules",
                domains_required=["medical", "ethics", "scheduling"],
                constraints=["resource_limits", "ethical_rules", "time_critical"],
                goal="Optimal outcomes within ethical bounds",
                failure_injection=FailureInjection(
                    failure_id="f5",
                    failure_type=FailureType.RESOURCE_UNAVAILABLE,
                    step_number=6,
                    description="Critical resource unavailable"
                ),
                success_criteria={"patients_treated": True, "ethics_preserved": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_6_travel_fatigue",
                title="Multi-modal Travel + Cognitive Fatigue",
                description="Plan trip with meetings, time zones, and fatigue limits",
                domains_required=["travel", "scheduling", "psychology"],
                constraints=["time_zones", "fatigue_limits", "deadlines"],
                goal="Complete trip with all meetings and manageable fatigue",
                failure_injection=FailureInjection(
                    failure_id="f6",
                    failure_type=FailureType.TIMING_VIOLATION,
                    step_number=3,
                    description="Flight canceled"
                ),
                success_criteria={"meetings_complete": True, "fatigue_ok": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_7_systems_debugging",
                title="Systems Debugging + Causal Analysis",
                description="Diagnose failing service, propose fix, plan rollout",
                domains_required=["systems", "causal_reasoning"],
                constraints=["uptime", "risk", "rollback_capability"],
                goal="Fix deployed without service disruption",
                failure_injection=FailureInjection(
                    failure_id="f7",
                    failure_type=FailureType.UNEXPECTED_OUTCOME,
                    step_number=5,
                    description="Fix causes latency spike"
                ),
                success_criteria={"bug_fixed": True, "no_disruption": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_8_school_schedule",
                title="Creative Design + Constraint Optimization",
                description="Design school schedule balancing outcomes, constraints, well-being",
                domains_required=["education", "optimization", "psychology"],
                constraints=["teacher_availability", "student_wellbeing", "learning_outcomes"],
                goal="Optimal schedule meeting all constraints",
                failure_injection=FailureInjection(
                    failure_id="f8",
                    failure_type=FailureType.CONSTRAINT_CHANGE,
                    step_number=7,
                    description="Teacher availability changes"
                ),
                success_criteria={"schedule_complete": True, "outcomes_ok": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_9_cross_domain_forecasting",
                title="Cross-domain Forecasting",
                description="Predict policy outcomes by transferring causal patterns",
                domains_required=["domain_a", "domain_b", "causal_reasoning"],
                constraints=["validity", "confidence_bounds"],
                goal="Accurate forecast with explicit causal transfer",
                failure_injection=FailureInjection(
                    failure_id="f9",
                    failure_type=FailureType.ASSUMPTION_INVALIDATED,
                    step_number=4,
                    description="Key assumption invalidated"
                ),
                success_criteria={"forecast_updated": True, "causal_justified": True},
                minimum_steps=10
            ),
            EvaluationTask(
                task_id="task_10_autonomous_improvement",
                title="Autonomous Skill Improvement Loop",
                description="Identify capability gap, propose improvement, validate, explain impact",
                domains_required=["introspection", "planning", "causal_reasoning"],
                constraints=["no_regressions", "measurable_improvement"],
                goal="Improvement deployed with verified impact",
                failure_injection=FailureInjection(
                    failure_id="f10",
                    failure_type=FailureType.UNEXPECTED_OUTCOME,
                    step_number=6,
                    description="Improvement reduces performance elsewhere"
                ),
                success_criteria={"improvement_deployed": True, "no_regressions": True},
                minimum_steps=10
            )
        ]
    
    def run_task(self, task_id: str, system_response_fn: Callable) -> EvaluationScore:
        """
        Run a single evaluation task.
        
        Args:
            task_id: ID of task to run
            system_response_fn: Function that takes (task, failure) and returns TaskResponse
        
        Returns:
            EvaluationScore
        """
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if not task:
            raise ValueError(f"Unknown task: {task_id}")
        
        # Get system response
        response = system_response_fn(task, task.failure_injection)
        
        # Score response
        score = self.scorer.evaluate(response, task)
        
        return score
    
    def run_all_tasks(self, system_response_fn: Callable) -> Dict[str, EvaluationScore]:
        """Run all evaluation tasks and return scores."""
        results = {}
        for task in self.tasks:
            results[task.task_id] = self.run_task(task.task_id, system_response_fn)
        return results
    
    def generate_report(self, results: Dict[str, EvaluationScore]) -> Dict[str, Any]:
        """Generate summary report across all tasks."""
        passed_count = sum(1 for score in results.values() if score.passed)
        total_count = len(results)
        
        avg_scores = {
            "cross_domain_transfer": sum(s.cross_domain_transfer for s in results.values()) / total_count,
            "multi_step_planning": sum(s.multi_step_planning for s in results.values()) / total_count,
            "adaptation_to_failure": sum(s.adaptation_to_failure for s in results.values()) / total_count,
            "explanation_quality": sum(s.explanation_quality for s in results.values()) / total_count,
            "overall": sum(s.overall for s in results.values()) / total_count
        }
        
        return {
            "tasks_passed": passed_count,
            "tasks_total": total_count,
            "pass_rate": passed_count / total_count,
            "average_scores": avg_scores,
            "classification": "AGI-capable" if passed_count >= 8 else 
                           "Advanced" if passed_count >= 6 else
                           "Narrow AI",
            "detailed_results": {tid: s.reasoning for tid, s in results.items()}
        }
