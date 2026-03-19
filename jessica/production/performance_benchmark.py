"""
Phase 4: Operator Performance Benchmarking

Benchmarks latency, memory, and throughput for refined operators.
"""

import time
import json
import statistics
from dataclasses import dataclass, asdict
from typing import Dict, List, Any
from pathlib import Path

from jessica.unified_world_model.causal_operator import (
    detect_bottleneck_operator,
    constrain_operator,
    optimize_operator,
    sequence_operator,
    adapt_operator,
    substitute_operator,
)


@dataclass
class BenchmarkResult:
    """Single benchmark measurement."""
    operator_name: str
    iteration: int
    duration_ms: float
    memory_used_mb: float
    input_size: int
    output_size: int
    success: bool
    error: str = ""


@dataclass
class BenchmarkSummary:
    """Summary of benchmark results."""
    operator_name: str
    iterations: int
    successful: int
    failed: int
    
    latency_ms_min: float
    latency_ms_max: float
    latency_ms_mean: float
    latency_ms_median: float
    latency_ms_std: float
    
    memory_mb_min: float
    memory_mb_max: float
    memory_mb_mean: float
    
    throughput_ops_per_sec: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class OperatorBenchmark:
    """Benchmark harness for operators."""
    
    def __init__(self):
        """Initialize benchmark."""
        self.results: List[BenchmarkResult] = []
    
    def benchmark_detect_bottleneck(self, iterations: int = 100) -> BenchmarkSummary:
        """Benchmark DETECT_BOTTLENECK operator."""
        return self._run_operator_benchmark(
            "detect_bottleneck_refined",
            detect_bottleneck_operator,
            iterations,
            self._create_bottleneck_inputs(),
        )
    
    def benchmark_constrain(self, iterations: int = 100) -> BenchmarkSummary:
        """Benchmark CONSTRAIN operator."""
        return self._run_operator_benchmark(
            "constrain",
            constrain_operator,
            iterations,
            self._create_constrain_inputs(),
        )
    
    def benchmark_sequence(self, iterations: int = 100) -> BenchmarkSummary:
        """Benchmark SEQUENCE operator."""
        return self._run_operator_benchmark(
            "sequence",
            sequence_operator,
            iterations,
            self._create_sequence_inputs(),
        )
    
    def benchmark_adapt(self, iterations: int = 100) -> BenchmarkSummary:
        """Benchmark ADAPT operator."""
        return self._run_operator_benchmark(
            "adapt",
            adapt_operator,
            iterations,
            self._create_adapt_inputs(),
        )
    
    def _run_operator_benchmark(
        self,
        operator_name: str,
        operator_fn,
        iterations: int,
        input_gen,
    ) -> BenchmarkSummary:
        """Run benchmark for operator."""
        import psutil
        process = psutil.Process()
        
        results = []
        durations = []
        memory_usages = []
        
        for i in range(iterations):
            # Get fresh input
            test_input = next(input_gen)
            input_size = len(str(test_input))
            
            # Measure memory before
            process.memory_info()  # Trigger garbage collection timing
            
            # Benchmark
            start_time = time.perf_counter()
            try:
                result = operator_fn(test_input)
                duration = (time.perf_counter() - start_time) * 1000  # Convert to ms
                
                # Measure memory after
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                output_size = len(str(result))
                
                benchmark = BenchmarkResult(
                    operator_name=operator_name,
                    iteration=i,
                    duration_ms=duration,
                    memory_used_mb=memory_mb,
                    input_size=input_size,
                    output_size=output_size,
                    success=True,
                )
                
                results.append(benchmark)
                durations.append(duration)
                memory_usages.append(memory_mb)
                
            except Exception as e:
                benchmark = BenchmarkResult(
                    operator_name=operator_name,
                    iteration=i,
                    duration_ms=0,
                    memory_used_mb=0,
                    input_size=input_size,
                    output_size=0,
                    success=False,
                    error=str(e),
                )
                results.append(benchmark)
        
        # Save results
        self.results.extend(results)
        
        # Calculate summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        if durations:
            summary = BenchmarkSummary(
                operator_name=operator_name,
                iterations=iterations,
                successful=successful,
                failed=failed,
                latency_ms_min=min(durations),
                latency_ms_max=max(durations),
                latency_ms_mean=statistics.mean(durations),
                latency_ms_median=statistics.median(durations),
                latency_ms_std=statistics.stdev(durations) if len(durations) > 1 else 0,
                memory_mb_min=min(memory_usages),
                memory_mb_max=max(memory_usages),
                memory_mb_mean=statistics.mean(memory_usages),
                throughput_ops_per_sec=1000 / statistics.mean(durations),
            )
        else:
            summary = BenchmarkSummary(
                operator_name=operator_name,
                iterations=iterations,
                successful=0,
                failed=failed,
                latency_ms_min=0,
                latency_ms_max=0,
                latency_ms_mean=0,
                latency_ms_median=0,
                latency_ms_std=0,
                memory_mb_min=0,
                memory_mb_max=0,
                memory_mb_mean=0,
                throughput_ops_per_sec=0,
            )
        
        return summary
    
    def _create_bottleneck_inputs(self):
        """Generate test inputs for bottleneck detection."""
        while True:
            # Simulate different system components with varying throughput
            yield {
                'components': {
                    'db': {'throughput': 100},
                    'api': {'throughput': 150},
                    'cache': {'throughput': 50},  # Bottleneck
                },
                'query': 'SELECT * FROM users',
            }
    
    def _create_constrain_inputs(self):
        """Generate test inputs for constraint application."""
        while True:
            yield {
                'constraints': {
                    'max_memory_mb': 500,
                    'max_latency_ms': 100,
                    'max_retries': 3,
                },
                'resources': {
                    'memory_mb': 400,
                    'latency_ms': 80,
                    'retries': 2,
                },
            }
    
    def _create_sequence_inputs(self):
        """Generate test inputs for sequencing."""
        while True:
            yield {
                'tasks': [
                    {'id': '1', 'duration': 10},
                    {'id': '2', 'duration': 20},
                    {'id': '3', 'duration': 15},
                ],
                'dependencies': {'2': ['1'], '3': ['2']},
            }
    
    def _create_adapt_inputs(self):
        """Generate test inputs for adaptation."""
        while True:
            yield {
                'current_strategy': 'strategy_a',
                'performance': {'success_rate': 0.85},
                'alternatives': ['strategy_b', 'strategy_c'],
            }
    
    def export_results_json(self, output_path: str) -> tuple[bool, str]:
        """Export benchmark results to JSON."""
        try:
            data = {
                'timestamp': time.time(),
                'results_count': len(self.results),
                'results': [asdict(r) for r in self.results],
            }
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True, f"Results exported to {output_path}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def get_all_summaries(self) -> Dict[str, BenchmarkSummary]:
        """Get all benchmark summaries."""
        summaries = {}
        for result in self.results:
            op_name = result.operator_name
            if op_name not in summaries:
                summaries[op_name] = self._calculate_summary(op_name)
        return summaries
    
    def _calculate_summary(self, operator_name: str) -> BenchmarkSummary:
        """Calculate summary for operator."""
        op_results = [r for r in self.results if r.operator_name == operator_name]
        successful = sum(1 for r in op_results if r.success)
        failed = len(op_results) - successful
        
        durations = [r.duration_ms for r in op_results if r.success]
        memory_usages = [r.memory_used_mb for r in op_results if r.success]
        
        if durations:
            return BenchmarkSummary(
                operator_name=operator_name,
                iterations=len(op_results),
                successful=successful,
                failed=failed,
                latency_ms_min=min(durations),
                latency_ms_max=max(durations),
                latency_ms_mean=statistics.mean(durations),
                latency_ms_median=statistics.median(durations),
                latency_ms_std=statistics.stdev(durations) if len(durations) > 1 else 0,
                memory_mb_min=min(memory_usages),
                memory_mb_max=max(memory_usages),
                memory_mb_mean=statistics.mean(memory_usages),
                throughput_ops_per_sec=1000 / statistics.mean(durations),
            )
        
        return BenchmarkSummary(
            operator_name=operator_name,
            iterations=len(op_results),
            successful=successful,
            failed=failed,
            latency_ms_min=0,
            latency_ms_max=0,
            latency_ms_mean=0,
            latency_ms_median=0,
            latency_ms_std=0,
            memory_mb_min=0,
            memory_mb_max=0,
            memory_mb_mean=0,
            throughput_ops_per_sec=0,
        )


def run_performance_benchmarks() -> Dict[str, BenchmarkSummary]:
    """Run complete performance benchmarking suite."""
    print("[PHASE 4] Operator Performance Benchmarking")
    print("=" * 70)
    
    benchmark = OperatorBenchmark()
    summaries = {}
    
    # Benchmark each operator
    print("\n[1/5] Benchmarking DETECT_BOTTLENECK (100 iterations)...")
    summaries['detect_bottleneck'] = benchmark.benchmark_detect_bottleneck(100)
    print(f"      Mean latency: {summaries['detect_bottleneck'].latency_ms_mean:.2f}ms")
    print(f"      Throughput: {summaries['detect_bottleneck'].throughput_ops_per_sec:.1f} ops/sec")
    
    print("\n[2/5] Benchmarking CONSTRAIN (100 iterations)...")
    summaries['constrain'] = benchmark.benchmark_constrain(100)
    print(f"      Mean latency: {summaries['constrain'].latency_ms_mean:.2f}ms")
    print(f"      Throughput: {summaries['constrain'].throughput_ops_per_sec:.1f} ops/sec")
    
    print("\n[3/5] Benchmarking SEQUENCE (100 iterations)...")
    summaries['sequence'] = benchmark.benchmark_sequence(100)
    print(f"      Mean latency: {summaries['sequence'].latency_ms_mean:.2f}ms")
    print(f"      Throughput: {summaries['sequence'].throughput_ops_per_sec:.1f} ops/sec")
    
    print("\n[4/5] Benchmarking ADAPT (100 iterations)...")
    summaries['adapt'] = benchmark.benchmark_adapt(100)
    print(f"      Mean latency: {summaries['adapt'].latency_ms_mean:.2f}ms")
    print(f"      Throughput: {summaries['adapt'].throughput_ops_per_sec:.1f} ops/sec")
    
    # Export results
    print("\n[5/5] Exporting results...")
    success, msg = benchmark.export_results_json('docs/phase_4_performance_results.json')
    print(f"      {msg}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("[PERFORMANCE SUMMARY]")
    print("=" * 70)
    
    total_latency = 0
    operator_count = 0
    
    for op_name, summary in summaries.items():
        print(f"\n{op_name.upper()}:")
        print(f"  Iterations: {summary.iterations}")
        print(f"  Successful: {summary.successful}/{summary.iterations}")
        print(f"  Latency (ms):     min={summary.latency_ms_min:.2f}, max={summary.latency_ms_max:.2f}, mean={summary.latency_ms_mean:.2f}, median={summary.latency_ms_median:.2f}")
        print(f"  Memory (MB):      min={summary.memory_mb_min:.1f}, max={summary.memory_mb_max:.1f}, mean={summary.memory_mb_mean:.1f}")
        print(f"  Throughput:       {summary.throughput_ops_per_sec:.1f} ops/sec")
        
        total_latency += summary.latency_ms_mean
        operator_count += 1
    
    avg_latency = total_latency / operator_count if operator_count > 0 else 0
    print(f"\n[AGGREGATES]")
    print(f"  Average latency across operators: {avg_latency:.2f}ms")
    print(f"  Status: {'[OK] Meets latency requirement <100ms' if avg_latency < 100 else '[WARNING] Exceeds latency target'}")
    
    return summaries


if __name__ == "__main__":
    summaries = run_performance_benchmarks()
