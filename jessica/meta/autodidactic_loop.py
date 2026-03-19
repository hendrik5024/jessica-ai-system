"""
Autodidactic Loop - Jessica's Self-Directed Curriculum

Weekly learning loop where Jessica:
1. Reviews failure clusters
2. Identifies weakest skills
3. Generates synthetic training data
4. Fine-tunes / adjusts prompts
5. Validates against benchmarks
6. Repeats

She becomes her own teacher.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from jessica.meta.failure_tracker import FailureTracker
from jessica.meta.synthetic_data_generator import SyntheticDataGenerator
from jessica.meta.self_directed_evolution import SelfDirectedEvolutionEngine


@dataclass
class LearningCycle:
    """A single learning cycle."""
    cycle_id: int
    started_at: str
    completed_at: Optional[str]
    target_skill: str
    baseline_metrics: Dict[str, float]
    training_data_count: int
    training_data_path: str
    improvement_metrics: Optional[Dict[str, float]]
    status: str  # "in_progress", "completed", "failed"
    notes: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningCycle':
        """Create from dictionary."""
        return cls(**data)


class AutodidacticLoop:
    """
    Self-directed learning system where Jessica improves herself.
    
    Usage:
        loop = AutodidacticLoop()
        
        # Run a single learning cycle
        cycle = loop.run_learning_cycle()
        
        # Schedule weekly runs
        loop.schedule_weekly()
        
        # Check progress
        stats = loop.get_learning_stats()
    """
    
    def __init__(self, storage_dir: str = "jessica_data_embeddings"):
        self.storage_dir = storage_dir
        self.storage_path = os.path.join(storage_dir, "autodidactic_state.json")
        self.failure_tracker = FailureTracker(storage_dir)
        self.data_generator = SyntheticDataGenerator()
        self.evolution_engine = SelfDirectedEvolutionEngine()
        
        self.cycles: List[LearningCycle] = []
        self.config = {
            "lookback_days": 7,
            "min_failures_threshold": 5,
            "training_data_count": 50,
            "success_rate_threshold": 0.7,  # Below this = needs improvement
            "cycle_interval_days": 7
        }
        
        self.load()
    
    def run_learning_cycle(
        self,
        force_skill: Optional[str] = None,
        allow_irreversible: bool = False,
        user_alignment_score: Optional[float] = None,
    ) -> Optional[LearningCycle]:
        """
        Run one complete learning cycle.
        
        Steps:
        1. Review failures
        2. Identify weakest skill
        3. Generate training data
        4. Prepare for fine-tuning
        5. Log cycle
        
        Args:
            force_skill: Override automatic skill selection
            
        Returns:
            LearningCycle object if successful, None if no improvement needed
        """
        print("🔬 Starting autodidactic learning cycle...")
        
        # Step 1: Review failures
        print("\n📊 Step 1: Reviewing failure clusters...")
        clusters = self.failure_tracker.get_failure_clusters(
            days=self.config["lookback_days"]
        )
        
        if not clusters:
            print("✅ No failures found! No learning needed.")
            return None
        
        print(f"Found failures in {len(clusters)} skills")
        
        # Step 2: Identify weakest skill
        print("\n🎯 Step 2: Identifying weakest skill...")
        weakest_skills = self.failure_tracker.identify_weakest_skills(
            days=self.config["lookback_days"],
            min_samples=self.config["min_failures_threshold"]
        )
        
        if not weakest_skills:
            print("✅ All skills performing well! No improvement needed.")
            return None
        
        if force_skill:
            target_skill = force_skill
            decision = None
        else:
            decision = self.evolution_engine.choose_learning_target(
                candidates=weakest_skills,
                user_alignment_score=user_alignment_score,
                allow_irreversible=allow_irreversible,
            )
            if not decision.constraints_passed:
                print("⚠️ Learning cycle blocked by hard constraints:")
                for violation in decision.violated_constraints:
                    print(f"  - {violation}")
                return None
            if decision.requires_approval and not allow_irreversible:
                print("⚠️ Irreversible learning change requires approval. Cycle paused.")
                return None
            target_skill = decision.target_skill
        baseline_metrics = {
            "success_rate": weakest_skills[0]["success_rate"],
            "avg_severity": weakest_skills[0]["avg_severity"],
            "failure_count": weakest_skills[0]["failures"]
        }
        
        print(f"Target skill: {target_skill}")
        print(f"  Success rate: {baseline_metrics['success_rate']:.1%}")
        print(f"  Avg severity: {baseline_metrics['avg_severity']:.1f}/10")
        print(f"  Failures: {baseline_metrics['failure_count']}")
        
        # Step 3: Generate training data
        print("\n📝 Step 3: Generating synthetic training data...")
        failure_patterns = self.failure_tracker.get_failure_patterns(
            target_skill,
            days=30
        )
        
        training_data = self.data_generator.generate_training_data(
            skill=target_skill,
            failure_patterns=failure_patterns,
            target_count=self.config["training_data_count"]
        )
        
        print(f"Generated {len(training_data)} training examples")
        
        # Step 4: Export training data
        print("\n💾 Step 4: Exporting training data...")
        cycle_id = len(self.cycles) + 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(self.storage_dir, "autodidactic_cycles")
        os.makedirs(output_dir, exist_ok=True)
        
        training_path = os.path.join(
            output_dir,
            f"cycle_{cycle_id}_{target_skill}_{timestamp}.jsonl"
        )
        
        self.data_generator.export_to_jsonl(training_data, training_path)
        print(f"Saved to: {training_path}")
        
        # Step 5: Create cycle record
        print("\n📈 Step 5: Recording learning cycle...")
        cycle = LearningCycle(
            cycle_id=cycle_id,
            started_at=datetime.now().isoformat(),
            completed_at=None,
            target_skill=target_skill,
            baseline_metrics=baseline_metrics,
            training_data_count=len(training_data),
            training_data_path=training_path,
            improvement_metrics=None,
            status="ready_for_training",
            notes=f"Generated {len(training_data)} examples for {target_skill} improvement"
            + (f"\nEvolution rationale: {decision.rationale}" if decision else "")
        )
        
        self.cycles.append(cycle)
        self.save()
        
        print(f"\n✅ Learning cycle #{cycle_id} complete!")
        print(f"\n📋 Next steps:")
        print(f"1. Review training data: {training_path}")
        print(f"2. Fine-tune model using this data")
        print(f"3. Run validation benchmarks")
        print(f"4. Call mark_cycle_complete({cycle_id}, metrics) when done")
        
        return cycle
    
    def mark_cycle_complete(self, cycle_id: int, improvement_metrics: Dict[str, float]) -> None:
        """
        Mark a learning cycle as complete with metrics.
        
        Args:
            cycle_id: Which cycle to update
            improvement_metrics: Post-training metrics
                {
                    "success_rate": 0.85,
                    "avg_severity": 4.2,
                    "failure_count": 3
                }
        """
        for cycle in self.cycles:
            if cycle.cycle_id == cycle_id:
                cycle.completed_at = datetime.now().isoformat()
                cycle.improvement_metrics = improvement_metrics
                cycle.status = "completed"
                
                # Calculate improvement
                baseline_sr = cycle.baseline_metrics["success_rate"]
                improved_sr = improvement_metrics["success_rate"]
                improvement_pct = ((improved_sr - baseline_sr) / baseline_sr) * 100
                
                cycle.notes += f"\n\nImprovement: {improvement_pct:+.1f}% success rate"
                
                self.save()
                print(f"✅ Cycle #{cycle_id} marked complete!")
                print(f"   Improvement: {improvement_pct:+.1f}%")
                break
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learning cycles."""
        if not self.cycles:
            return {
                "total_cycles": 0,
                "completed_cycles": 0,
                "skills_improved": [],
                "avg_improvement": 0.0
            }
        
        completed = [c for c in self.cycles if c.status == "completed"]
        
        # Calculate average improvement
        improvements = []
        for cycle in completed:
            if cycle.improvement_metrics and cycle.baseline_metrics:
                baseline_sr = cycle.baseline_metrics["success_rate"]
                improved_sr = cycle.improvement_metrics["success_rate"]
                improvement_pct = ((improved_sr - baseline_sr) / baseline_sr) * 100
                improvements.append(improvement_pct)
        
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        # Skills improved
        skills = list(set(c.target_skill for c in completed))
        
        return {
            "total_cycles": len(self.cycles),
            "completed_cycles": len(completed),
            "in_progress_cycles": len([c for c in self.cycles if c.status == "ready_for_training"]),
            "skills_improved": skills,
            "avg_improvement": avg_improvement,
            "total_training_examples": sum(c.training_data_count for c in self.cycles)
        }
    
    def get_next_cycle_recommendation(self) -> Dict[str, Any]:
        """
        Recommend when to run next cycle and what to focus on.
        
        Returns:
            {
                "should_run": bool,
                "recommended_skill": str,
                "reason": str,
                "days_since_last_cycle": int
            }
        """
        # Check if we have a recent cycle
        if self.cycles:
            last_cycle = self.cycles[-1]
            last_cycle_date = datetime.fromisoformat(last_cycle.started_at)
            days_since = (datetime.now() - last_cycle_date).days
        else:
            days_since = 999  # No previous cycles
        
        # Should we run?
        should_run = days_since >= self.config["cycle_interval_days"]
        
        # What skill?
        priority_skills = self.failure_tracker.get_improvement_priority(
            days=self.config["lookback_days"]
        )
        
        recommended_skill = priority_skills[0] if priority_skills else None
        
        if not recommended_skill:
            return {
                "should_run": False,
                "recommended_skill": None,
                "reason": "No skills need improvement",
                "days_since_last_cycle": days_since
            }
        
        reason = f"Skill '{recommended_skill}' has highest improvement priority"
        
        if not should_run:
            wait_days = self.config["cycle_interval_days"] - days_since
            reason += f". Wait {wait_days} more days for scheduled interval."
        
        return {
            "should_run": should_run,
            "recommended_skill": recommended_skill,
            "reason": reason,
            "days_since_last_cycle": days_since
        }
    
    def schedule_weekly(self) -> str:
        """
        Schedule weekly learning cycles.
        
        Returns:
            Instructions for setting up scheduler
        """
        return """
To schedule weekly autodidactic learning cycles:

1. Add to crontab (Linux/Mac):
   0 2 * * 0 cd /path/to/AGI && python -c "from jessica.meta.autodidactic_loop import AutodidacticLoop; AutodidacticLoop().run_learning_cycle()"

2. Add to Windows Task Scheduler:
   - Action: Start a program
   - Program: python
   - Arguments: -c "from jessica.meta.autodidactic_loop import AutodidacticLoop; AutodidacticLoop().run_learning_cycle()"
   - Trigger: Weekly, Sunday at 2 AM

3. Manual integration with run_jessica.py:
   - Add weekly check in main agent loop
   - Call run_learning_cycle() automatically

4. Or run manually:
   python -c "from jessica.meta.autodidactic_loop import AutodidacticLoop; AutodidacticLoop().run_learning_cycle()"
"""
    
    def export_report(self, output_path: str = "autodidactic_report.txt") -> None:
        """Generate a human-readable report."""
        stats = self.get_learning_stats()
        recommendation = self.get_next_cycle_recommendation()
        
        report = f"""
========================================
AUTODIDACTIC LEARNING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================

SUMMARY
-------
Total learning cycles: {stats['total_cycles']}
Completed cycles: {stats['completed_cycles']}
In progress: {stats['in_progress_cycles']}
Skills improved: {', '.join(stats['skills_improved']) or 'None'}
Average improvement: {stats['avg_improvement']:.1f}%
Total training examples: {stats['total_training_examples']}

NEXT CYCLE
----------
Should run: {recommendation['should_run']}
Recommended skill: {recommendation['recommended_skill'] or 'None'}
Reason: {recommendation['reason']}
Days since last: {recommendation['days_since_last_cycle']}

CYCLE HISTORY
-------------
"""
        
        for cycle in self.cycles:
            report += f"\nCycle #{cycle.cycle_id}: {cycle.target_skill}\n"
            report += f"  Started: {cycle.started_at[:10]}\n"
            report += f"  Status: {cycle.status}\n"
            report += f"  Baseline success rate: {cycle.baseline_metrics['success_rate']:.1%}\n"
            
            if cycle.improvement_metrics:
                improved = cycle.improvement_metrics['success_rate']
                report += f"  Improved success rate: {improved:.1%}\n"
            
            report += f"  Training examples: {cycle.training_data_count}\n"
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"Report saved to: {output_path}")
    
    def save(self) -> None:
        """Persist state to disk."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        data = {
            "saved_at": datetime.now().isoformat(),
            "config": self.config,
            "cycle_count": len(self.cycles),
            "cycles": [c.to_dict() for c in self.cycles]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> None:
        """Load state from disk."""
        if not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.config.update(data.get("config", {}))
            self.cycles = [
                LearningCycle.from_dict(c)
                for c in data.get("cycles", [])
            ]
        except Exception as e:
            print(f"Warning: Could not load autodidactic state: {e}")
            self.cycles = []
