"""
Phase 5.1.5: Intent Orchestrator

Orchestrates intent mediation, simulation, and approval.
Central coordinator for cognitive grounding.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import time
import json

from .intent_mediator import IntentMediator, Intent, IntentType, RiskLevel
from .dry_run_simulator import DryRunSimulator, SimulationResult
from .approval_gate import ApprovalGate, ApprovalMethod, ApprovalDecision


@dataclass
class CognitivePipeline:
    """Complete cognitive pipeline: Intent → Justify → Risk → Simulate → Approve."""
    
    pipeline_id: str
    intent: Intent
    
    # Pipeline stages
    has_justification: bool = False
    has_risk_assessment: bool = False
    has_simulation: bool = False
    has_approval: bool = False
    
    # Results
    simulation_result: Optional[SimulationResult] = None
    approval_method: Optional[ApprovalMethod] = None
    approval_decision: Optional[Dict[str, Any]] = None
    
    # Status
    status: str = "created"  # created, justified, risk_assessed, simulated, approved, rejected
    
    # Timestamps
    created_timestamp: float = field(default_factory=time.time)
    completed_timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'pipeline_id': self.pipeline_id,
            'intent_id': self.intent.intent_id,
            'has_justification': self.has_justification,
            'has_risk_assessment': self.has_risk_assessment,
            'has_simulation': self.has_simulation,
            'has_approval': self.has_approval,
            'status': self.status,
            'approval_method': self.approval_method.value if self.approval_method else None,
            'approval_decision': self.approval_decision,
            'created_timestamp': self.created_timestamp,
            'completed_timestamp': self.completed_timestamp,
        }


class IntentOrchestrator:
    """Orchestrates complete intent workflow."""
    
    def __init__(
        self,
        mediator: Optional[IntentMediator] = None,
        simulator: Optional[DryRunSimulator] = None,
        approval_gate: Optional[ApprovalGate] = None,
    ):
        """Initialize orchestrator."""
        self._mediator = mediator or IntentMediator()
        self._simulator = simulator or DryRunSimulator()
        self._approval_gate = approval_gate or ApprovalGate()
        
        self._pipelines: Dict[str, CognitivePipeline] = {}
        self._pipeline_counter = 0
        self._is_enabled = True
    
    def start_pipeline(
        self,
        action_name: str,
        intent_type: IntentType,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> CognitivePipeline:
        """Start a cognitive pipeline for an intent."""
        if not self._is_enabled:
            return None
        
        # Create intent
        intent = self._mediator.create_intent(
            action_name=action_name,
            intent_type=intent_type,
            parameters=parameters or {},
        )
        
        # Create pipeline
        pipeline_id = f"pipeline_{self._pipeline_counter:06d}"
        self._pipeline_counter += 1
        
        pipeline = CognitivePipeline(
            pipeline_id=pipeline_id,
            intent=intent,
        )
        
        self._pipelines[pipeline_id] = pipeline
        return pipeline
    
    def add_justification_to_pipeline(
        self,
        pipeline: CognitivePipeline,
        primary_goal: str,
        reasoning_chain: List[str],
        expected_outcome: str,
        confidence: float = 0.8,
    ) -> CognitivePipeline:
        """Add justification stage to pipeline."""
        if not self._is_enabled:
            return pipeline
        
        self._mediator.add_justification(
            pipeline.intent,
            primary_goal=primary_goal,
            reasoning_chain=reasoning_chain,
            expected_outcome=expected_outcome,
            confidence=confidence,
        )
        
        pipeline.has_justification = True
        pipeline.status = "justified"
        
        return pipeline
    
    def add_risk_assessment_to_pipeline(
        self,
        pipeline: CognitivePipeline,
        risk_level: RiskLevel,
        potential_harms: Optional[List[str]] = None,
        affected_systems: Optional[List[str]] = None,
    ) -> CognitivePipeline:
        """Add risk assessment stage to pipeline."""
        if not self._is_enabled:
            return pipeline
        
        self._mediator.add_risk_assessment(
            pipeline.intent,
            risk_level=risk_level,
            potential_harms=potential_harms or [],
            affected_systems=affected_systems or [],
        )
        
        pipeline.has_risk_assessment = True
        pipeline.status = "risk_assessed"
        
        return pipeline
    
    def add_simulation_to_pipeline(
        self,
        pipeline: CognitivePipeline,
    ) -> CognitivePipeline:
        """Add simulation stage to pipeline."""
        if not self._is_enabled:
            return pipeline
        
        simulation_result = self._simulator.simulate_action(
            intent_id=pipeline.intent.intent_id,
            action_name=pipeline.intent.action_name,
            parameters=pipeline.intent.parameters,
        )
        
        pipeline.simulation_result = simulation_result
        pipeline.has_simulation = True
        pipeline.status = "simulated"
        
        return pipeline
    
    def evaluate_for_approval(
        self,
        pipeline: CognitivePipeline,
    ) -> ApprovalMethod:
        """Evaluate if intent needs human approval."""
        if not self._is_enabled:
            return ApprovalMethod.AUTOMATIC
        
        approval_method = self._approval_gate.evaluate_for_approval(
            pipeline.intent,
            simulation_result=pipeline.simulation_result,
        )
        
        pipeline.approval_method = approval_method
        
        return approval_method
    
    def request_approval(
        self,
        pipeline: CognitivePipeline,
    ) -> Dict[str, Any]:
        """Request approval for intent."""
        if not self._is_enabled:
            return {}
        
        approval_method = self.evaluate_for_approval(pipeline)
        
        approval_request = self._approval_gate.request_approval(
            intent=pipeline.intent,
            approval_method=approval_method,
            simulation_result=pipeline.simulation_result,
        )
        
        pipeline.has_approval = True
        pipeline.status = "approval_requested"
        
        return approval_request
    
    def approve_pipeline(
        self,
        approval_id: str,
        approved_by: str,
        notes: str = "",
    ) -> bool:
        """Approve intent in pipeline."""
        if not self._is_enabled:
            return False
        
        decision = self._approval_gate.approve(
            approval_id=approval_id,
            approved_by=approved_by,
            notes=notes,
        )
        
        if decision:
            # Update pipeline
            for pipeline in self._pipelines.values():
                if pipeline.intent.intent_id == decision.intent_id:
                    pipeline.approval_decision = decision.to_dict()
                    pipeline.status = "approved"
                    pipeline.completed_timestamp = time.time()
                    
                    # Mark intent as approved
                    self._mediator.approve_intent(
                        pipeline.intent,
                        approved_by=approved_by,
                        notes=notes,
                    )
                    
                    return True
        
        return False
    
    def reject_pipeline(
        self,
        approval_id: str,
        rejected_by: str,
        reason: str = "",
    ) -> bool:
        """Reject intent in pipeline."""
        if not self._is_enabled:
            return False
        
        decision = self._approval_gate.reject(
            approval_id=approval_id,
            rejected_by=rejected_by,
            reason=reason,
        )
        
        if decision:
            # Update pipeline
            for pipeline in self._pipelines.values():
                if pipeline.intent.intent_id == decision.intent_id:
                    pipeline.approval_decision = decision.to_dict()
                    pipeline.status = "rejected"
                    pipeline.completed_timestamp = time.time()
                    
                    # Mark intent as rejected
                    self._mediator.reject_intent(
                        pipeline.intent,
                        rejected_by=rejected_by,
                        reason=reason,
                    )
                    
                    return True
        
        return False
    
    def process_pipeline_complete(
        self,
        pipeline: CognitivePipeline,
    ) -> bool:
        """Check if pipeline is complete and ready."""
        required = [
            pipeline.has_justification,
            pipeline.has_risk_assessment,
            pipeline.has_simulation,
            pipeline.has_approval,
        ]
        
        return all(required) and pipeline.status in ["approved", "simulated"]
    
    def get_pipeline(self, pipeline_id: str) -> Optional[CognitivePipeline]:
        """Retrieve pipeline."""
        return self._pipelines.get(pipeline_id)
    
    def list_pipelines(
        self,
        status: Optional[str] = None,
    ) -> List[CognitivePipeline]:
        """List pipelines."""
        pipelines = list(self._pipelines.values())
        
        if status:
            pipelines = [p for p in pipelines if p.status == status]
        
        return pipelines
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        pipelines = list(self._pipelines.values())
        
        return {
            'enabled': self._is_enabled,
            'total_pipelines': len(pipelines),
            'justification_count': sum(1 for p in pipelines if p.has_justification),
            'risk_assessed_count': sum(1 for p in pipelines if p.has_risk_assessment),
            'simulated_count': sum(1 for p in pipelines if p.has_simulation),
            'approved_count': sum(1 for p in pipelines if p.status == "approved"),
            'rejected_count': sum(1 for p in pipelines if p.status == "rejected"),
        }
    
    def enable(self) -> None:
        """Enable orchestration."""
        self._is_enabled = True
    
    def disable(self) -> None:
        """Disable orchestration (reversible)."""
        self._is_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if enabled."""
        return self._is_enabled


if __name__ == "__main__":
    # Demo
    orchestrator = IntentOrchestrator()
    
    # Start pipeline
    pipeline = orchestrator.start_pipeline(
        action_name="click_button",
        intent_type=IntentType.INTERACTION,
        parameters={"x": 100, "y": 50},
    )
    
    print(f"Pipeline: {pipeline.pipeline_id}")
    print(f"Intent: {pipeline.intent.intent_id}")
    
    # Add justification
    orchestrator.add_justification_to_pipeline(
        pipeline,
        primary_goal="Submit form",
        reasoning_chain=["Form complete", "Ready to submit"],
        expected_outcome="Form submitted",
    )
    
    print(f"After justification: {pipeline.status}")
    
    # Add risk assessment
    orchestrator.add_risk_assessment_to_pipeline(
        pipeline,
        risk_level=RiskLevel.LOW,
    )
    
    print(f"After risk assessment: {pipeline.status}")
    
    # Add simulation
    orchestrator.add_simulation_to_pipeline(pipeline)
    
    print(f"After simulation: {pipeline.status}")
    print(f"Simulation safe: {pipeline.simulation_result.is_safe_to_execute()}")
    
    print(f"\nOrchestrator status: {orchestrator.get_status()}")
