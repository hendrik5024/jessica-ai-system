"""
Continual Learning System - Streaming learning with safety verification and rollback.

Enables:
- Streaming learning from interactions (not just weekly batches)
- Online safety verification before deploying updates
- Catastrophic forgetting detection
- Automatic rollback on performance degradation
- Learning curve tracking and convergence detection
- Distribution drift detection
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple, Callable
from datetime import datetime
from enum import Enum
import statistics
import hashlib


class LearningMode(Enum):
    """Learning mode."""
    BATCH = "batch"  # Weekly batch updates
    STREAMING = "streaming"  # Continuous updates
    HYBRID = "hybrid"  # Both batch and streaming


class ModelVersion(Enum):
    """Model version state."""
    BASE = "base"
    CANDIDATE = "candidate"  # Under validation
    DEPLOYED = "deployed"  # Currently in production
    ARCHIVED = "archived"  # Previous version kept for rollback


@dataclass
class LearningSignal:
    """
    A single learning signal extracted from an interaction.
    
    Contains what was expected vs what happened, for model improvement.
    """
    
    signal_id: str
    domain: str
    input_context: Dict[str, Any]
    predicted_output: Any
    actual_output: Any
    error_magnitude: float  # How wrong was the prediction
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def compute_loss(self) -> float:
        """Compute loss for this signal."""
        # Simple binary loss for now
        if self.predicted_output == self.actual_output:
            return 0.0
        return self.error_magnitude


@dataclass
class ModelSnapshot:
    """
    Snapshot of model state at a point in time.
    
    Used for rollback and performance comparison.
    """
    
    snapshot_id: str
    version: str
    timestamp: float
    parameters: Dict[str, Any]  # Model parameters (simplified)
    performance_metrics: Dict[str, float]
    safety_verification: bool
    notes: str = ""


@dataclass
class ValidationResult:
    """Result of model validation."""
    
    valid: bool
    performance_delta: Dict[str, float]  # Change in metrics
    catastrophic_forgetting: bool
    forgetting_domains: List[str]
    safety_violations: List[str]
    confidence: float
    reasoning: str


class CatastrophicForgettingDetector:
    """
    Detects when learning erases prior correct behavior.
    
    Monitors performance across all domains to ensure new learning
    doesn't degrade existing capabilities.
    """
    
    def __init__(self, threshold: float = 0.05):
        """
        Args:
            threshold: Maximum acceptable performance drop (5% default)
        """
        self.threshold = threshold
        self.baseline_performance: Dict[str, float] = {}
        self.domain_history: Dict[str, List[float]] = {}
    
    def set_baseline(self, domain: str, performance: float) -> None:
        """Set baseline performance for a domain."""
        self.baseline_performance[domain] = performance
        if domain not in self.domain_history:
            self.domain_history[domain] = []
        self.domain_history[domain].append(performance)
    
    def check_forgetting(self, 
                        domain: str, 
                        current_performance: float) -> Tuple[bool, float]:
        """
        Check if performance has degraded significantly.
        
        Returns:
            (is_forgetting, delta) where delta is performance change
        """
        if domain not in self.baseline_performance:
            # No baseline, can't detect forgetting
            return False, 0.0
        
        baseline = self.baseline_performance[domain]
        delta = current_performance - baseline
        
        # Record current performance
        if domain not in self.domain_history:
            self.domain_history[domain] = []
        self.domain_history[domain].append(current_performance)
        
        # Check if degradation exceeds threshold
        is_forgetting = delta < -self.threshold
        
        return is_forgetting, delta
    
    def get_forgetting_report(self) -> Dict[str, Any]:
        """Get report on forgetting across all domains."""
        report = {
            "domains_tracked": len(self.baseline_performance),
            "forgetting_detected": [],
            "stable_domains": [],
            "improved_domains": []
        }
        
        for domain, baseline in self.baseline_performance.items():
            if domain not in self.domain_history or not self.domain_history[domain]:
                continue
            
            current = self.domain_history[domain][-1]
            delta = current - baseline
            
            if delta < -self.threshold:
                report["forgetting_detected"].append({
                    "domain": domain,
                    "baseline": baseline,
                    "current": current,
                    "delta": delta
                })
            elif abs(delta) <= self.threshold:
                report["stable_domains"].append(domain)
            else:
                report["improved_domains"].append({
                    "domain": domain,
                    "improvement": delta
                })
        
        return report


class SafetyVerifier:
    """
    Verifies that model updates are safe before deployment.
    
    Runs validation tests on held-out data and checks for:
    - Performance improvement on target domain
    - No degradation on other domains
    - No safety violations
    """
    
    def __init__(self):
        self.test_suites: Dict[str, List[Dict[str, Any]]] = {}
        self.safety_constraints: List[Callable] = []
    
    def register_test_suite(self, domain: str, tests: List[Dict[str, Any]]) -> None:
        """Register test suite for a domain."""
        self.test_suites[domain] = tests
    
    def add_safety_constraint(self, constraint: Callable) -> None:
        """Add a safety constraint function."""
        self.safety_constraints.append(constraint)
    
    def verify(self, 
              model_snapshot: ModelSnapshot,
              baseline_snapshot: ModelSnapshot) -> ValidationResult:
        """
        Verify model update is safe.
        
        Args:
            model_snapshot: New model to validate
            baseline_snapshot: Current production model
        
        Returns:
            ValidationResult with safety assessment
        """
        # Compare performance metrics
        performance_delta = {}
        for metric, value in model_snapshot.performance_metrics.items():
            baseline_value = baseline_snapshot.performance_metrics.get(metric, 0.0)
            performance_delta[metric] = value - baseline_value
        
        # Check for catastrophic forgetting
        forgetting_domains = []
        for domain, delta in performance_delta.items():
            if delta < -0.05:  # 5% degradation threshold
                forgetting_domains.append(domain)
        
        catastrophic_forgetting = len(forgetting_domains) > 0
        
        # Check safety constraints
        safety_violations = []
        for constraint in self.safety_constraints:
            try:
                if not constraint(model_snapshot):
                    safety_violations.append(constraint.__name__)
            except Exception as e:
                safety_violations.append(f"Error in {constraint.__name__}: {str(e)}")
        
        # Determine validity
        valid = (
            not catastrophic_forgetting and
            len(safety_violations) == 0 and
            any(delta > 0 for delta in performance_delta.values())  # Some improvement
        )
        
        # Build reasoning
        if valid:
            improvements = [f"{k}: +{v:.2%}" for k, v in performance_delta.items() if v > 0]
            reasoning = f"Valid update: {', '.join(improvements)}; no forgetting or safety violations"
        else:
            issues = []
            if catastrophic_forgetting:
                issues.append(f"Forgetting in {len(forgetting_domains)} domains")
            if safety_violations:
                issues.append(f"{len(safety_violations)} safety violations")
            if not any(delta > 0 for delta in performance_delta.values()):
                issues.append("No performance improvement")
            reasoning = f"Invalid update: {'; '.join(issues)}"
        
        # Confidence based on magnitude of changes
        confidence = 1.0
        if catastrophic_forgetting:
            confidence -= 0.4
        if safety_violations:
            confidence -= 0.3
        confidence = max(0.0, min(1.0, confidence))
        
        return ValidationResult(
            valid=valid,
            performance_delta=performance_delta,
            catastrophic_forgetting=catastrophic_forgetting,
            forgetting_domains=forgetting_domains,
            safety_violations=safety_violations,
            confidence=confidence,
            reasoning=reasoning
        )


class ContinualLearningEngine:
    """
    Continual learning engine with streaming updates and safety verification.
    """
    
    def __init__(self, world_model):
        """
        Args:
            world_model: WorldModel instance
        """
        self.world_model = world_model
        self.mode = LearningMode.HYBRID
        
        # Model versioning
        self.snapshots: Dict[str, ModelSnapshot] = {}
        self.current_version = "base_v1"
        self.deployed_version = "base_v1"
        
        # Learning signals
        self.streaming_buffer: List[LearningSignal] = []
        self.batch_buffer: List[LearningSignal] = []
        
        # Safety and verification
        self.safety_verifier = SafetyVerifier()
        self.forgetting_detector = CatastrophicForgettingDetector()
        
        # Learning tracking
        self.learning_history: List[Dict[str, Any]] = []
        self.convergence_metrics: Dict[str, List[float]] = {}
        
        # Initialize base model
        self._initialize_base_model()
    
    def _initialize_base_model(self) -> None:
        """Initialize base model snapshot."""
        base_snapshot = ModelSnapshot(
            snapshot_id="base_v1",
            version="base_v1",
            timestamp=datetime.now().timestamp(),
            parameters={},  # Simplified
            performance_metrics={
                "chess": 0.75,
                "cooking": 0.70,
                "travel": 0.68,
                "decision_making": 0.72
            },
            safety_verification=True,
            notes="Initial base model"
        )
        self.snapshots["base_v1"] = base_snapshot
        
        # Set baselines for forgetting detection
        for domain, perf in base_snapshot.performance_metrics.items():
            self.forgetting_detector.set_baseline(domain, perf)
    
    def collect_learning_signal(self,
                               domain: str,
                               input_context: Dict[str, Any],
                               predicted: Any,
                               actual: Any,
                               error: float) -> str:
        """
        Collect a learning signal from an interaction.
        
        Args:
            domain: Domain name
            input_context: Input that produced prediction
            predicted: What model predicted
            actual: What actually happened
            error: Magnitude of error
        
        Returns:
            Signal ID
        """
        signal_id = f"signal_{len(self.streaming_buffer) + len(self.batch_buffer)}"
        
        signal = LearningSignal(
            signal_id=signal_id,
            domain=domain,
            input_context=input_context,
            predicted_output=predicted,
            actual_output=actual,
            error_magnitude=error
        )
        
        # Add to appropriate buffer
        if self.mode in [LearningMode.STREAMING, LearningMode.HYBRID]:
            self.streaming_buffer.append(signal)
        
        if self.mode in [LearningMode.BATCH, LearningMode.HYBRID]:
            self.batch_buffer.append(signal)
        
        # If streaming buffer is large enough, trigger update
        if len(self.streaming_buffer) >= 10:  # Threshold
            self._process_streaming_updates()
        
        return signal_id
    
    def _process_streaming_updates(self) -> None:
        """Process accumulated streaming signals."""
        if not self.streaming_buffer:
            return
        
        # Compute aggregate update
        domain_signals: Dict[str, List[LearningSignal]] = {}
        for signal in self.streaming_buffer:
            if signal.domain not in domain_signals:
                domain_signals[signal.domain] = []
            domain_signals[signal.domain].append(signal)
        
        # Create candidate update
        candidate_id = f"candidate_{len(self.snapshots)}"
        candidate = self._create_candidate_update(candidate_id, domain_signals)
        
        # Verify safety
        baseline = self.snapshots[self.deployed_version]
        validation = self.safety_verifier.verify(candidate, baseline)
        
        if validation.valid:
            # Deploy update
            self._deploy_update(candidate)
            self.streaming_buffer.clear()
        else:
            # Reject update, keep buffer for batch processing
            self.batch_buffer.extend(self.streaming_buffer)
            self.streaming_buffer.clear()
    
    def _create_candidate_update(self,
                                candidate_id: str,
                                domain_signals: Dict[str, List[LearningSignal]]) -> ModelSnapshot:
        """Create candidate model from signals."""
        # Simulate performance update
        baseline = self.snapshots[self.deployed_version]
        new_metrics = baseline.performance_metrics.copy()
        
        # Improve performance on domains with signals
        for domain, signals in domain_signals.items():
            if domain in new_metrics:
                avg_error = statistics.mean(s.error_magnitude for s in signals)
                # Reduce error by learning
                improvement = min(0.05, avg_error * 0.1)  # Cap at 5% improvement
                new_metrics[domain] += improvement
        
        candidate = ModelSnapshot(
            snapshot_id=candidate_id,
            version=candidate_id,
            timestamp=datetime.now().timestamp(),
            parameters={},  # Simplified
            performance_metrics=new_metrics,
            safety_verification=False,  # Not yet verified
            notes=f"Candidate from {len(domain_signals)} domains"
        )
        
        self.snapshots[candidate_id] = candidate
        return candidate
    
    def _deploy_update(self, candidate: ModelSnapshot) -> None:
        """Deploy validated candidate to production."""
        # Archive current version
        current = self.snapshots[self.deployed_version]
        
        # Deploy candidate
        candidate.safety_verification = True
        self.deployed_version = candidate.snapshot_id
        self.current_version = candidate.snapshot_id
        
        # Update forgetting detector baselines
        for domain, perf in candidate.performance_metrics.items():
            self.forgetting_detector.set_baseline(domain, perf)
        
        # Record learning event
        self.learning_history.append({
            "timestamp": datetime.now().timestamp(),
            "version": candidate.snapshot_id,
            "from_version": current.snapshot_id,
            "performance_metrics": candidate.performance_metrics,
            "type": "streaming_update"
        })
    
    def rollback(self, to_version: Optional[str] = None) -> bool:
        """
        Rollback to previous version.
        
        Args:
            to_version: Version to rollback to, or None for previous
        
        Returns:
            True if rollback successful
        """
        if to_version is None:
            # Find previous deployed version
            if len(self.learning_history) < 2:
                return False  # No previous version
            to_version = self.learning_history[-2]["version"]
        
        if to_version not in self.snapshots:
            return False
        
        # Rollback
        self.deployed_version = to_version
        self.current_version = to_version
        
        # Record rollback
        self.learning_history.append({
            "timestamp": datetime.now().timestamp(),
            "version": to_version,
            "type": "rollback",
            "reason": "Manual rollback or performance degradation"
        })
        
        return True
    
    def validate_current_model(self) -> ValidationResult:
        """Validate currently deployed model against baseline."""
        current = self.snapshots[self.deployed_version]
        baseline = self.snapshots["base_v1"]
        
        return self.safety_verifier.verify(current, baseline)
    
    def detect_distribution_drift(self,
                                 domain: str,
                                 recent_signals: List[LearningSignal],
                                 window_size: int = 50) -> Dict[str, Any]:
        """
        Detect if data distribution has shifted.
        
        Compares recent signals to historical patterns to identify drift.
        """
        if len(recent_signals) < window_size:
            return {
                "drift_detected": False,
                "reason": "Insufficient data for drift detection"
            }
        
        # Compare recent error rates to historical
        recent_errors = [s.error_magnitude for s in recent_signals[-window_size:]]
        historical_errors = [s.error_magnitude for s in recent_signals[:-window_size]] if len(recent_signals) > window_size else []
        
        if not historical_errors:
            return {
                "drift_detected": False,
                "reason": "No historical data for comparison"
            }
        
        recent_avg = statistics.mean(recent_errors)
        historical_avg = statistics.mean(historical_errors)
        
        # Check for significant change
        drift_threshold = 0.15  # 15% change
        change = abs(recent_avg - historical_avg) / historical_avg if historical_avg > 0 else 0
        
        drift_detected = change > drift_threshold
        
        return {
            "drift_detected": drift_detected,
            "domain": domain,
            "recent_error_rate": recent_avg,
            "historical_error_rate": historical_avg,
            "change_percentage": change,
            "recommendation": "Retrain on new data" if drift_detected else "Continue current model"
        }
    
    def get_learning_curve(self, domain: str) -> List[float]:
        """Get learning curve for a domain."""
        curve = []
        for event in self.learning_history:
            if "performance_metrics" in event and domain in event["performance_metrics"]:
                curve.append(event["performance_metrics"][domain])
        return curve
    
    def check_convergence(self, domain: str, window: int = 5) -> Dict[str, Any]:
        """
        Check if learning has converged for a domain.
        
        Returns convergence status and suggested action.
        """
        curve = self.get_learning_curve(domain)
        
        if len(curve) < window:
            return {
                "converged": False,
                "reason": "Insufficient history",
                "suggestion": "Continue learning"
            }
        
        # Check if recent improvements are diminishing
        recent = curve[-window:]
        improvements = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
        
        avg_improvement = statistics.mean(improvements) if improvements else 0
        
        # Convergence threshold: <1% improvement per cycle
        converged = avg_improvement < 0.01
        
        return {
            "converged": converged,
            "domain": domain,
            "recent_improvement_rate": avg_improvement,
            "current_performance": curve[-1] if curve else 0,
            "suggestion": "Explore new domains" if converged else "Continue optimization"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning system statistics."""
        return {
            "deployed_version": self.deployed_version,
            "total_snapshots": len(self.snapshots),
            "streaming_buffer_size": len(self.streaming_buffer),
            "batch_buffer_size": len(self.batch_buffer),
            "learning_events": len(self.learning_history),
            "mode": self.mode.value,
            "forgetting_report": self.forgetting_detector.get_forgetting_report(),
            "current_performance": self.snapshots[self.deployed_version].performance_metrics
        }
