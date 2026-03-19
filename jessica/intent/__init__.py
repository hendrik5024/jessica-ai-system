"""
Phase 5.1.5: Intent Mediation & Cognitive Grounding

Intent objects, justification, risk assessment, dry-run simulation, and approval gates.
Prepares system for future action without enabling any action.
"""

from .intent_mediator import (
    IntentMediator,
    Intent,
    IntentType,
    IntentPriority,
    IntentJustification,
    IntentRiskAssessment,
    IntentApprovalRecord,
    RiskLevel,
    ApprovalStatus,
)

from .dry_run_simulator import (
    DryRunSimulator,
    SimulationResult,
    SimulationOutcome,
    SimulationStatus,
)

from .approval_gate import (
    ApprovalGate,
    ApprovalCriteria,
    ApprovalDecisionRecord,
    ApprovalMethod,
    ApprovalDecision,
)

from .orchestrator import (
    IntentOrchestrator,
    CognitivePipeline,
)

__all__ = [
    # Intent mediation
    'IntentMediator',
    'Intent',
    'IntentType',
    'IntentPriority',
    'IntentJustification',
    'IntentRiskAssessment',
    'IntentApprovalRecord',
    'RiskLevel',
    'ApprovalStatus',
    # Dry-run simulation
    'DryRunSimulator',
    'SimulationResult',
    'SimulationOutcome',
    'SimulationStatus',
    # Approval gate
    'ApprovalGate',
    'ApprovalCriteria',
    'ApprovalDecisionRecord',
    'ApprovalMethod',
    'ApprovalDecision',
    # Orchestration
    'IntentOrchestrator',
    'CognitivePipeline',
]
