"""
Phase 4: Operator Trace Observability System

Provides complete audit trail of operator decisions and execution.
- Non-invasive operator logging
- Performance metrics collection
- Error tracking with context
- Telemetry export (JSON/CSV)
- Dashboard data generation
"""

from __future__ import annotations

import json
import time
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import deque


class OperatorType(Enum):
    """Operator types for tracing."""
    SEQUENCE = "SEQUENCE"
    CONSTRAIN = "CONSTRAIN"
    DETECT_BOTTLENECK = "DETECT_BOTTLENECK"
    ADAPT = "ADAPT"
    SUBSTITUTE = "SUBSTITUTE"
    HANDLE = "HANDLE"


class OperatorStatus(Enum):
    """Operator execution status."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


@dataclass
class OperatorTrace:
    """Single operator invocation trace."""
    # Identification
    trace_id: str
    operator_type: str
    operator_name: str
    
    # Timing
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    
    # Execution
    status: str = OperatorStatus.INITIATED.value
    input_params: Dict[str, Any] = field(default_factory=dict)
    output_result: Dict[str, Any] = field(default_factory=dict)
    
    # Memory & Resources
    memory_before_mb: Optional[float] = None
    memory_after_mb: Optional[float] = None
    memory_peak_mb: Optional[float] = None
    
    # Error Information
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    error_trace: Optional[str] = None
    
    # Metadata
    chain_id: str = ""
    parent_trace_id: Optional[str] = None
    depth: int = 0
    
    def finalize(self, status: OperatorStatus, result: Optional[Dict] = None, error: Optional[Exception] = None):
        """Mark trace as complete."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = status.value
        
        if result:
            self.output_result = result
        
        if error:
            self.error_type = type(error).__name__
            self.error_message = str(error)
            self.error_trace = repr(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary."""
        return asdict(self)


@dataclass
class OperatorChainTrace:
    """Complete operator chain execution trace."""
    chain_id: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    
    query: str = ""
    operator_traces: List[OperatorTrace] = field(default_factory=list)
    
    total_operators: int = 0
    successful_operators: int = 0
    failed_operators: int = 0
    
    status: str = OperatorStatus.IN_PROGRESS.value
    error_message: Optional[str] = None
    
    def add_operator_trace(self, trace: OperatorTrace):
        """Add operator trace to chain."""
        self.operator_traces.append(trace)
        self.total_operators = len(self.operator_traces)
    
    def finalize(self, status: OperatorStatus, error: Optional[Exception] = None):
        """Mark chain as complete."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = status.value
        
        # Count statuses
        self.successful_operators = sum(
            1 for t in self.operator_traces 
            if t.status == OperatorStatus.SUCCESS.value
        )
        self.failed_operators = sum(
            1 for t in self.operator_traces 
            if t.status == OperatorStatus.FAILURE.value
        )
        
        if error:
            self.error_message = str(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chain trace to dictionary."""
        return {
            'chain_id': self.chain_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_ms': self.duration_ms,
            'query': self.query,
            'total_operators': self.total_operators,
            'successful_operators': self.successful_operators,
            'failed_operators': self.failed_operators,
            'status': self.status,
            'error_message': self.error_message,
            'operator_traces': [t.to_dict() for t in self.operator_traces],
        }


class OperatorTracer:
    """Non-invasive operator trace collection and management."""
    
    def __init__(self, buffer_size: int = 10000):
        """Initialize tracer with buffer."""
        self.buffer_size = buffer_size
        self.traces: deque = deque(maxlen=buffer_size)
        self.chain_traces: deque = deque(maxlen=buffer_size)
        self._lock = threading.RLock()
        self._operator_stats: Dict[str, Dict[str, Any]] = {}
        self._is_collecting = True
    
    def start_operator_trace(
        self,
        operator_type: OperatorType,
        operator_name: str,
        input_params: Dict[str, Any],
        chain_id: str = "",
        parent_trace_id: Optional[str] = None,
        depth: int = 0,
    ) -> OperatorTrace:
        """Start tracing an operator invocation."""
        if not self._is_collecting:
            return None
        
        trace_id = f"{chain_id}::{operator_name}::{int(time.time()*1e6)}"
        
        trace = OperatorTrace(
            trace_id=trace_id,
            operator_type=operator_type.value,
            operator_name=operator_name,
            start_time=time.time(),
            input_params=input_params,
            chain_id=chain_id,
            parent_trace_id=parent_trace_id,
            depth=depth,
        )
        
        return trace
    
    def end_operator_trace(
        self,
        trace: OperatorTrace,
        status: OperatorStatus,
        result: Optional[Dict] = None,
        error: Optional[Exception] = None,
    ):
        """Complete tracing of operator invocation."""
        if not self._is_collecting or trace is None:
            return
        
        trace.finalize(status, result, error)
        
        with self._lock:
            self.traces.append(trace)
            self._update_operator_stats(trace)
    
    def start_chain_trace(self, chain_id: str, query: str = "") -> OperatorChainTrace:
        """Start tracing an operator chain."""
        if not self._is_collecting:
            return None
        
        chain_trace = OperatorChainTrace(
            chain_id=chain_id,
            start_time=time.time(),
            query=query,
        )
        
        return chain_trace
    
    def end_chain_trace(
        self,
        chain_trace: OperatorChainTrace,
        status: OperatorStatus,
        error: Optional[Exception] = None,
    ):
        """Complete tracing of operator chain."""
        if not self._is_collecting or chain_trace is None:
            return
        
        chain_trace.finalize(status, error)
        
        with self._lock:
            self.chain_traces.append(chain_trace)
    
    def add_operator_to_chain(self, chain_trace: OperatorChainTrace, operator_trace: OperatorTrace):
        """Add operator trace to chain trace."""
        if chain_trace is not None and operator_trace is not None:
            chain_trace.add_operator_trace(operator_trace)
    
    def _update_operator_stats(self, trace: OperatorTrace):
        """Update aggregate statistics for operator."""
        op_name = trace.operator_name
        
        if op_name not in self._operator_stats:
            self._operator_stats[op_name] = {
                'invocations': 0,
                'successes': 0,
                'failures': 0,
                'total_duration_ms': 0.0,
                'min_duration_ms': float('inf'),
                'max_duration_ms': 0.0,
                'avg_duration_ms': 0.0,
            }
        
        stats = self._operator_stats[op_name]
        stats['invocations'] += 1
        
        if trace.status == OperatorStatus.SUCCESS.value:
            stats['successes'] += 1
        elif trace.status == OperatorStatus.FAILURE.value:
            stats['failures'] += 1
        
        if trace.duration_ms:
            stats['total_duration_ms'] += trace.duration_ms
            stats['min_duration_ms'] = min(stats['min_duration_ms'], trace.duration_ms)
            stats['max_duration_ms'] = max(stats['max_duration_ms'], trace.duration_ms)
            stats['avg_duration_ms'] = stats['total_duration_ms'] / stats['invocations']
    
    def get_operator_stats(self, operator_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for operator(s)."""
        with self._lock:
            if operator_name:
                return self._operator_stats.get(operator_name, {})
            return dict(self._operator_stats)
    
    def get_recent_traces(self, limit: int = 100) -> List[OperatorTrace]:
        """Get recent operator traces."""
        with self._lock:
            return list(self.traces)[-limit:]
    
    def get_recent_chain_traces(self, limit: int = 50) -> List[OperatorChainTrace]:
        """Get recent chain traces."""
        with self._lock:
            return list(self.chain_traces)[-limit:]
    
    def get_chain_trace(self, chain_id: str) -> Optional[OperatorChainTrace]:
        """Get specific chain trace."""
        with self._lock:
            for chain_trace in self.chain_traces:
                if chain_trace.chain_id == chain_id:
                    return chain_trace
        return None
    
    def export_traces_json(self, output_path: str) -> tuple[bool, str]:
        """Export collected traces to JSON file."""
        try:
            with self._lock:
                data = {
                    'export_timestamp': datetime.now().isoformat(),
                    'traces_count': len(self.traces),
                    'chains_count': len(self.chain_traces),
                    'operator_stats': self._operator_stats,
                    'recent_traces': [t.to_dict() for t in list(self.traces)[-100:]],
                    'recent_chains': [c.to_dict() for c in list(self.chain_traces)[-50:]],
                }
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True, f"Traces exported to {output_path}"
        except Exception as e:
            return False, f"Failed to export traces: {str(e)}"
    
    def export_traces_csv(self, output_path: str) -> tuple[bool, str]:
        """Export collected traces to CSV file."""
        try:
            import csv
            
            with self._lock:
                traces_list = list(self.traces)
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='') as f:
                fieldnames = [
                    'trace_id', 'operator_type', 'operator_name',
                    'start_time', 'end_time', 'duration_ms',
                    'status', 'error_type', 'error_message',
                    'chain_id', 'depth'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for trace in traces_list:
                    writer.writerow({
                        'trace_id': trace.trace_id,
                        'operator_type': trace.operator_type,
                        'operator_name': trace.operator_name,
                        'start_time': trace.start_time,
                        'end_time': trace.end_time,
                        'duration_ms': trace.duration_ms,
                        'status': trace.status,
                        'error_type': trace.error_type or '',
                        'error_message': trace.error_message or '',
                        'chain_id': trace.chain_id,
                        'depth': trace.depth,
                    })
            
            return True, f"Traces exported to {output_path}"
        except Exception as e:
            return False, f"Failed to export CSV: {str(e)}"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get tracing summary."""
        with self._lock:
            return {
                'total_traces': len(self.traces),
                'total_chains': len(self.chain_traces),
                'buffer_size': self.buffer_size,
                'operators_tracked': len(self._operator_stats),
                'is_collecting': self._is_collecting,
                'operator_stats': dict(self._operator_stats),
            }
    
    def pause_collection(self):
        """Pause trace collection."""
        self._is_collecting = False
    
    def resume_collection(self):
        """Resume trace collection."""
        self._is_collecting = True
    
    def clear_traces(self):
        """Clear all collected traces."""
        with self._lock:
            self.traces.clear()
            self.chain_traces.clear()
            self._operator_stats.clear()


# Global tracer instance
_global_tracer: Optional[OperatorTracer] = None


def initialize_global_tracer(buffer_size: int = 10000) -> OperatorTracer:
    """Initialize global tracer."""
    global _global_tracer
    _global_tracer = OperatorTracer(buffer_size)
    return _global_tracer


def get_global_tracer() -> OperatorTracer:
    """Get global tracer instance."""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = OperatorTracer()
    return _global_tracer
