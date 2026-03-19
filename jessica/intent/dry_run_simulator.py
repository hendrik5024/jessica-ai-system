"""
Phase 5.1.5: Dry-Run Simulation

Simulates intended actions using perception-only data.
No actual action execution - testing ground for cognitive grounding.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
import time
import json


class SimulationStatus(Enum):
    """Status of a dry-run simulation."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SimulationOutcome:
    """Predicted outcome of a simulated action."""
    
    success_probability: float  # 0.0 to 1.0
    expected_state_changes: Dict[str, Any] = field(default_factory=dict)
    potential_side_effects: List[str] = field(default_factory=list)
    estimated_duration_ms: float = 0.0
    confidence_level: float = 0.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success_probability': self.success_probability,
            'expected_state_changes': self.expected_state_changes,
            'potential_side_effects': self.potential_side_effects,
            'estimated_duration_ms': self.estimated_duration_ms,
            'confidence_level': self.confidence_level,
        }


@dataclass
class SimulationResult:
    """Result of a dry-run simulation."""
    
    simulation_id: str
    intent_id: str
    status: SimulationStatus
    
    # Simulation details
    action_simulated: str
    parameters_used: Dict[str, Any] = field(default_factory=dict)
    
    # Outcome prediction
    predicted_outcome: Optional[SimulationOutcome] = None
    
    # Impact analysis
    ui_impact: Dict[str, Any] = field(default_factory=dict)  # UI changes
    system_impact: Dict[str, Any] = field(default_factory=dict)  # System state
    
    # Warnings and issues
    warnings: List[str] = field(default_factory=list)
    issues_detected: List[str] = field(default_factory=list)
    
    # Timestamps
    started_timestamp: float = field(default_factory=time.time)
    completed_timestamp: Optional[float] = None
    duration_ms: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'simulation_id': self.simulation_id,
            'intent_id': self.intent_id,
            'status': self.status.value,
            'action_simulated': self.action_simulated,
            'parameters_used': self.parameters_used,
            'predicted_outcome': self.predicted_outcome.to_dict() if self.predicted_outcome else None,
            'ui_impact': self.ui_impact,
            'system_impact': self.system_impact,
            'warnings': self.warnings,
            'issues_detected': self.issues_detected,
            'started_timestamp': self.started_timestamp,
            'completed_timestamp': self.completed_timestamp,
            'duration_ms': self.duration_ms,
            'metadata': self.metadata,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def is_safe_to_execute(self) -> bool:
        """Check if simulation indicates safe execution."""
        # Safe if no critical issues
        critical_issues = [i for i in self.issues_detected if "critical" in i.lower()]
        if critical_issues:
            return False
        
        # Safe if outcome probability high enough
        if self.predicted_outcome and self.predicted_outcome.success_probability < 0.7:
            return False
        
        return True


class DryRunSimulator:
    """Simulates intended actions using perception data."""
    
    def __init__(self, perception_manager=None):
        """Initialize simulator."""
        self._perception_manager = perception_manager
        self._simulations: Dict[str, SimulationResult] = {}
        self._simulation_counter = 0
        self._is_enabled = True
        self._action_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default action simulation handlers."""
        self._action_handlers['click'] = self._simulate_click
        self._action_handlers['type'] = self._simulate_type
        self._action_handlers['navigate'] = self._simulate_navigate
        self._action_handlers['query'] = self._simulate_query
    
    def _simulate_click(
        self,
        parameters: Dict[str, Any],
    ) -> SimulationOutcome:
        """Simulate mouse click action."""
        x = parameters.get('x', 0)
        y = parameters.get('y', 0)
        button = parameters.get('button', 'left')
        
        # Check if coordinates are within screen bounds
        outcome = SimulationOutcome(
            success_probability=0.85,
            expected_state_changes={
                'ui_state': 'potentially_changed',
                'mouse_position': (x, y),
                'click_registered': True,
            },
            potential_side_effects=['window_focus_change', 'application_response'],
            estimated_duration_ms=100.0,
            confidence_level=0.8,
        )
        
        return outcome
    
    def _simulate_type(
        self,
        parameters: Dict[str, Any],
    ) -> SimulationOutcome:
        """Simulate keyboard text input."""
        text = parameters.get('text', '')
        target_field = parameters.get('target_field', 'unknown')
        
        outcome = SimulationOutcome(
            success_probability=0.9,
            expected_state_changes={
                'text_input': text,
                'target_field': target_field,
                'field_modified': True,
                'text_length': len(text),
            },
            potential_side_effects=['form_validation', 'auto_complete'],
            estimated_duration_ms=len(text) * 50.0,
            confidence_level=0.85,
        )
        
        return outcome
    
    def _simulate_navigate(
        self,
        parameters: Dict[str, Any],
    ) -> SimulationOutcome:
        """Simulate navigation action."""
        target_url = parameters.get('url', '')
        method = parameters.get('method', 'get')
        
        outcome = SimulationOutcome(
            success_probability=0.75,
            expected_state_changes={
                'url': target_url,
                'page_load': True,
                'navigation_method': method,
            },
            potential_side_effects=['network_request', 'page_render', 'script_execution'],
            estimated_duration_ms=2000.0,
            confidence_level=0.7,
        )
        
        return outcome
    
    def _simulate_query(
        self,
        parameters: Dict[str, Any],
    ) -> SimulationOutcome:
        """Simulate system query (observation)."""
        query_type = parameters.get('query_type', 'state')
        
        outcome = SimulationOutcome(
            success_probability=0.98,
            expected_state_changes={
                'query_executed': True,
                'data_retrieved': True,
                'query_type': query_type,
            },
            potential_side_effects=['logging', 'caching'],
            estimated_duration_ms=10.0,
            confidence_level=0.95,
        )
        
        return outcome
    
    def register_action_handler(
        self,
        action_name: str,
        handler: Callable,
    ) -> None:
        """Register custom action simulation handler."""
        self._action_handlers[action_name] = handler
    
    def simulate_action(
        self,
        intent_id: str,
        action_name: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SimulationResult:
        """Simulate an intended action."""
        if not self._is_enabled:
            return None
        
        simulation_id = f"sim_{self._simulation_counter:06d}"
        self._simulation_counter += 1
        
        start_time = time.time()
        
        # Get outcome using registered handler
        handler = self._action_handlers.get(action_name)
        if handler is None:
            predicted_outcome = SimulationOutcome(
                success_probability=0.5,
                confidence_level=0.3,
            )
        else:
            predicted_outcome = handler(parameters)
        
        # Create perception snapshot if available
        ui_impact = {}
        if self._perception_manager:
            try:
                snapshot = self._perception_manager.perceive_environment()
                if snapshot:
                    ui_impact = {
                        'current_window': str(snapshot.active_window),
                        'cursor_position': snapshot.cursor_position,
                    }
            except:
                pass
        
        # Check for potential issues
        issues = []
        if predicted_outcome.success_probability < 0.6:
            issues.append("warning: low success probability")
        if parameters.get('x', -1) < 0 or parameters.get('y', -1) < 0:
            issues.append("warning: invalid coordinates")
        
        duration = (time.time() - start_time) * 1000
        
        result = SimulationResult(
            simulation_id=simulation_id,
            intent_id=intent_id,
            status=SimulationStatus.COMPLETED,
            action_simulated=action_name,
            parameters_used=parameters,
            predicted_outcome=predicted_outcome,
            ui_impact=ui_impact,
            issues_detected=issues,
            completed_timestamp=time.time(),
            duration_ms=duration,
            metadata=metadata or {},
        )
        
        self._simulations[simulation_id] = result
        return result
    
    def batch_simulate(
        self,
        intents: List[Dict[str, Any]],
    ) -> List[SimulationResult]:
        """Simulate multiple intents."""
        results = []
        for intent_data in intents:
            result = self.simulate_action(
                intent_id=intent_data.get('intent_id'),
                action_name=intent_data.get('action_name'),
                parameters=intent_data.get('parameters', {}),
                metadata=intent_data.get('metadata'),
            )
            results.append(result)
        
        return results
    
    def get_simulation(self, simulation_id: str) -> Optional[SimulationResult]:
        """Retrieve a simulation result."""
        return self._simulations.get(simulation_id)
    
    def list_simulations(
        self,
        intent_id: Optional[str] = None,
        status: Optional[SimulationStatus] = None,
    ) -> List[SimulationResult]:
        """List simulations, optionally filtered."""
        sims = list(self._simulations.values())
        
        if intent_id:
            sims = [s for s in sims if s.intent_id == intent_id]
        
        if status:
            sims = [s for s in sims if s.status == status]
        
        return sims
    
    def get_status(self) -> Dict[str, Any]:
        """Get simulator status."""
        completed = len(self.list_simulations(status=SimulationStatus.COMPLETED))
        return {
            'enabled': self._is_enabled,
            'total_simulations': len(self._simulations),
            'completed_simulations': completed,
            'registered_handlers': list(self._action_handlers.keys()),
        }
    
    def enable(self) -> None:
        """Enable simulations."""
        self._is_enabled = True
    
    def disable(self) -> None:
        """Disable simulations (reversible)."""
        self._is_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if enabled."""
        return self._is_enabled


if __name__ == "__main__":
    # Demo
    simulator = DryRunSimulator()
    
    # Simulate click
    result = simulator.simulate_action(
        intent_id="intent_000001",
        action_name="click",
        parameters={"x": 100, "y": 50, "button": "left"},
    )
    
    print(f"Simulation: {result.simulation_id}")
    print(f"Status: {result.status.value}")
    print(f"Safe to execute: {result.is_safe_to_execute()}")
    print(f"\nSimulation JSON:\n{result.to_json()}")
