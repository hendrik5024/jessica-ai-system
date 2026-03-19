"""
Performance Monitor - Real-time system metrics for bottleneck detection.

Tracks:
- LLM inference latency (router, general, code, visual models)
- Memory retrieval performance (episodic, semantic, RAG, causal)
- VRAM usage and model loading times
- Response pipeline timing (understanding → deciding → responding)
- Token throughput and cache hit rates
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    name: str
    duration_ms: float
    timestamp: datetime
    category: str  # 'inference', 'memory', 'vram', 'pipeline', 'cache'
    details: Dict = field(default_factory=dict)


@dataclass
class BottleneckReport:
    """Analysis of identified bottlenecks."""
    identified_at: datetime
    bottlenecks: List[Dict]  # [{"name": str, "metric": str, "severity": 0-1, "suggestion": str}]
    performance_summary: Dict
    recommendations: List[str]


class PerformanceMonitor:
    """Real-time performance tracking with bottleneck detection."""
    
    def __init__(self, window_size: int = 1000):
        """
        Args:
            window_size: Number of metrics to keep in rolling window
        """
        self.window_size = window_size
        self.metrics: List[PerformanceMetric] = []
        self.lock = threading.RLock()
        
        # Thresholds for bottleneck detection (ms)
        self.thresholds = {
            'router_inference': 100,      # Phi-3.5 should be <100ms
            'general_inference': 800,     # Mistral-7b should be <800ms
            'code_inference': 1200,       # CodeLlama-13b should be <1200ms
            'memory_retrieval': 150,      # Should be <150ms
            'vram_swap': 300,            # Model loading <300ms
            'full_pipeline': 2000,       # End-to-end <2sec for normal queries
        }
        
        # Performance baseline (updated from actual runs)
        self.baseline = {
            'router_inference': 80,
            'general_inference': 600,
            'code_inference': 900,
            'memory_retrieval': 80,
            'vram_swap': 200,
            'full_pipeline': 1500,
        }
    
    def record(self, name: str, duration_ms: float, category: str, details: Dict = None):
        """Record a performance metric."""
        with self.lock:
            metric = PerformanceMetric(
                name=name,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                category=category,
                details=details or {}
            )
            self.metrics.append(metric)
            
            # Trim to window size
            if len(self.metrics) > self.window_size:
                self.metrics = self.metrics[-self.window_size:]
    
    def get_stats(self, name: str = None, category: str = None, 
                  minutes: int = 5) -> Dict:
        """Get statistics for recent metrics."""
        with self.lock:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            
            # Filter metrics
            filtered = self.metrics
            if name:
                filtered = [m for m in filtered if m.name == name]
            if category:
                filtered = [m for m in filtered if m.category == category]
            filtered = [m for m in filtered if m.timestamp >= cutoff]
            
            if not filtered:
                return {}
            
            durations = [m.duration_ms for m in filtered]
            return {
                'name': name or category or 'all',
                'count': len(filtered),
                'min_ms': min(durations),
                'max_ms': max(durations),
                'avg_ms': sum(durations) / len(durations),
                'median_ms': sorted(durations)[len(durations) // 2],
                'p95_ms': sorted(durations)[int(len(durations) * 0.95)],
                'p99_ms': sorted(durations)[int(len(durations) * 0.99)],
            }
    
    def detect_bottlenecks(self, window_minutes: int = 10) -> BottleneckReport:
        """Identify performance bottlenecks in recent metrics."""
        bottlenecks = []
        
        # Check each tracked metric type
        metric_types = {
            'router_inference': ('router', 'inference'),
            'general_inference': ('general', 'inference'),
            'code_inference': ('code', 'inference'),
            'memory_retrieval': ('memory', 'retrieval'),
            'vram_swap': ('vram', 'swap'),
            'full_pipeline': (None, 'pipeline'),
        }
        
        performance_summary = {}
        
        with self.lock:
            for metric_key, (name_filter, category) in metric_types.items():
                stats = self.get_stats(name=name_filter, category=category, 
                                      minutes=window_minutes)
                if not stats:
                    continue
                
                performance_summary[metric_key] = stats
                
                # Compare to threshold
                threshold = self.thresholds[metric_key]
                avg_time = stats.get('avg_ms', 0)
                p95_time = stats.get('p95_ms', 0)
                
                # Severity: how far above baseline/threshold
                if p95_time > threshold:
                    severity = min(1.0, (p95_time - threshold) / threshold)
                    
                    bottlenecks.append({
                        'name': metric_key,
                        'metric': f"p95_ms",
                        'current_ms': p95_time,
                        'threshold_ms': threshold,
                        'severity': severity,
                        'suggestion': self._get_suggestion(metric_key, stats),
                    })
        
        # Sort by severity
        bottlenecks.sort(key=lambda x: x['severity'], reverse=True)
        
        # Generate recommendations
        recommendations = []
        for bn in bottlenecks[:3]:  # Top 3
            if bn['severity'] > 0.2:
                recommendations.append(bn['suggestion'])
        
        return BottleneckReport(
            identified_at=datetime.now(),
            bottlenecks=bottlenecks,
            performance_summary=performance_summary,
            recommendations=recommendations,
        )
    
    def _get_suggestion(self, metric_key: str, stats: Dict) -> str:
        """Generate a suggestion for fixing a bottleneck."""
        p95 = stats.get('p95_ms', 0)
        suggestions = {
            'router_inference': f"Router too slow ({p95:.0f}ms). Consider quantizing Phi-3.5 further or reducing context size.",
            'general_inference': f"Chat model slow ({p95:.0f}ms). Profile token generation; consider batch-size tuning.",
            'code_inference': f"Code model slow ({p95:.0f}ms). Check for long inputs; consider chunking large files.",
            'memory_retrieval': f"Memory access slow ({p95:.0f}ms). Rebuild FAISS index or increase cache size.",
            'vram_swap': f"Model loading slow ({p95:.0f}ms). Use faster storage (SSD) or pre-load common models.",
            'full_pipeline': f"End-to-end pipeline slow ({p95:.0f}ms). Parallelize memory/inference or reduce context.",
        }
        return suggestions.get(metric_key, f"Performance issue detected in {metric_key}")
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON for analysis."""
        with self.lock:
            data = {
                'exported_at': datetime.now().isoformat(),
                'metrics': [
                    {
                        'name': m.name,
                        'duration_ms': m.duration_ms,
                        'timestamp': m.timestamp.isoformat(),
                        'category': m.category,
                        'details': m.details,
                    }
                    for m in self.metrics
                ],
                'thresholds': self.thresholds,
                'baseline': self.baseline,
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
    
    def clear_metrics(self):
        """Clear all recorded metrics."""
        with self.lock:
            self.metrics.clear()


# Global monitor instance
_monitor = None


def get_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor."""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


def record_inference(model_name: str, duration_ms: float, tokens: int = 0):
    """Record an LLM inference event."""
    monitor = get_monitor()
    details = {'tokens': tokens, 'tokens_per_sec': tokens / (duration_ms / 1000) if duration_ms > 0 else 0}
    monitor.record(f"{model_name}_inference", duration_ms, 'inference', details)


def record_memory_retrieval(source: str, duration_ms: float, results: int = 0):
    """Record a memory retrieval event."""
    monitor = get_monitor()
    details = {'source': source, 'results_returned': results}
    monitor.record(f"{source}_retrieval", duration_ms, 'memory', details)


def record_vram_operation(operation: str, duration_ms: float, model: str = ""):
    """Record a VRAM operation (load, unload, swap)."""
    monitor = get_monitor()
    details = {'operation': operation, 'model': model}
    monitor.record(f"vram_{operation}", duration_ms, 'vram', details)


def record_pipeline_stage(stage: str, duration_ms: float, details: Dict = None):
    """Record a response pipeline stage."""
    monitor = get_monitor()
    monitor.record(f"pipeline_{stage}", duration_ms, 'pipeline', details or {})
