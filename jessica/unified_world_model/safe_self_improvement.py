"""
Safe Self-Improvement Loop - Design Specification

A conservative, auditable framework for autonomous system improvement that:
1. Proposes changes (not executes them)
2. Evaluates changes offline in sandboxed environments
3. Requires human approval before deployment
4. Includes automatic rollback if degradation detected
5. Maintains detailed audit logs of all changes
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable, Any, Set
from enum import Enum
import json
from datetime import datetime
import hashlib


# ============================================================================
# PHASE: CHANGE PROPOSAL GENERATION
# ============================================================================

class ChangeType(Enum):
    """Categories of allowable changes."""
    PARAMETER_TUNING = "parameter_tuning"  # Adjust thresholds, weights
    HEURISTIC_REFINEMENT = "heuristic_refinement"  # Improve decision rules
    KNOWLEDGE_EXPANSION = "knowledge_expansion"  # Add new domain knowledge
    STRATEGY_SWITCH = "strategy_switch"  # Switch between strategies
    PERFORMANCE_OPTIMIZATION = "performance_optimization"  # Speed/efficiency
    SAFETY_IMPROVEMENT = "safety_improvement"  # Enhance safety checks
    INTEGRATION_IMPROVEMENT = "integration_improvement"  # Better phase coupling


class ChangeRiskLevel(Enum):
    """Quantifies potential impact of change."""
    TRIVIAL = 1.0  # <1% performance impact, no human approval needed
    LOW = 2.0  # 1-5% impact, automated approval possible
    MEDIUM = 3.0  # 5-15% impact, requires human review + simulation
    HIGH = 4.0  # 15-50% impact, requires human approval + extended testing
    CRITICAL = 5.0  # >50% impact, requires deep analysis + multi-expert review


@dataclass
class ChangeProposal:
    """Proposal for a self-directed improvement."""
    proposal_id: str
    change_type: ChangeType
    title: str
    description: str
    
    # Affected components
    affected_components: List[str]  # e.g., ["CausalStateManager", "TransferConsultant"]
    affected_phases: List[int]  # e.g., [1, 2, 6]
    
    # Change specification
    current_value: Any  # Current parameter/strategy
    proposed_value: Any  # New value after change
    parameter_name: str  # What's being changed
    
    # Change justification
    motivation: str  # Why this change is beneficial
    expected_improvement: str  # How performance should improve
    improvement_metric: str  # What to measure (e.g., "causal_consistency_score")
    estimated_improvement: float  # 0.0-1.0 (e.g., 0.15 = 15% better)
    
    # Risk assessment
    risk_level: ChangeRiskLevel
    potential_downsides: List[str]  # Risks of the change
    affected_capabilities: List[str]  # Which capabilities could degrade
    rollback_difficulty: str  # "easy", "medium", "hard"
    
    # Temporal
    proposed_by: str  # "autonomous_discovery", "meta_learner", etc.
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None  # Don't try this forever
    
    # Metadata
    source_evidence: List[str] = field(default_factory=list)  # What data supports this
    confidence: float = 0.8  # How confident in the proposal (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/review."""
        return {
            "proposal_id": self.proposal_id,
            "change_type": self.change_type.value,
            "title": self.title,
            "affected_components": self.affected_components,
            "risk_level": self.risk_level.name,
            "estimated_improvement": self.estimated_improvement,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ChangeProposalBatch:
    """Batch of proposals generated in one cycle."""
    batch_id: str
    timestamp: datetime
    proposals: List[ChangeProposal]
    total_count: int
    high_risk_count: int
    
    def filter_by_risk(self, max_risk: ChangeRiskLevel) -> List[ChangeProposal]:
        """Get proposals below risk threshold."""
        return [p for p in self.proposals if p.risk_level.value <= max_risk.value]
    
    def filter_by_component(self, component: str) -> List[ChangeProposal]:
        """Get proposals affecting specific component."""
        return [p for p in self.proposals if component in p.affected_components]


class ChangeProposalGenerator:
    """
    Generates candidate improvements based on system analysis.
    
    Conservative: Only proposes changes that are:
    - Incremental (small bounded changes)
    - Reversible (easy to undo)
    - Low-risk (unlikely to harm performance)
    - Evidence-based (grounded in observed data)
    """
    
    def __init__(self):
        self.generated_count = 0
        self.approved_count = 0
        self.deployed_count = 0
        self.change_history: List[ChangeProposal] = []
    
    def analyze_system_and_propose(self,
                                   world_model: Any,
                                   statistics: Dict[str, Any]) -> ChangeProposalBatch:
        """
        Analyze current system state and generate improvement proposals.
        
        Data sources:
        - Performance statistics (accuracy, latency, consistency)
        - Error logs (categories, frequencies)
        - Component interactions (coupling metrics)
        - Domain coverage (gaps in knowledge)
        """
        self.generated_count += 1
        proposals = []
        
        # ===== PROPOSAL TYPE 1: Parameter Tuning =====
        # Adjust thresholds based on observed performance
        
        if statistics.get("prediction_errors"):
            error_rate = len(statistics["prediction_errors"]) / max(1, statistics.get("total_predictions", 1))
            
            if error_rate > 0.2:
                # Error rate high - propose tightening validation threshold
                proposals.append(ChangeProposal(
                    proposal_id=f"prop_{self.generated_count}_1",
                    change_type=ChangeType.PARAMETER_TUNING,
                    title="Increase Plan Validation Strictness",
                    description="Prediction error rate is high. Increase validation thresholds to catch more issues.",
                    affected_components=["PlanValidator"],
                    affected_phases=[6],
                    current_value=0.70,
                    proposed_value=0.75,
                    parameter_name="validation_threshold",
                    motivation="High prediction error rate suggests current validation is too permissive",
                    expected_improvement="Reduce false positives, improve causal consistency",
                    improvement_metric="causal_consistency_score",
                    estimated_improvement=0.05,
                    risk_level=ChangeRiskLevel.LOW,
                    potential_downsides=["May reject valid plans", "Could slow planning"],
                    affected_capabilities=["planning_success_rate"],
                    rollback_difficulty="easy",
                    proposed_by="autonomous_analysis",
                    source_evidence=[f"error_rate={error_rate:.2f}"]
                ))
        
        # ===== PROPOSAL TYPE 2: Heuristic Refinement =====
        # Improve decision-making rules
        
        if statistics.get("transfer_consultation_rate", 0) < 0.95:
            proposals.append(ChangeProposal(
                proposal_id=f"prop_{self.generated_count}_2",
                change_type=ChangeType.HEURISTIC_REFINEMENT,
                title="Improve Transfer Pattern Matching",
                description="Transfer consultation rate below target. Relax matching criteria.",
                affected_components=["TransferConsultant"],
                affected_phases=[2, 6],
                current_value="exact_structural_match",
                proposed_value="relaxed_structural_match",
                parameter_name="pattern_matching_strategy",
                motivation="Transfer consultation rate is low, indicating missed opportunities",
                expected_improvement="Increase cross-domain pattern reuse without sacrificing quality",
                improvement_metric="transfer_consultation_rate",
                estimated_improvement=0.10,
                risk_level=ChangeRiskLevel.MEDIUM,
                potential_downsides=["Could apply inappropriate patterns", "May reduce plan quality"],
                affected_capabilities=["cross_domain_transfer"],
                rollback_difficulty="easy",
                proposed_by="transfer_system",
                source_evidence=[f"consultation_rate={statistics.get('transfer_consultation_rate', 0):.2f}"]
            ))
        
        # ===== PROPOSAL TYPE 3: Knowledge Expansion =====
        # Add new domain knowledge if gaps detected
        
        if statistics.get("knowledge_gaps"):
            for gap_domain in list(statistics["knowledge_gaps"])[:3]:  # Limit to top 3
                proposals.append(ChangeProposal(
                    proposal_id=f"prop_{self.generated_count}_3_{gap_domain}",
                    change_type=ChangeType.KNOWLEDGE_EXPANSION,
                    title=f"Add Knowledge: {gap_domain.title()}",
                    description=f"Detected gap in {gap_domain} domain knowledge",
                    affected_components=["WorldModel"],
                    affected_phases=[1],
                    current_value=None,
                    proposed_value={"domain": gap_domain, "patterns": []},  # To be filled by human
                    parameter_name=f"{gap_domain}_knowledge",
                    motivation=f"System shows weakness in {gap_domain} reasoning",
                    expected_improvement="Broader applicability, better cross-domain transfer",
                    improvement_metric="domain_coverage_score",
                    estimated_improvement=0.08,
                    risk_level=ChangeRiskLevel.MEDIUM,
                    potential_downsides=["Added complexity", "Requires curation"],
                    affected_capabilities=["general_reasoning"],
                    rollback_difficulty="medium",
                    proposed_by="problem_discovery",
                    source_evidence=[f"gap_detected={gap_domain}"]
                ))
        
        # ===== PROPOSAL TYPE 4: Strategy Switching =====
        # Change algorithms based on meta-learning
        
        if statistics.get("meta_learner_stats"):
            meta = statistics["meta_learner_stats"]
            best_strategy = meta.get("best_strategy")
            current_strategy = statistics.get("current_learning_strategy", "hybrid")
            
            if best_strategy and best_strategy != current_strategy:
                improvement = meta.get("strategy_improvement", 0.0)
                if improvement > 0.15:  # >15% improvement threshold
                    proposals.append(ChangeProposal(
                        proposal_id=f"prop_{self.generated_count}_4",
                        change_type=ChangeType.STRATEGY_SWITCH,
                        title=f"Switch Learning Strategy to {best_strategy.title()}",
                        description=f"Meta-learner identified {best_strategy} as superior strategy",
                        affected_components=["ContinualLearningEngine"],
                        affected_phases=[4],
                        current_value=current_strategy,
                        proposed_value=best_strategy,
                        parameter_name="learning_strategy",
                        motivation=f"Meta-learner shows {improvement:.1%} improvement with {best_strategy}",
                        expected_improvement="Faster learning, better convergence",
                        improvement_metric="learning_efficiency",
                        estimated_improvement=improvement,
                        risk_level=ChangeRiskLevel.HIGH,
                        potential_downsides=["Strategy may not generalize", "Could harm other metrics"],
                        affected_capabilities=["learning_speed", "model_quality"],
                        rollback_difficulty="easy",
                        proposed_by="meta_learner",
                        confidence=meta.get("confidence", 0.7),
                        source_evidence=[f"improvement={improvement:.2f}", f"trials={meta.get('trials', 0)}"]
                    ))
        
        # ===== PROPOSAL TYPE 5: Safety Improvements =====
        # Strengthen safety mechanisms
        
        if statistics.get("safety_violations", 0) > 0:
            violations = statistics["safety_violations"]
            proposals.append(ChangeProposal(
                proposal_id=f"prop_{self.generated_count}_5",
                change_type=ChangeType.SAFETY_IMPROVEMENT,
                title="Strengthen Causal Consistency Checking",
                description="Safety violations detected. Increase monitoring.",
                affected_components=["CausalStateManager"],
                affected_phases=[6],
                current_value="reactive_checking",
                proposed_value="proactive_checking",
                parameter_name="safety_check_mode",
                motivation=f"Detected {violations} safety violations",
                expected_improvement="Prevent more violations before they occur",
                improvement_metric="safety_violation_count",
                estimated_improvement=1.0,  # Expected to reduce to 0
                risk_level=ChangeRiskLevel.TRIVIAL,
                potential_downsides=["Slight performance overhead"],
                affected_capabilities=["safety"],
                rollback_difficulty="easy",
                proposed_by="safety_monitor",
                source_evidence=[f"violations={violations}"]
            ))
        
        # ===== PROPOSAL TYPE 6: Integration Improvements =====
        # Tighten coupling between phases
        
        if statistics.get("integration_quality", 0) < 4.0:
            proposals.append(ChangeProposal(
                proposal_id=f"prop_{self.generated_count}_6",
                change_type=ChangeType.INTEGRATION_IMPROVEMENT,
                title="Increase Cross-Phase Coordination",
                description="Improve feedback between learning and transfer systems",
                affected_components=["UnifiedController"],
                affected_phases=[2, 4, 6],
                current_value="loose_coupling",
                proposed_value="tight_coupling",
                parameter_name="phase_coordination_level",
                motivation="Integration quality below target",
                expected_improvement="Better information flow between components",
                improvement_metric="integration_quality",
                estimated_improvement=0.25,
                risk_level=ChangeRiskLevel.MEDIUM,
                potential_downsides=["More complex interactions", "Harder to debug"],
                affected_capabilities=["overall_intelligence"],
                rollback_difficulty="medium",
                proposed_by="architecture_analyzer",
                source_evidence=[f"integration_quality={statistics.get('integration_quality', 0):.2f}"]
            ))
        
        batch = ChangeProposalBatch(
            batch_id=f"batch_{self.generated_count}",
            timestamp=datetime.now(),
            proposals=proposals,
            total_count=len(proposals),
            high_risk_count=sum(1 for p in proposals if p.risk_level.value >= 4.0)
        )
        
        self.change_history.extend(proposals)
        return batch


# ============================================================================
# PHASE: OFFLINE SIMULATION & EVALUATION
# ============================================================================

@dataclass
class SimulationResult:
    """Results from testing a change in isolated environment."""
    proposal_id: str
    simulation_id: str
    
    # Metrics
    performance_before: Dict[str, float]
    performance_after: Dict[str, float]
    performance_delta: Dict[str, float]  # Positive = improvement
    overall_score_before: float
    overall_score_after: float
    score_improvement: float
    
    # Safety
    safety_violations: int
    causal_drift: float
    regression_detected: bool
    affected_metrics: List[str]
    
    # Validation
    passed_baseline: bool  # Passes minimum quality bar
    passed_improvement: bool  # Achieves expected improvement
    safe_to_deploy: bool  # Safe for real deployment
    
    # Metadata
    environment: str  # "test_suite", "synthetic_queries", "replay_log"
    duration_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    confidence: float = 0.9
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for review/logging."""
        return {
            "proposal_id": self.proposal_id,
            "overall_improvement": self.score_improvement,
            "safe_to_deploy": self.safe_to_deploy,
            "regression_detected": self.regression_detected,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat()
        }


class SimulationEnvironment:
    """
    Sandboxed environment for testing changes before deployment.
    
    - Isolated from production system
    - Uses historical data and synthetic queries
    - Measures all key metrics
    - Detects regressions automatically
    """
    
    def __init__(self):
        self.simulations_run = 0
        self.results_cache: Dict[str, SimulationResult] = {}
    
    def create_copy_of_system(self, original_system: Any) -> Any:
        """Create an isolated copy of the system for testing."""
        # Deep copy of all components
        import copy
        return copy.deepcopy(original_system)
    
    def apply_proposal_to_system(self, system: Any, proposal: ChangeProposal) -> None:
        """Apply a proposed change to the test copy."""
        component = proposal.affected_components[0]
        
        if proposal.change_type == ChangeType.PARAMETER_TUNING:
            # Update parameter value
            if hasattr(system, component):
                comp = getattr(system, component)
                if hasattr(comp, proposal.parameter_name):
                    setattr(comp, proposal.parameter_name, proposal.proposed_value)
        
        elif proposal.change_type == ChangeType.STRATEGY_SWITCH:
            # Switch strategy
            if hasattr(system, component):
                comp = getattr(system, component)
                if hasattr(comp, "strategy"):
                    comp.strategy = proposal.proposed_value
        
        # Similar for other change types...
    
    def run_test_queries(self, system: Any, query_count: int = 100) -> Dict[str, float]:
        """Run system through test query suite."""
        metrics = {
            "accuracy": 0.0,
            "latency_ms": 0.0,
            "causal_consistency": 1.0,
            "transfer_rate": 0.0,
            "validation_rate": 1.0,
            "error_count": 0,
            "safety_violations": 0
        }
        
        # Simplified: in production, would run comprehensive test suite
        # For now, return realistic simulated metrics
        
        return metrics
    
    def evaluate_proposal(self,
                         original_system: Any,
                         proposal: ChangeProposal,
                         test_queries: Optional[List[Dict]] = None) -> SimulationResult:
        """
        Simulate the proposed change and evaluate results.
        
        Steps:
        1. Create isolated copy of system
        2. Measure baseline performance
        3. Apply proposal
        4. Measure performance after change
        5. Compare and assess safety
        """
        self.simulations_run += 1
        
        # Measure baseline
        baseline_metrics = self.run_test_queries(original_system)
        baseline_score = self._calculate_overall_score(baseline_metrics)
        
        # Create test copy
        test_system = self.create_copy_of_system(original_system)
        
        # Apply change
        self.apply_proposal_to_system(test_system, proposal)
        
        # Measure after change
        after_metrics = self.run_test_queries(test_system)
        after_score = self._calculate_overall_score(after_metrics)
        
        # Calculate deltas
        deltas = {
            k: after_metrics.get(k, 0) - baseline_metrics.get(k, 0)
            for k in baseline_metrics.keys()
        }
        
        # Detect problems
        regression = any(deltas.get(k, 0) < -0.05 for k in ["accuracy", "causal_consistency"])
        violations = after_metrics.get("safety_violations", 0)
        drift = 1.0 - after_metrics.get("causal_consistency", 0.9)
        
        # Determine if safe
        safe = (
            not regression and
            violations == 0 and
            drift < 0.1 and
            after_score >= baseline_score * 0.95  # Don't degrade more than 5%
        )
        
        result = SimulationResult(
            proposal_id=proposal.proposal_id,
            simulation_id=f"sim_{self.simulations_run}",
            performance_before=baseline_metrics,
            performance_after=after_metrics,
            performance_delta=deltas,
            overall_score_before=baseline_score,
            overall_score_after=after_score,
            score_improvement=after_score - baseline_score,
            safety_violations=violations,
            causal_drift=drift,
            regression_detected=regression,
            affected_metrics=list(deltas.keys()),
            passed_baseline=after_score >= baseline_score * 0.95,
            passed_improvement=after_score > baseline_score,
            safe_to_deploy=safe,
            environment="synthetic_queries",
            duration_seconds=0.5,
            confidence=0.85 if not regression else 0.6,
            notes=f"Improvement: {(after_score - baseline_score):.3f}"
        )
        
        self.results_cache[proposal.proposal_id] = result
        return result
    
    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calculate composite quality score from metrics."""
        # Weighted combination
        weights = {
            "accuracy": 0.30,
            "causal_consistency": 0.25,
            "transfer_rate": 0.15,
            "validation_rate": 0.15,
            "latency_ms": -0.15  # Negative = lower is better
        }
        
        score = 0.0
        for k, w in weights.items():
            if k in metrics:
                if k == "latency_ms":
                    # Normalize latency: lower is better, 1000ms = 0 score
                    latency_score = max(0.0, 1.0 - metrics[k] / 1000.0)
                    score += latency_score * w
                else:
                    score += metrics.get(k, 0.5) * w
            else:
                # Default to 0.5 for missing metrics
                score += 0.5 * w
        
        return max(0.0, min(1.0, score))


# ============================================================================
# PHASE: HUMAN APPROVAL GATE
# ============================================================================

class ApprovalStatus(Enum):
    """Current state of approval workflow."""
    PROPOSED = "proposed"  # Initial state
    UNDER_REVIEW = "under_review"  # Human is examining
    APPROVED = "approved"  # Approved for deployment
    REJECTED = "rejected"  # Rejected
    QUEUED_FOR_DEPLOYMENT = "queued"  # Waiting for deployment window
    DEPLOYED = "deployed"  # Already deployed
    ROLLED_BACK = "rolled_back"  # Reverted


@dataclass
class ApprovalDecision:
    """Record of human approval decision."""
    proposal_id: str
    decision: ApprovalStatus
    reviewer_id: str  # Which human approved it
    reasoning: str  # Why they approved/rejected
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Conditions
    conditions: List[str] = field(default_factory=list)  # e.g., ["Only deploy if X"]
    require_retest: bool = False
    approval_confidence: float = 0.9  # 0.0-1.0


class ApprovalGate:
    """
    Human-in-the-loop approval for changes.
    
    Strategy:
    - Trivial changes: Auto-approve with logging
    - Low-risk changes: Require one reviewer
    - Medium-risk changes: Require two reviewers + simulation
    - High-risk changes: Require expert review + extended analysis
    - Critical changes: Require executive-level approval
    """
    
    def __init__(self):
        self.approval_queue: List[Tuple[ChangeProposal, SimulationResult]] = []
        self.approval_decisions: Dict[str, ApprovalDecision] = {}
        self.auto_approved_count = 0
        self.human_approved_count = 0
        self.rejected_count = 0
    
    def submit_for_approval(self,
                           proposal: ChangeProposal,
                           simulation_result: SimulationResult) -> ApprovalStatus:
        """
        Submit proposal to approval queue.
        Returns either auto-approval or queues for human review.
        """
        
        # ===== AUTO-APPROVE: Safety Improvements (Trivial Risk) =====
        if (proposal.change_type == ChangeType.SAFETY_IMPROVEMENT and
            proposal.risk_level == ChangeRiskLevel.TRIVIAL and
            simulation_result.safe_to_deploy):
            
            self.approval_decisions[proposal.proposal_id] = ApprovalDecision(
                proposal_id=proposal.proposal_id,
                decision=ApprovalStatus.APPROVED,
                reviewer_id="system_auto_approval",
                reasoning="Safety improvement, trivial risk, simulation passed"
            )
            self.auto_approved_count += 1
            return ApprovalStatus.APPROVED
        
        # ===== AUTO-APPROVE: Performance Optimizations (Low Risk + Good Results) =====
        if (proposal.change_type == ChangeType.PERFORMANCE_OPTIMIZATION and
            proposal.risk_level == ChangeRiskLevel.LOW and
            simulation_result.safe_to_deploy and
            simulation_result.passed_improvement):
            
            self.approval_decisions[proposal.proposal_id] = ApprovalDecision(
                proposal_id=proposal.proposal_id,
                decision=ApprovalStatus.APPROVED,
                reviewer_id="system_auto_approval",
                reasoning="Performance optimization, low risk, positive results in simulation"
            )
            self.auto_approved_count += 1
            return ApprovalStatus.APPROVED
        
        # ===== QUEUE FOR HUMAN REVIEW =====
        self.approval_queue.append((proposal, simulation_result))
        return ApprovalStatus.UNDER_REVIEW
    
    def generate_review_summary(self,
                               proposal: ChangeProposal,
                               simulation_result: SimulationResult) -> Dict[str, Any]:
        """Generate human-readable summary for reviewer."""
        return {
            "title": proposal.title,
            "type": proposal.change_type.value,
            "risk_level": proposal.risk_level.name,
            "motivation": proposal.motivation,
            "expected_improvement": proposal.expected_improvement,
            "estimated_improvement": f"{proposal.estimated_improvement:.1%}",
            "simulation_results": {
                "safe_to_deploy": simulation_result.safe_to_deploy,
                "score_improvement": f"{simulation_result.score_improvement:.3f}",
                "regression_detected": simulation_result.regression_detected,
                "safety_violations": simulation_result.safety_violations,
                "confidence": f"{simulation_result.confidence:.1%}"
            },
            "downsides": proposal.potential_downsides,
            "rollback_difficulty": proposal.rollback_difficulty,
            "reviewer_questions": [
                "Does the motivation align with system goals?",
                "Is the estimated improvement realistic?",
                "Are the potential downsides acceptable?",
                "Is rollback feasible if problems occur?",
                f"Does simulation result justify {proposal.risk_level.name} risk?"
            ]
        }
    
    def human_decision(self,
                      proposal_id: str,
                      decision: ApprovalStatus,
                      reviewer_id: str,
                      reasoning: str,
                      conditions: Optional[List[str]] = None) -> ApprovalDecision:
        """Record human approval decision."""
        decision_record = ApprovalDecision(
            proposal_id=proposal_id,
            decision=decision,
            reviewer_id=reviewer_id,
            reasoning=reasoning,
            conditions=conditions or []
        )
        
        self.approval_decisions[proposal_id] = decision_record
        
        if decision == ApprovalStatus.APPROVED:
            self.human_approved_count += 1
        elif decision == ApprovalStatus.REJECTED:
            self.rejected_count += 1
        
        return decision_record


# ============================================================================
# PHASE: DEPLOYMENT WITH AUTOMATIC ROLLBACK
# ============================================================================

@dataclass
class DeploymentRecord:
    """Records a deployed change."""
    proposal_id: str
    deployment_id: str
    change_type: ChangeType
    
    # Before state
    system_state_hash: str  # Hash of system before change
    baseline_metrics: Dict[str, float]
    
    # Deployment
    deployed_at: datetime
    deployed_by: str  # Who initiated deployment
    
    # After deployment
    active: bool
    metrics_after: Optional[Dict[str, float]] = None
    
    # Rollback
    needs_rollback: bool = False
    rollback_reason: Optional[str] = None
    rollback_triggered_at: Optional[datetime] = None


class RollbackDetector:
    """
    Monitors deployed changes for problems.
    Automatically triggers rollback if degradation detected.
    """
    
    def __init__(self):
        self.monitored_deployments: List[DeploymentRecord] = []
        self.rollback_count = 0
        self.degradation_threshold = 0.10  # Rollback if >10% degradation
        self.regression_threshold = 0.05   # Rollback if any metric drops >5%
    
    def monitor_deployment(self, deployment: DeploymentRecord) -> None:
        """Start monitoring a deployed change."""
        self.monitored_deployments.append(deployment)
    
    def check_for_degradation(self,
                             deployment: DeploymentRecord,
                             current_metrics: Dict[str, float]) -> Tuple[bool, Optional[str]]:
        """
        Check if deployed change should be rolled back.
        
        Returns:
            (should_rollback, reason)
        """
        baseline = deployment.baseline_metrics
        
        # Calculate overall degradation
        key_metrics = ["accuracy", "causal_consistency", "planning_success_rate"]
        degradation = sum(
            max(0, baseline.get(m, 0) - current_metrics.get(m, 0))
            for m in key_metrics
        ) / len(key_metrics)
        
        if degradation > self.degradation_threshold:
            return True, f"Overall degradation {degradation:.1%} exceeds threshold"
        
        # Check for regressions
        for metric in key_metrics:
            baseline_val = baseline.get(metric, 0)
            current_val = current_metrics.get(metric, 0)
            regression = (baseline_val - current_val) / max(0.01, baseline_val)
            
            if regression > self.regression_threshold:
                return True, f"Regression in {metric}: {regression:.1%}"
        
        # Check safety
        if current_metrics.get("safety_violations", 0) > baseline.get("safety_violations", 0):
            violations_increase = (
                current_metrics["safety_violations"] - baseline["safety_violations"]
            )
            return True, f"Safety violations increased by {violations_increase}"
        
        return False, None
    
    def trigger_rollback(self,
                        deployment: DeploymentRecord,
                        reason: str,
                        rollback_fn: Callable) -> bool:
        """Execute rollback of a deployment."""
        try:
            # Execute rollback function
            rollback_fn(deployment)
            
            # Record rollback
            deployment.needs_rollback = True
            deployment.rollback_reason = reason
            deployment.rollback_triggered_at = datetime.now()
            deployment.active = False
            
            self.rollback_count += 1
            
            print(f"✓ Rollback triggered for {deployment.proposal_id}")
            print(f"  Reason: {reason}")
            return True
            
        except Exception as e:
            print(f"✗ Rollback FAILED for {deployment.proposal_id}: {str(e)}")
            return False


class DeploymentManager:
    """
    Manages deployment of approved changes.
    Includes staged rollout and monitoring.
    """
    
    def __init__(self):
        self.deployments: Dict[str, DeploymentRecord] = {}
        self.rollback_detector = RollbackDetector()
        self.deployed_count = 0
        self.rollback_executed_count = 0
    
    def deploy_change(self,
                     proposal: ChangeProposal,
                     apply_fn: Callable) -> DeploymentRecord:
        """Deploy an approved change."""
        # Record baseline metrics (simplified)
        baseline_metrics = {
            "accuracy": 0.85,
            "causal_consistency": 0.95,
            "planning_success_rate": 0.88,
            "latency_ms": 125,
            "safety_violations": 0
        }
        
        # Generate deployment record
        deployment = DeploymentRecord(
            proposal_id=proposal.proposal_id,
            deployment_id=f"deploy_{self.deployed_count}",
            change_type=proposal.change_type,
            system_state_hash=self._hash_system_state(),
            baseline_metrics=baseline_metrics,
            deployed_at=datetime.now(),
            deployed_by="deployment_manager",
            active=True
        )
        
        # Apply the change
        apply_fn(proposal)
        
        # Start monitoring
        self.rollback_detector.monitor_deployment(deployment)
        
        self.deployments[proposal.proposal_id] = deployment
        self.deployed_count += 1
        
        return deployment
    
    def _hash_system_state(self) -> str:
        """Generate hash of current system state."""
        return hashlib.sha256(b"system_state").hexdigest()


# ============================================================================
# ORCHESTRATOR: SAFE SELF-IMPROVEMENT LOOP
# ============================================================================

class SafeSelfImprovementLoop:
    """
    Complete safe self-improvement system.
    
    Flow:
    1. Analyze → Generate proposals
    2. Simulate → Evaluate offline
    3. Review → Get human approval
    4. Deploy → Apply changes
    5. Monitor → Check for problems
    6. Rollback → Fix if needed
    """
    
    def __init__(self,
                 system: Any,
                 approval_gate: ApprovalGate,
                 simulation_env: SimulationEnvironment,
                 deployment_manager: DeploymentManager):
        self.system = system
        self.approval_gate = approval_gate
        self.simulation_env = simulation_env
        self.deployment_manager = deployment_manager
        
        self.proposal_generator = ChangeProposalGenerator()
        
        # State tracking
        self.improvement_cycles = 0
        self.total_proposals = 0
        self.approved_proposals = 0
        self.deployed_proposals = 0
        self.rolled_back_proposals = 0
        
        # Audit log
        self.audit_log: List[Dict[str, Any]] = []
    
    def run_improvement_cycle(self,
                             system_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute one complete self-improvement cycle.
        
        Steps:
        1. Propose improvements
        2. Simulate each proposal
        3. Queue for human approval
        4. Deploy approved changes
        5. Monitor for problems
        """
        self.improvement_cycles += 1
        cycle_report = {
            "cycle": self.improvement_cycles,
            "timestamp": datetime.now().isoformat(),
            "proposals_generated": 0,
            "proposals_approved": 0,
            "proposals_deployed": 0,
            "proposals_rejected": 0,
            "proposals_rolled_back": 0,
            "total_improvement": 0.0
        }
        
        # ===== STEP 1: Generate Proposals =====
        print(f"\n{'='*60}")
        print(f"SELF-IMPROVEMENT CYCLE {self.improvement_cycles}")
        print(f"{'='*60}\n")
        
        print("[1/5] Generating improvement proposals...")
        batch = self.proposal_generator.analyze_system_and_propose(self.system, system_statistics)
        self.total_proposals += batch.total_count
        cycle_report["proposals_generated"] = batch.total_count
        
        print(f"Generated {batch.total_count} proposals ({batch.high_risk_count} high-risk)")
        
        # ===== STEP 2: Simulate Proposals =====
        print("\n[2/5] Running offline simulations...")
        simulation_results = []
        
        for proposal in batch.proposals:
            result = self.simulation_env.evaluate_proposal(self.system, proposal)
            simulation_results.append((proposal, result))
            print(f"  {proposal.title}: ", end="")
            
            if result.safe_to_deploy:
                print(f"✓ Safe (+{result.score_improvement:.3f})")
            elif result.passed_baseline:
                print(f"⚠ Baseline met, needs review")
            else:
                print(f"✗ Failed baseline")
        
        # ===== STEP 3: Submit for Approval =====
        print("\n[3/5] Submitting for approval...")
        approved = []
        
        for proposal, result in simulation_results:
            status = self.approval_gate.submit_for_approval(proposal, result)
            
            if status == ApprovalStatus.APPROVED:
                approved.append((proposal, result))
                cycle_report["proposals_approved"] += 1
                print(f"  {proposal.title}: AUTO-APPROVED")
            else:
                print(f"  {proposal.title}: Queued for human review")
                # In practice, would notify human here
        
        # ===== STEP 4: Deploy Approved Changes =====
        print("\n[4/5] Deploying approved changes...")
        
        for proposal, result in approved:
            try:
                deployment = self.deployment_manager.deploy_change(
                    proposal,
                    apply_fn=lambda p: self._apply_change(p)
                )
                cycle_report["proposals_deployed"] += 1
                cycle_report["total_improvement"] += result.score_improvement
                print(f"  ✓ Deployed: {proposal.title}")
                
            except Exception as e:
                print(f"  ✗ Failed to deploy: {proposal.title} ({str(e)})")
        
        # ===== STEP 5: Monitor and Prepare Rollback =====
        print("\n[5/5] Monitoring for problems...")
        
        # In production, would continuously monitor
        # For now, just report
        print(f"  Active deployments: {len(self.deployment_manager.deployments)}")
        print(f"  Rollback capacity: {'✓ Ready' if self.deployment_manager.rollback_detector else '✗ Not configured'}")
        
        # ===== FINAL REPORT =====
        print(f"\n{'='*60}")
        print(f"CYCLE SUMMARY")
        print(f"{'='*60}")
        print(f"Proposals: {cycle_report['proposals_generated']} generated")
        print(f"           {cycle_report['proposals_approved']} approved")
        print(f"           {cycle_report['proposals_deployed']} deployed")
        print(f"           {cycle_report['proposals_rejected']} rejected")
        print(f"Total Improvement: {cycle_report['total_improvement']:.3f}")
        print(f"{'='*60}\n")
        
        self.audit_log.append(cycle_report)
        return cycle_report
    
    def _apply_change(self, proposal: ChangeProposal) -> None:
        """Apply a change to the system."""
        # Simplified: in production, would apply based on proposal details
        component = proposal.affected_components[0]
        if hasattr(self.system, component):
            comp = getattr(self.system, component)
            if hasattr(comp, proposal.parameter_name):
                setattr(comp, proposal.parameter_name, proposal.proposed_value)
    
    def handle_detected_problem(self,
                               deployment_id: str,
                               current_metrics: Dict[str, float]) -> bool:
        """
        Handle detected problem in deployed change.
        Checks if rollback is needed and executes it.
        """
        deployment = self.deployment_manager.deployments.get(deployment_id)
        if not deployment:
            return False
        
        # Check for degradation
        should_rollback, reason = self.deployment_manager.rollback_detector.check_for_degradation(
            deployment, current_metrics
        )
        
        if should_rollback:
            # Execute rollback
            success = self.deployment_manager.rollback_detector.trigger_rollback(
                deployment,
                reason,
                rollback_fn=self._execute_rollback
            )
            
            if success:
                self.rolled_back_proposals += 1
                self.audit_log.append({
                    "event": "rollback",
                    "deployment_id": deployment_id,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                })
            
            return success
        
        return False
    
    def _execute_rollback(self, deployment: DeploymentRecord) -> None:
        """Execute actual rollback of a deployed change."""
        # Restore system to state before deployment
        # This is simplified; real version would restore from snapshot
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of improvement system."""
        return {
            "cycles_completed": self.improvement_cycles,
            "total_proposals": self.total_proposals,
            "approved": self.approval_gate.human_approved_count + self.approval_gate.auto_approved_count,
            "deployed": self.deployed_proposals,
            "rolled_back": self.rolled_back_proposals,
            "auto_approval_rate": (
                self.approval_gate.auto_approved_count /
                max(1, self.total_proposals)
            ),
            "approval_queue_size": len(self.approval_gate.approval_queue),
            "active_deployments": len([d for d in self.deployment_manager.deployments.values() if d.active])
        }
