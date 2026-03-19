"""
Unified World Model - Foundational representational substrate for cross-domain reasoning.

This module provides:
- Canonical entity types (Actor, Goal, Constraint, Resource, State)
- Cross-domain inference engine
- Unified variable system (time, energy, attention, risk)
- Integration layer for composing domain models
"""

from .entity_system import (
    Entity,
    Actor,
    Goal,
    Constraint,
    Resource,
    State,
    Relation,
    CausalLink,
    EntityType,
    ConstraintType,
    ResourceType
)

from .inference_engine import (
    InferenceEngine,
    InferenceRule,
    Pattern,
    PatternMatch
)

from .unified_variables import (
    UnifiedVariable,
    TimeVariable,
    EnergyVariable,
    AttentionVariable,
    RiskVariable
)

from .integration_layer import (
    WorldModel,
    DomainAdapter
)

from .transfer_system import (
    AutonomousTransferEngine,
    TransferValidityAssessor,
    StructuralSignature,
    TransferAttempt
)

from .planning_system import (
    LongHorizonPlanner,
    Plan,
    PlanStep,
    PlanVerification,
    EmergentConstraint,
    ConstraintStatus,
    StepStatus,
    ConstraintViolationType
)

# Phase 4: Continual Learning
from .continual_learning import (
    ContinualLearningEngine,
    LearningSignal,
    ModelSnapshot,
    SafetyVerifier,
    CatastrophicForgettingDetector,
    ValidationResult,
    LearningMode,
    ModelVersion
)

# Phase 5: Autonomous Problem Discovery
from .problem_discovery import (
    ProblemDiscoveryEngine,
    DiscoverySignal,
    CapabilityGap,
    Opportunity,
    ProblemProposal,
    DiscoveryReport,
    SignalType,
    OpportunityType
)

# AGI Evaluation Harness
from .agi_evaluation_harness import (
    AGIEvaluationHarness,
    AGIEvaluationScorer,
    EvaluationTask,
    TaskResponse,
    DomainMapping,
    CausalExplanation,
    EvaluationScore,
    FailureInjection,
    FailureType,
    ScoringDimension
)

# Phase 6: Unified Control Loop
from .unified_control_loop import (
    UnifiedController,
    CausalStateManager,
    TransferConsultant,
    PlanValidator,
    OutcomeEvaluator,
    MetaLearner,
    ExecutionContext,
    CausalStateChange,
    PredictionComparison,
    ControlLoopPhase
)

__all__ = [
    # Entity system
    'Entity',
    'Actor',
    'Goal',
    'Constraint',
    'Resource',
    'State',
    'Relation',
    'CausalLink',
    'EntityType',
    'ConstraintType',
    'ResourceType',
    
    # Inference engine
    'InferenceEngine',
    'InferenceRule',
    'Pattern',
    'PatternMatch',
    
    # Unified variables
    'UnifiedVariable',
    'TimeVariable',
    'EnergyVariable',
    'AttentionVariable',
    'RiskVariable',
    
    # Integration
    'WorldModel',
    'DomainAdapter',
    
    # Transfer system
    'AutonomousTransferEngine',
    'TransferValidityAssessor',
    'StructuralSignature',
    'TransferAttempt',
    
    # Planning system
    'LongHorizonPlanner',
    'Plan',
    'PlanStep',
    'PlanVerification',
    'EmergentConstraint',
    'ConstraintStatus',
    'StepStatus',
    'ConstraintViolationType',
    
    # Continual learning
    'ContinualLearningEngine',
    'LearningSignal',
    'ModelSnapshot',
    'SafetyVerifier',
    'CatastrophicForgettingDetector',
    'ValidationResult',
    'LearningMode',
    'ModelVersion',
    
    # Autonomous problem discovery
    'ProblemDiscoveryEngine',
    'DiscoverySignal',
    'CapabilityGap',
    'Opportunity',
    'ProblemProposal',
    'DiscoveryReport',
    'SignalType',
    'OpportunityType',
    
    # AGI evaluation harness
    'AGIEvaluationHarness',
    'AGIEvaluationScorer',
    'EvaluationTask',
    'TaskResponse',
    'PlanStep',
    'DomainMapping',
    'CausalExplanation',
    'EvaluationScore',
    'FailureInjection',
    'FailureType',
    'ScoringDimension',
    
    # Phase 6: Unified Control Loop
    'UnifiedController',
    'CausalStateManager',
    'TransferConsultant',
    'PlanValidator',
    'OutcomeEvaluator',
    'MetaLearner',
    'ExecutionContext',
    'CausalStateChange',
    'PredictionComparison',
    'ControlLoopPhase'
]
