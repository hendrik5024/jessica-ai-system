"""
Self-Code Improvement Integration with Autodidactic Loop.

The Autodidactic Loop (weekly self-learning) now includes a new capability:
identifying and implementing recursive code improvements.

Weekly Process:
1. Collect performance metrics from the week
2. Analyze code for bottlenecks
3. Generate improvement pull requests
4. Safety gate each PR (Self-Simulation)
5. Execute approved PRs
6. Log results and lessons learned
7. Feed learnings back into model fine-tuning

This is the Singularity Loop - Jessica improving her own code.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os


@dataclass
class SelfImprovementCycle:
    """A complete weekly self-improvement cycle."""
    cycle_id: str
    week_start: datetime
    week_end: datetime
    
    # Performance analysis
    performance_bottlenecks: List[Dict] = field(default_factory=list)
    code_issues_identified: List[Dict] = field(default_factory=list)
    
    # Improvement PRs
    prs_generated: int = 0
    prs_approved: int = 0
    prs_applied: int = 0
    prs_failed: int = 0
    
    # Results
    total_speedup_achieved: float = 1.0
    new_tests_added: int = 0
    code_coverage_improvement: float = 0.0
    
    # Learning
    lessons_learned: List[str] = field(default_factory=list)
    failure_analysis: List[Dict] = field(default_factory=list)
    model_update_suggested: bool = False
    
    cycle_status: str = "in_progress"  # in_progress, completed, partially_failed


class SelfCodeImprovementEngine:
    """Manages recursive self-code improvement integration with autodidactic loop."""
    
    def __init__(self, jessica_root: str, autodidactic_instance=None):
        self.jessica_root = jessica_root
        self.autodidactic = autodidactic_instance
        self.improvement_history: List[SelfImprovementCycle] = []
        self.log_dir = os.path.join(jessica_root, ".jessica/self_improvement_logs")
        os.makedirs(self.log_dir, exist_ok=True)
    
    def run_weekly_improvement_cycle(self) -> SelfImprovementCycle:
        """
        Execute complete weekly self-improvement cycle.
        
        This is called by the autodidactic loop every Sunday.
        """
        
        cycle_id = f"improvement-week-{datetime.now().strftime('%Y%m%d')}"
        cycle = SelfImprovementCycle(
            cycle_id=cycle_id,
            week_start=datetime.now() - timedelta(days=7),
            week_end=datetime.now(),
        )
        
        print(f"\n{'='*70}")
        print(f"Starting Weekly Self-Improvement Cycle: {cycle_id}")
        print(f"{'='*70}\n")
        
        # Step 1: Analyze performance metrics from the week
        print("Step 1: Analyzing performance bottlenecks from past week...")
        cycle.performance_bottlenecks = self._analyze_weekly_performance()
        print(f"  ✓ Found {len(cycle.performance_bottlenecks)} performance issues")
        
        # Step 2: Analyze code for optimization opportunities
        print("\nStep 2: Analyzing code for optimization opportunities...")
        from jessica.meta.code_analyzer import analyze_jessica
        analysis_report = analyze_jessica(self.jessica_root)
        cycle.code_issues_identified = [
            {
                'file': issue.file_path,
                'line': issue.line_number,
                'category': issue.category.value,
                'severity': issue.severity,
            }
            for issue in analysis_report.issues_found[:10]
        ]
        print(f"  ✓ Identified {len(cycle.code_issues_identified)} code issues")
        
        # Step 3: Generate improvement PRs
        print("\nStep 3: Generating improvement pull requests...")
        from jessica.meta.improvement_generator import generate_improvements_from_analysis
        pull_requests = generate_improvements_from_analysis(analysis_report)
        cycle.prs_generated = len(pull_requests)
        print(f"  ✓ Generated {cycle.prs_generated} improvement PRs")
        
        # Step 4: Safety gate and execute each PR
        print("\nStep 4: Safety review and executing approved PRs...")
        from jessica.meta.self_simulation_gate import gate_code_change
        from jessica.meta.pr_manager import execute_self_improvement
        
        for pr in pull_requests:
            # Safety gate
            approved, impact = gate_code_change(pr, verbose=False)
            
            if approved:
                cycle.prs_approved += 1
                
                # Execute PR
                success, log = execute_self_improvement(
                    pr,
                    self.jessica_root,
                    safety_gate_fn=lambda x: (approved, impact)
                )
                
                if success:
                    cycle.prs_applied += 1
                    cycle.total_speedup_achieved *= log.performance_improvement or 1.0
                    
                    print(f"  ✓ Applied: {pr.title}")
                else:
                    cycle.prs_failed += 1
                    cycle.failure_analysis.append({
                        'pr_id': pr.pr_id,
                        'reason': log.errors[0] if log.errors else "Unknown",
                    })
                    print(f"  ✗ Failed: {pr.title}")
        
        # Step 5: Run full test suite
        print("\nStep 5: Running full test suite to verify integrity...")
        tests_passed = self._run_test_suite()
        if tests_passed:
            print(f"  ✓ All tests passed")
        else:
            print(f"  ⚠️ Some tests failed - may need rollback")
        
        # Step 6: Extract lessons learned
        print("\nStep 6: Extracting lessons for future improvement...")
        cycle.lessons_learned = self._extract_lessons(cycle)
        for lesson in cycle.lessons_learned[:3]:
            print(f"  • {lesson}")
        
        # Step 7: Suggest model updates
        print("\nStep 7: Analyzing if model update is needed...")
        cycle.model_update_suggested = self._should_update_model(cycle)
        if cycle.model_update_suggested:
            print(f"  ✓ Model update recommended for next cycle")
        
        # Step 8: Save cycle results
        cycle.cycle_status = "completed" if cycle.prs_applied > 0 else "no_improvements"
        self._save_cycle_results(cycle)
        
        print(f"\n{'='*70}")
        print(f"Cycle Complete: {cycle.prs_applied}/{cycle.prs_generated} PRs applied")
        print(f"Total speedup achieved: {cycle.total_speedup_achieved:.2f}x")
        print(f"{'='*70}\n")
        
        return cycle
    
    def _analyze_weekly_performance(self) -> List[Dict]:
        """Analyze performance metrics from the past week."""
        from jessica.meta.performance_monitor import get_monitor
        
        monitor = get_monitor()
        report = monitor.detect_bottlenecks(window_minutes=10080)  # 7 days
        
        return [
            {
                'metric': bn['name'],
                'current_ms': bn['current_ms'],
                'threshold_ms': bn['threshold_ms'],
                'severity': bn['severity'],
            }
            for bn in report.bottlenecks
        ]
    
    def _run_test_suite(self) -> bool:
        """Run the full test suite to verify changes."""
        import subprocess
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-q"],
                cwd=self.jessica_root,
                capture_output=True,
                timeout=600,
            )
            return result.returncode == 0
        except:
            return False
    
    def _extract_lessons(self, cycle: SelfImprovementCycle) -> List[str]:
        """Extract lessons learned from the improvement cycle."""
        
        lessons = []
        
        # Lesson 1: Most common optimization type
        optimization_types = {}
        for issue in cycle.code_issues_identified:
            cat = issue.get('category', 'unknown')
            optimization_types[cat] = optimization_types.get(cat, 0) + 1
        
        if optimization_types:
            most_common = max(optimization_types, key=optimization_types.get)
            lessons.append(
                f"This week's main bottleneck was {most_common} - "
                f"focus next week on {most_common} optimizations"
            )
        
        # Lesson 2: Success rate
        if cycle.prs_generated > 0:
            success_rate = cycle.prs_applied / cycle.prs_generated
            if success_rate < 0.5:
                lessons.append(
                    "Most PRs failed safety gate this week - "
                    "code modifications had high identity risk"
                )
            elif success_rate > 0.8:
                lessons.append(
                    "High success rate on PRs - safe optimizations working well"
                )
        
        # Lesson 3: Performance gain
        if cycle.total_speedup_achieved > 1.1:
            lessons.append(
                f"Achieved {cycle.total_speedup_achieved:.1f}x speedup - "
                f"significant performance improvement this cycle"
            )
        
        # Lesson 4: Failures
        if cycle.failure_analysis:
            lessons.append(
                f"{len(cycle.failure_analysis)} PRs failed - "
                f"investigate failure patterns"
            )
        
        return lessons
    
    def _should_update_model(self, cycle: SelfImprovementCycle) -> bool:
        """Determine if model fine-tuning should happen."""
        
        # Update model if:
        # 1. Significant code improvements made
        if cycle.total_speedup_achieved > 1.5:
            return True
        
        # 2. New patterns learned from failures
        if len(cycle.failure_analysis) > 3:
            return True
        
        # 3. Coverage improvement
        if cycle.code_coverage_improvement > 0.05:
            return True
        
        return False
    
    def _save_cycle_results(self, cycle: SelfImprovementCycle):
        """Save cycle results for analysis."""
        
        cycle_path = os.path.join(self.log_dir, f"{cycle.cycle_id}.json")
        
        cycle_dict = {
            'cycle_id': cycle.cycle_id,
            'week_start': cycle.week_start.isoformat(),
            'week_end': cycle.week_end.isoformat(),
            'prs_generated': cycle.prs_generated,
            'prs_approved': cycle.prs_approved,
            'prs_applied': cycle.prs_applied,
            'prs_failed': cycle.prs_failed,
            'total_speedup_achieved': cycle.total_speedup_achieved,
            'lessons_learned': cycle.lessons_learned,
            'cycle_status': cycle.cycle_status,
        }
        
        with open(cycle_path, 'w') as f:
            json.dump(cycle_dict, f, indent=2)
    
    def get_improvement_history(self) -> List[Dict]:
        """Get history of all self-improvement cycles."""
        
        history = []
        for log_file in sorted(os.listdir(self.log_dir)):
            if log_file.endswith('.json'):
                with open(os.path.join(self.log_dir, log_file), 'r') as f:
                    history.append(json.load(f))
        
        return history
    
    def get_cumulative_speedup(self) -> float:
        """Calculate cumulative speedup from all improvement cycles."""
        
        total = 1.0
        for record in self.get_improvement_history():
            total *= record.get('total_speedup_achieved', 1.0)
        
        return total


def integrate_with_autodidactic_loop(autodidactic_instance, jessica_root: str):
    """
    Hook self-improvement engine into the autodidactic loop.
    
    Call this once to set up the integration.
    """
    
    engine = SelfCodeImprovementEngine(jessica_root, autodidactic_instance)
    
    # Register self-improvement as a weekly task
    if hasattr(autodidactic_instance, 'register_weekly_task'):
        autodidactic_instance.register_weekly_task(
            name="recursive_self_code_improvement",
            task=engine.run_weekly_improvement_cycle,
            description="Analyze performance, generate and execute code improvements"
        )
    
    return engine


# ============================================================================
# EXAMPLE: How to use (for documentation)
# ============================================================================

"""
# In your autodidactic_loop.py or agent initialization:

from jessica.meta.recursive_self_improvement import integrate_with_autodidactic_loop

# Initialize autodidactic loop
autodidactic = AutodidacticLoop(...)

# Integrate self-improvement
# Example (portable):
# from jessica.config.paths import get_base_dir
# import os
# improvement_engine = integrate_with_autodidactic_loop(
#     autodidactic,
#     jessica_root=os.path.join(get_base_dir(), "jessica")
# )

# Every Sunday, autodidactic loop will automatically:
# 1. Run improvement_engine.run_weekly_improvement_cycle()
# 2. Collect PRs
# 3. Safety gate them
# 4. Execute approved changes
# 5. Log results

# You can also manually trigger it:
cycle = improvement_engine.run_weekly_improvement_cycle()
print(f"Applied {cycle.prs_applied} improvements")
print(f"Speedup: {cycle.total_speedup_achieved:.2f}x")
"""
