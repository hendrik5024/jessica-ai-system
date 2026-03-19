"""
Integration of Autonomous Refinement Module into Jessica's Autodidactic Loop

This module handles:
1. Integration with existing autodidactic_loop.py
2. Failure detection and routing to recursive_refiner
3. Learning cycle orchestration
4. Statistics and monitoring
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class LearningCycleCheckpoint:
    """Checkpoint in Jessica's learning week"""
    day: int  # 0-6 (Mon-Sun)
    phase: str  # "refinement", "testing", "integration"
    timestamp: float
    status: str  # "complete", "in_progress", "pending"


class RefinementCycleOrchestrator:
    """
    Orchestrates Jessica's self-refinement within the weekly learning cycle
    
    Integration Points:
    - Failure detection from interaction logs
    - Weekly refinement trigger (e.g., Sunday review)
    - Feedback integration into causal models
    - Safety constraints (personality inertia)
    """
    
    def __init__(self, 
                 autonomus_refinement_engine,
                 identity_anchors: Dict[str, Any] = None,
                 personality_inertia_threshold: float = 0.2):
        """
        Initialize orchestrator
        
        Args:
            autonomus_refinement_engine: Recursive refiner module
            identity_anchors: Core values (shouldn't change)
            personality_inertia_threshold: Max % of code to change per cycle
        """
        self.refinement_engine = autonomus_refinement_engine
        self.identity_anchors = identity_anchors or {}
        self.inertia_threshold = personality_inertia_threshold  # Max 20% change per week
        
        self.checkpoints: List[LearningCycleCheckpoint] = []
        self.cycle_history: List[Dict[str, Any]] = []
    
    def should_trigger_refinement(self) -> bool:
        """
        Determine if it's time for self-refinement
        
        Rules:
        - Weekly refinement cycle (default: Sunday)
        - On-demand if failure rate exceeds threshold
        - After major learning events
        """
        # Check: Is it refinement day? (mock)
        now = datetime.now()
        is_sunday = now.weekday() == 6
        
        if is_sunday:
            logger.info("✓ Weekly refinement trigger: Sunday")
            return True
        
        # Check: High failure rate? (mock)
        failure_rate = 0.05  # Would get from metrics
        if failure_rate > 0.10:  # > 10% failures
            logger.info(f"✓ Urgent refinement: Failure rate {failure_rate:.1%}")
            return True
        
        return False
    
    def validate_personality_constraints(self, patch: Any) -> bool:
        """
        Validate personality inertia:
        - Can't change core identity anchors
        - Can't modify greeting personality
        - Can't exceed 20% code change per week
        
        This ensures Jessica's core "self" is preserved
        """
        logger.info("Validating personality constraints...")
        
        protected_modules = [
            "jessica/brain/identity_anchors.py",
            "jessica/skills/greeting_skill.py",
            "jessica/meta/meta_observer.py"
        ]
        
        # Check 1: Protected modules
        if patch.source_module in protected_modules:
            logger.warning(f"  ✗ Module {patch.source_module} is protected")
            return False
        
        # Check 2: Code change magnitude
        change_magnitude = self._calculate_change_magnitude(patch)
        if change_magnitude > self.inertia_threshold:
            logger.warning(
                f"  ✗ Change too large: {change_magnitude:.0%} "
                f"(threshold: {self.inertia_threshold:.0%})"
            )
            return False
        
        logger.info("  ✓ Personality constraints satisfied")
        return True
    
    def integrate_learnings(self, refinement_records: List[Any]) -> Dict[str, Any]:
        """
        After successful refinement, integrate learnings into:
        1. Causal World Models (what was wrong, what's fixed)
        2. Regret Memory (mark failures as resolved)
        3. Meta-cognition Stack (update confidence calibration)
        4. Identity Anchors (reinforce values)
        """
        logger.info("Integrating learnings into Jessica's systems...")
        
        summary = {
            "causal_models_updated": 0,
            "regret_memory_cleared": 0,
            "confidence_calibration_changed": 0.0,
            "identity_reinforced": False
        }
        
        for record in refinement_records:
            if record.applied:
                # Update 1: Causal Models
                # Would call: self.causal_models.add_learned_causality(record)
                logger.info(f"  → Updated causal model for {record.patch_id}")
                summary["causal_models_updated"] += 1
                
                # Update 2: Regret Memory
                # Would call: self.regret_memory.mark_resolved(record.cluster_id)
                logger.info(f"  → Cleared regrets in {record.cluster_id}")
                summary["regret_memory_cleared"] += 1
                
                # Update 3: Confidence Calibration
                # Would call: self.meta_observer.update_calibration(record.wisdom_score)
                summary["confidence_calibration_changed"] += 0.05
        
        # Update 4: Identity Reinforcement
        logger.info("  → Reinforced identity anchors")
        summary["identity_reinforced"] = True
        
        return summary
    
    def run_weekly_refinement_cycle(self) -> Dict[str, Any]:
        """
        Run complete weekly refinement cycle
        
        Steps:
        1. Check if refinement should trigger
        2. Validate personality constraints
        3. Run self-correction cycle
        4. Integrate learnings
        5. Log results
        """
        logger.info(f"\n{'='*70}")
        logger.info("WEEKLY REFINEMENT CYCLE")
        logger.info(f"{'='*70}\n")
        
        # Step 1: Check trigger
        if not self.should_trigger_refinement():
            logger.info("Refinement not triggered")
            return {"triggered": False}
        
        # Step 2-3: Run refinement
        logger.info("Running self-correction cycle...")
        records = self.refinement_engine.run_self_correction_cycle()
        
        if not records:
            logger.warning("No refinement records generated")
            return {"triggered": True, "records": 0}
        
        # Step 4: Validate and integrate
        applied_records = []
        for record in records:
            if self.validate_personality_constraints(record.patch if hasattr(record, 'patch') else None):
                applied_records.append(record)
        
        learnings = self.integrate_learnings(applied_records)
        
        # Step 5: Log results
        cycle_result = {
            "triggered": True,
            "timestamp": datetime.now().isoformat(),
            "refinements_attempted": len(records),
            "refinements_applied": len(applied_records),
            "learnings": learnings,
            "statistics": self.refinement_engine.get_refinement_statistics()
        }
        
        self.cycle_history.append(cycle_result)
        
        logger.info(f"\nCycle Results:")
        logger.info(f"  • Refinements Attempted: {len(records)}")
        logger.info(f"  • Refinements Applied: {len(applied_records)}")
        logger.info(f"  • Causal Models Updated: {learnings['causal_models_updated']}")
        
        return cycle_result
    
    def on_critical_failure(self, failure_info: Dict[str, Any]) -> None:
        """
        Handle critical failure with immediate refinement
        
        Triggers emergency refinement if:
        - User explicitly requests fix
        - Repeated failures on same problem
        - Safety/alignment violation
        """
        logger.info(f"\n⚠ CRITICAL FAILURE DETECTED")
        logger.info(f"  Type: {failure_info.get('type', 'unknown')}")
        logger.info(f"  Module: {failure_info.get('module', 'unknown')}")
        
        # Could trigger immediate refinement instead of waiting for weekly cycle
        logger.info("  → Queuing for immediate analysis")
    
    def get_refinement_health_metrics(self) -> Dict[str, Any]:
        """Get overall health of Jessica's self-refinement process"""
        
        if not self.cycle_history:
            return {
                "cycles_completed": 0,
                "health_status": "no_data"
            }
        
        recent_cycles = self.cycle_history[-4:]  # Last month
        
        total_attempted = sum(c.get("refinements_attempted", 0) for c in recent_cycles)
        total_applied = sum(c.get("refinements_applied", 0) for c in recent_cycles)
        
        success_rate = (total_applied / total_attempted * 100) if total_attempted > 0 else 0
        
        return {
            "cycles_completed": len(self.cycle_history),
            "recent_cycles": len(recent_cycles),
            "total_refinements_attempted": total_attempted,
            "total_refinements_applied": total_applied,
            "success_rate": f"{success_rate:.0f}%",
            "health_status": "healthy" if success_rate > 60 else "needs_review"
        }
    
    def _calculate_change_magnitude(self, patch: Any) -> float:
        """Calculate what % of the module is changing"""
        # Mock: estimate from code length ratio
        if hasattr(patch, 'old_code') and hasattr(patch, 'new_code'):
            old_len = len(patch.old_code)
            new_len = len(patch.new_code)
            if old_len > 0:
                return abs(new_len - old_len) / old_len
        return 0.1


class AutonomousLearningIntegration:
    """
    High-level integration point between:
    - Jessica's main reasoning loop
    - Autodidactic learning cycle
    - Self-refinement system
    """
    
    def __init__(self, orchestrator: RefinementCycleOrchestrator):
        self.orchestrator = orchestrator
    
    def on_interaction_complete(self, interaction_summary: Dict[str, Any]) -> None:
        """Called after each interaction (conversation, task, etc.)"""
        
        # Log for pattern detection
        if interaction_summary.get("had_error"):
            logger.debug(f"Failure logged: {interaction_summary.get('error_type')}")
        
        # Check for critical failures
        if interaction_summary.get("error_severity", 0) > 0.8:
            self.orchestrator.on_critical_failure(interaction_summary)
    
    def on_learning_cycle_start(self) -> None:
        """Called at start of learning cycle (default: weekly)"""
        logger.info("\n🧠 Learning Cycle Starting...")
        self.orchestrator.run_weekly_refinement_cycle()
    
    def get_jessica_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "refinement_health": self.orchestrator.get_refinement_health_metrics(),
            "next_refinement": self._estimate_next_refinement(),
            "recommendation": self._generate_recommendation()
        }
    
    def _estimate_next_refinement(self) -> str:
        """Estimate when next refinement will occur"""
        now = datetime.now()
        days_until_sunday = (6 - now.weekday()) % 7
        
        if days_until_sunday == 0:
            return "Today (Sunday)"
        else:
            next_date = now + timedelta(days=days_until_sunday)
            return f"In {days_until_sunday} days ({next_date.strftime('%A')})"
    
    def _generate_recommendation(self) -> str:
        """Generate recommendation based on health"""
        health = self.orchestrator.get_refinement_health_metrics()
        success_rate_str = health.get("success_rate", "0%")
        success_rate = float(success_rate_str.rstrip('%')) if success_rate_str != "0%" else 0
        
        if success_rate > 80:
            return "✓ All systems healthy - Jessica learning well"
        elif success_rate > 60:
            return "⊘ Moderate refinement success - monitor closely"
        else:
            return "⚠ Low refinement success - review refinement strategy"


def create_refinement_integration(
    recursion_refiner,
    identity_anchors: Dict[str, Any] = None
) -> AutonomousLearningIntegration:
    """Factory function"""
    
    orchestrator = RefinementCycleOrchestrator(
        recursion_refiner,
        identity_anchors=identity_anchors
    )
    
    return AutonomousLearningIntegration(orchestrator)
