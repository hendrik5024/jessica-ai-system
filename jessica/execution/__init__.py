"""Phase 5.2: Minimal Action-Only Embodiment

Keyboard and mouse execution ONLY through approved Phase 5.1.5 intent pipelines.

One intent → one atomic action → immediate return
No chaining, no loops, no automation
Full audit trail and reversibility
"""

from .execution_tracker import ExecutionTracker, ExecutionOutcome, ExecutionStatus, ExecutionRecord
from .keyboard_executor import KeyboardExecutor
from .mouse_executor import MouseExecutor
from .action_executor import ActionExecutor
from .outcome_reflection import OutcomeReflection
from .failure_classifier import FailureClassifier, FailureCategory, ClassificationResult
from .recovery_option import RecoveryOption, RecoveryRisk
from .recovery_analyzer import RecoveryAnalyzer
from .recovery_orchestrator import RecoveryOrchestrator
from .action_plan import ActionPlan, PlanStatus, StepResult, create_action_plan
from .action_plan_builder import ActionPlanBuilder
from .action_plan_executor import ActionPlanExecutor
from .action_plan_state_tracker import ActionPlanStateTracker
from .decision_structures import (
    DecisionProposal,
    DecisionEvaluation,
    DecisionExplanation,
    DecisionBundle,
    RiskLevel,
    ReversibilityScore,
    create_decision_bundle,
)
from .decision_proposer import DecisionProposer
from .decision_evaluator import DecisionEvaluator
from .decision_explainer import DecisionExplainer
from .decision_orchestrator import DecisionOrchestrator
from .action_proposal_structures import (
    ActionProposal,
    ProposalStatus,
    create_action_proposal,
)
from .proposal_engine import ActionProposalEngine
from .approval_gate import HumanApprovalGate, ApprovalDecision
from .proposal_registry import ProposalRegistry
from .execution_request import ExecutionRequest, create_execution_request
from .execution_validator import ExecutionValidator, ValidationResult
from .execution_engine import ExecutionEngine, ExecutionResultStatus, ExecutionResult
from .execution_audit import ExecutionAudit, AuditEntry
from .execution_orchestrator import ExecutionOrchestrator
from .reflection_record import ReflectionRecord, SourceType, ConfidenceLevel, create_reflection_record
from .reflection_factory import ReflectionFactory
from .reflection_analyzer import ReflectionAnalyzer
from .reflection_registry import ReflectionRegistry
from .reflection_orchestrator import ReflectionOrchestrator
from .identity_profile import IdentityProfile
from .conversational_orchestrator import ConversationalOrchestrator
from .conversation_context import ConversationContext
from .enhanced_narrative_formatter import EnhancedNarrativeFormatter
from .contextual_orchestrator import ContextualOrchestrator

__all__ = [
    "ExecutionTracker",
    "ExecutionOutcome",
    "ExecutionStatus",
    "ExecutionRecord",
    "KeyboardExecutor",
    "MouseExecutor",
    "ActionExecutor",
    "OutcomeReflection",
    "FailureClassifier",
    "FailureCategory",
    "ClassificationResult",
    "RecoveryOption",
    "RecoveryRisk",
    "RecoveryAnalyzer",
    "RecoveryOrchestrator",
    "ActionPlan",
    "PlanStatus",
    "StepResult",
    "create_action_plan",
    "ActionPlanBuilder",
    "ActionPlanExecutor",
    "ActionPlanStateTracker",
    # Phase 6: Decision Support - Read-Only Advisory Layer
    "DecisionProposal",
    "DecisionEvaluation",
    "DecisionExplanation",
    "DecisionBundle",
    "RiskLevel",
    "ReversibilityScore",
    "create_decision_bundle",
    "DecisionProposer",
    "DecisionEvaluator",
    "DecisionExplainer",
    "DecisionOrchestrator",
    # Phase 7.1: Action Proposals - Human-Reviewed Advisory Layer
    "ActionProposal",
    "ProposalStatus",
    "create_action_proposal",
    "ActionProposalEngine",
    "HumanApprovalGate",
    "ApprovalDecision",
    "ProposalRegistry",
    # Phase 7.2: Proposal-Bound Execution - Controlled Execution Layer
    "ExecutionRequest",
    "create_execution_request",
    "ExecutionValidator",
    "ValidationResult",
    "ExecutionEngine",
    "ExecutionResultStatus",
    "ExecutionResult",
    "ExecutionAudit",
    "AuditEntry",
    "ExecutionOrchestrator",
    # Phase 7.3: Reflective Intelligence - Advisory-Only Layer
    "ReflectionRecord",
    "SourceType",
    "ConfidenceLevel",
    "create_reflection_record",
    "ReflectionFactory",
    "ReflectionAnalyzer",
    "ReflectionRegistry",
    "ReflectionOrchestrator",
    # Phase 8: Conversational Identity - Narrative Interface
    "IdentityProfile",
    "ConversationalOrchestrator",
    # Phase 8.2: Conversational Memory Boundary
    "ConversationContext",
    "EnhancedNarrativeFormatter",
    "ContextualOrchestrator",
]
