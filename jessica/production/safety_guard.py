"""
Phase 4: Safety Guard and Rollback System

Prevents failures and enables fast recovery.
- Operator output validation (invariant checks)
- Resource limit enforcement (memory, timeout)
- Automatic fallback to Phase 3 baseline
- Rollback tracking and logging
- Safety intervention recording
"""

from __future__ import annotations

import time
import psutil
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Callable
from collections import deque


class SafetyViolationType(Enum):
    """Types of safety violations."""
    INVARIANT_VIOLATION = "invariant_violation"
    MEMORY_EXCEEDED = "memory_exceeded"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    INVALID_OUTPUT = "invalid_output"
    EXCEPTION_RAISED = "exception_raised"
    RESOURCE_UNAVAILABLE = "resource_unavailable"


class RollbackTrigger(Enum):
    """Reasons for rollback."""
    SAFETY_VIOLATION = "safety_violation"
    MANUAL_OVERRIDE = "manual_override"
    HEALTH_CHECK_FAILURE = "health_check_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"


@dataclass
class SafetyViolation:
    """Record of a safety violation."""
    violation_type: SafetyViolationType
    operator_name: str
    timestamp: float
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "warning"  # warning | error | critical
    resolved: bool = False
    resolution_method: Optional[str] = None
    
    def mark_resolved(self, method: str):
        """Mark violation as resolved."""
        self.resolved = True
        self.resolution_method = method


@dataclass
class RollbackRecord:
    """Record of a rollback event."""
    rollback_id: str
    trigger: RollbackTrigger
    timestamp: float
    duration_sec: Optional[float] = None
    success: bool = False
    reason: str = ""
    violations_count: int = 0
    recovery_chain_id: Optional[str] = None


class OperatorInvariantValidator:
    """Validates operator outputs against expected invariants."""
    
    def __init__(self):
        """Initialize validator."""
        self.invariants: Dict[str, list[Callable]] = {}
    
    def register_invariant(self, operator_name: str, check_fn: Callable[[Dict], bool]):
        """Register invariant check for operator."""
        if operator_name not in self.invariants:
            self.invariants[operator_name] = []
        self.invariants[operator_name].append(check_fn)
    
    def validate(self, operator_name: str, output: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate operator output against invariants."""
        errors = []
        
        if operator_name not in self.invariants:
            return True, []  # No invariants registered
        
        for i, check_fn in enumerate(self.invariants[operator_name]):
            try:
                if not check_fn(output):
                    errors.append(f"Invariant {i} failed for {operator_name}")
            except Exception as e:
                errors.append(f"Invariant check {i} raised exception: {str(e)}")
        
        return len(errors) == 0, errors


class ResourceMonitor:
    """Monitors system resource usage."""
    
    def __init__(self, memory_limit_mb: int = 500, timeout_sec: int = 30):
        """Initialize resource monitor."""
        self.memory_limit_mb = memory_limit_mb
        self.timeout_sec = timeout_sec
        self.process = psutil.Process()
    
    def check_memory(self) -> tuple[bool, Optional[str]]:
        """Check if memory usage is within limits."""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            if memory_mb > self.memory_limit_mb:
                return False, f"Memory exceeded: {memory_mb:.1f}MB > {self.memory_limit_mb}MB"
            return True, None
        except Exception as e:
            return False, f"Memory check failed: {str(e)}"
    
    def check_timeout(self, start_time: float) -> tuple[bool, Optional[str]]:
        """Check if operation exceeded timeout."""
        elapsed = time.time() - start_time
        if elapsed > self.timeout_sec:
            return False, f"Timeout exceeded: {elapsed:.1f}s > {self.timeout_sec}s"
        return True, None
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / 1024 / 1024
        except:
            return 0.0


class RollbackManager:
    """Manages rollback operations and recovery."""
    
    def __init__(self, phase_3_baseline_path: Optional[str] = None):
        """Initialize rollback manager."""
        self.phase_3_baseline_path = phase_3_baseline_path
        self.rollback_records: deque = deque(maxlen=100)
        self._lock = threading.RLock()
        self._is_phase_3_available = phase_3_baseline_path is not None
        self._rollback_in_progress = False
    
    def perform_rollback(
        self,
        trigger: RollbackTrigger,
        reason: str = "",
        violations_count: int = 0,
    ) -> tuple[bool, str]:
        """Perform rollback to Phase 3 baseline."""
        if self._rollback_in_progress:
            return False, "Rollback already in progress"
        
        if not self._is_phase_3_available:
            return False, "Phase 3 baseline not available"
        
        try:
            self._rollback_in_progress = True
            start_time = time.time()
            
            # Simulate rollback (in production: swap operator implementations)
            rollback_id = f"ROLLBACK_{int(start_time*1e6)}"
            
            # Attempt recovery (placeholder)
            success = self._execute_recovery()
            
            duration = time.time() - start_time
            
            record = RollbackRecord(
                rollback_id=rollback_id,
                trigger=trigger,
                timestamp=start_time,
                duration_sec=duration,
                success=success,
                reason=reason,
                violations_count=violations_count,
            )
            
            with self._lock:
                self.rollback_records.append(record)
            
            if success:
                return True, f"Rollback completed in {duration:.2f}s"
            else:
                return False, f"Rollback failed after {duration:.2f}s"
        
        finally:
            self._rollback_in_progress = False
    
    def _execute_recovery(self) -> bool:
        """Execute actual recovery procedure."""
        # In production, this would:
        # 1. Restore Phase 3 operator implementations
        # 2. Clear Phase 3.5 refined operators
        # 3. Validate state
        # 4. Resume operation
        return True
    
    def get_rollback_status(self) -> Dict[str, Any]:
        """Get rollback system status."""
        with self._lock:
            recent_rollbacks = list(self.rollback_records)[-10:]
            successful = sum(1 for r in recent_rollbacks if r.success)
            
            return {
                'is_phase_3_available': self._is_phase_3_available,
                'rollback_in_progress': self._rollback_in_progress,
                'total_rollbacks': len(self.rollback_records),
                'recent_rollbacks': [
                    {
                        'id': r.rollback_id,
                        'trigger': r.trigger.value,
                        'success': r.success,
                        'duration_sec': r.duration_sec,
                    }
                    for r in recent_rollbacks
                ],
                'success_rate': successful / len(recent_rollbacks) if recent_rollbacks else 0,
            }


class SafetyGuard:
    """Central safety guard system for production."""
    
    def __init__(
        self,
        memory_limit_mb: int = 500,
        timeout_sec: int = 30,
        phase_3_baseline_path: Optional[str] = None,
    ):
        """Initialize safety guard."""
        self.invariant_validator = OperatorInvariantValidator()
        self.resource_monitor = ResourceMonitor(memory_limit_mb, timeout_sec)
        self.rollback_manager = RollbackManager(phase_3_baseline_path)
        
        self.violations: deque = deque(maxlen=1000)
        self._lock = threading.RLock()
        self._enabled = True
    
    def register_operator_invariant(self, operator_name: str, check_fn: Callable):
        """Register invariant check for operator."""
        self.invariant_validator.register_invariant(operator_name, check_fn)
    
    def validate_operator_output(
        self,
        operator_name: str,
        output: Dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Validate operator output."""
        if not self._enabled:
            return True, []
        
        is_valid, errors = self.invariant_validator.validate(operator_name, output)
        
        if not is_valid:
            for error in errors:
                self._record_violation(
                    SafetyViolationType.INVALID_OUTPUT,
                    operator_name,
                    error,
                    "error"
                )
        
        return is_valid, errors
    
    def check_resource_constraints(self, start_time: float) -> tuple[bool, Optional[str]]:
        """Check resource constraints (memory, timeout)."""
        if not self._enabled:
            return True, None
        
        # Check memory
        memory_ok, memory_msg = self.resource_monitor.check_memory()
        if not memory_ok:
            self._record_violation(
                SafetyViolationType.MEMORY_EXCEEDED,
                "system",
                memory_msg or "Memory exceeded",
                "critical"
            )
            return False, memory_msg
        
        # Check timeout
        timeout_ok, timeout_msg = self.resource_monitor.check_timeout(start_time)
        if not timeout_ok:
            self._record_violation(
                SafetyViolationType.TIMEOUT_EXCEEDED,
                "system",
                timeout_msg or "Timeout exceeded",
                "warning"
            )
            return False, timeout_msg
        
        return True, None
    
    def handle_violation(
        self,
        violation_type: SafetyViolationType,
        operator_name: str,
        message: str,
        context: Optional[Dict] = None,
    ) -> tuple[bool, str]:
        """Handle safety violation with potential rollback."""
        self._record_violation(violation_type, operator_name, message, "error", context)
        
        # Decide on rollback
        should_rollback = violation_type in [
            SafetyViolationType.INVARIANT_VIOLATION,
            SafetyViolationType.MEMORY_EXCEEDED,
        ]
        
        if should_rollback and self.rollback_manager._is_phase_3_available:
            trigger = RollbackTrigger.SAFETY_VIOLATION
            success, msg = self.rollback_manager.perform_rollback(
                trigger=trigger,
                reason=f"{violation_type.value}: {message}",
                violations_count=1,
            )
            return success, msg
        
        return False, f"Violation recorded but no rollback performed: {message}"
    
    def _record_violation(
        self,
        violation_type: SafetyViolationType,
        operator_name: str,
        message: str,
        severity: str = "warning",
        context: Optional[Dict] = None,
    ):
        """Record safety violation."""
        violation = SafetyViolation(
            violation_type=violation_type,
            operator_name=operator_name,
            timestamp=time.time(),
            message=message,
            context=context or {},
            severity=severity,
        )
        
        with self._lock:
            self.violations.append(violation)
    
    def get_violations(self, limit: int = 100) -> list[SafetyViolation]:
        """Get recent violations."""
        with self._lock:
            return list(self.violations)[-limit:]
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status."""
        with self._lock:
            violations_list = list(self.violations)
            critical_count = sum(1 for v in violations_list if v.severity == "critical")
            error_count = sum(1 for v in violations_list if v.severity == "error")
        
        return {
            'enabled': self._enabled,
            'total_violations': len(self.violations),
            'critical_violations': critical_count,
            'error_violations': error_count,
            'memory_usage_mb': self.resource_monitor.get_memory_usage_mb(),
            'memory_limit_mb': self.resource_monitor.memory_limit_mb,
            'rollback_status': self.rollback_manager.get_rollback_status(),
        }
    
    def enable(self):
        """Enable safety guard."""
        self._enabled = True
    
    def disable(self):
        """Disable safety guard."""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if safety guard is enabled."""
        return self._enabled


# Global safety guard instance
_global_safety_guard: Optional[SafetyGuard] = None


def initialize_global_safety_guard(
    memory_limit_mb: int = 500,
    timeout_sec: int = 30,
    phase_3_baseline_path: Optional[str] = None,
) -> SafetyGuard:
    """Initialize global safety guard."""
    global _global_safety_guard
    _global_safety_guard = SafetyGuard(memory_limit_mb, timeout_sec, phase_3_baseline_path)
    return _global_safety_guard


def get_global_safety_guard() -> SafetyGuard:
    """Get global safety guard instance."""
    global _global_safety_guard
    if _global_safety_guard is None:
        _global_safety_guard = SafetyGuard()
    return _global_safety_guard
