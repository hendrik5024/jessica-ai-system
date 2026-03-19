"""
Long-Term Recursive Reasoning - Integration

Integrates all System 2 reasoning components:
- Background cognition engine (idle detection)
- System 2 reasoner (counterfactual generation)
- Reflection window (existing meta-cognition)
- Regret memory (failure tracking)
- Autodidactic loop (learning application)

Main entry point for "Thinking Slow" capability.
"""

import time
import threading
from typing import Optional, Dict, Any
import logging

from jessica.meta.background_cognition import (
    BackgroundCognitionEngine,
    BackgroundTask,
    TaskPriority
)
from jessica.meta.system2_reasoner import (
    System2Reasoner,
    ReasoningDepth
)

logger = logging.getLogger(__name__)


class LongTermReasoningSystem:
    """
    Complete long-term recursive reasoning system
    
    During idle periods:
    1. Detects idle time (BackgroundCognitionEngine)
    2. Schedules System 2 reasoning tasks
    3. Processes failures with counterfactuals
    4. Extracts and applies learnings
    5. Updates prompts, knowledge, and strategies
    """
    
    def __init__(
        self,
        regret_memory,  # RegretMemoryStore
        autodidactic_loop,  # AutodidacticLoop
        reflection_window,  # ReflectionWindow (existing)
        enable_auto_start: bool = True
    ):
        # Core components
        self.regret_memory = regret_memory
        self.autodidactic_loop = autodidactic_loop
        self.reflection_window = reflection_window
        
        # Create subsystems
        self.background_engine = BackgroundCognitionEngine(
            idle_check_interval=10.0,  # Check every 10 seconds
            short_idle_threshold=300.0,  # 5 min
            medium_idle_threshold=900.0,  # 15 min
            long_idle_threshold=3600.0  # 1 hour
        )
        
        self.system2 = System2Reasoner(
            regret_memory=regret_memory,
            autodidactic_loop=autodidactic_loop,
            reflection_window=reflection_window
        )
        
        # Register background tasks
        self._register_thinking_tasks()
        
        # Auto-start if enabled
        if enable_auto_start:
            self.start()
            logger.info("Long-term reasoning system auto-started")
    
    def _register_thinking_tasks(self):
        """Register System 2 reasoning tasks with background engine"""
        
        # Task 1: Quick regret review (runs during short idle periods)
        self.background_engine.register_task(BackgroundTask(
            task_id="quick_regret_review",
            name="Quick Regret Review",
            function=self._quick_regret_review,
            priority=TaskPriority.HIGH,
            estimated_duration=120.0,  # 2 minutes
            min_idle_duration=300.0  # Requires 5 min idle
        ))
        
        # Task 2: Deep counterfactual analysis (runs during medium idle)
        self.background_engine.register_task(BackgroundTask(
            task_id="deep_counterfactual_analysis",
            name="Deep Counterfactual Analysis",
            function=self._deep_counterfactual_analysis,
            priority=TaskPriority.MEDIUM,
            estimated_duration=600.0,  # 10 minutes
            min_idle_duration=900.0  # Requires 15 min idle
        ))
        
        # Task 3: Cross-domain pattern synthesis (runs during long idle)
        self.background_engine.register_task(BackgroundTask(
            task_id="pattern_synthesis",
            name="Cross-Domain Pattern Synthesis",
            function=self._pattern_synthesis,
            priority=TaskPriority.LOW,
            estimated_duration=1200.0,  # 20 minutes
            min_idle_duration=3600.0  # Requires 1 hour idle
        ))
        
        logger.info("Registered 3 System 2 reasoning tasks")
    
    def _quick_regret_review(self, interrupt_flag) -> Dict[str, Any]:
        """
        Quick review of recent failures (last 24 hours)
        
        Runs during short idle periods (5-15 min)
        Shallow analysis to catch critical issues
        """
        logger.info("Starting quick regret review...")
        
        session = self.system2.think_slow(
            interrupt_flag=interrupt_flag,
            depth=ReasoningDepth.SHALLOW,
            time_range_hours=24  # Last 24 hours
        )
        
        return {
            "task": "quick_regret_review",
            "regrets_processed": session.regrets_processed,
            "counterfactuals": session.counterfactuals_generated,
            "learnings": session.learnings_extracted,
            "updates": session.updates_applied,
            "interrupted": session.interrupted
        }
    
    def _deep_counterfactual_analysis(self, interrupt_flag) -> Dict[str, Any]:
        """
        Deep analysis with full counterfactual trees (last 7 days)
        
        Runs during medium idle periods (15-60 min)
        Generates comprehensive alternative scenarios
        """
        logger.info("Starting deep counterfactual analysis...")
        
        session = self.system2.think_slow(
            interrupt_flag=interrupt_flag,
            depth=ReasoningDepth.DEEP,
            time_range_hours=168  # Last 7 days
        )
        
        return {
            "task": "deep_counterfactual_analysis",
            "regrets_processed": session.regrets_processed,
            "counterfactuals": session.counterfactuals_generated,
            "learnings": session.learnings_extracted,
            "updates": session.updates_applied,
            "patterns": len(session.results.get("patterns", [])),
            "interrupted": session.interrupted
        }
    
    def _pattern_synthesis(self, interrupt_flag) -> Dict[str, Any]:
        """
        Cross-domain pattern identification (last 30 days)
        
        Runs during long idle periods (>1 hour)
        Finds systemic issues across domains
        """
        logger.info("Starting cross-domain pattern synthesis...")
        
        # Process last 30 days with deep analysis
        session = self.system2.think_slow(
            interrupt_flag=interrupt_flag,
            depth=ReasoningDepth.DEEP,
            time_range_hours=720  # Last 30 days
        )
        
        # Also run existing reflection window for meta-analysis
        if not interrupt_flag.is_set():
            reflection_report = self.reflection_window.run(days=7)
            session.results["reflection_report"] = reflection_report
        
        return {
            "task": "pattern_synthesis",
            "regrets_processed": session.regrets_processed,
            "counterfactuals": session.counterfactuals_generated,
            "learnings": session.learnings_extracted,
            "updates": session.updates_applied,
            "patterns": len(session.results.get("patterns", [])),
            "reflection_included": not interrupt_flag.is_set(),
            "interrupted": session.interrupted
        }
    
    def start(self):
        """Start long-term reasoning system"""
        self.background_engine.start()
        logger.info("Long-term reasoning system started")
    
    def stop(self):
        """Stop long-term reasoning system"""
        self.background_engine.stop()
        logger.info("Long-term reasoning system stopped")
    
    def mark_activity(self):
        """
        Mark user activity (call this when user interacts)
        
        This resets the idle timer and interrupts any active thinking.
        """
        self.background_engine.mark_activity()
    
    def trigger_manual_reflection(
        self,
        depth: ReasoningDepth = ReasoningDepth.MEDIUM,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Manually trigger System 2 reasoning (doesn't require idle time)
        
        Useful for:
        - Testing
        - User-requested reflection
        - Scheduled analysis
        """
        logger.info(f"Manual reflection triggered: depth={depth.value}, range={time_range_hours}h")
        
        # Create a dummy interrupt flag (won't be set)
        interrupt_flag = threading.Event()
        
        session = self.system2.think_slow(
            interrupt_flag=interrupt_flag,
            depth=depth,
            time_range_hours=time_range_hours
        )
        
        return {
            "manual_trigger": True,
            "regrets_processed": session.regrets_processed,
            "counterfactuals_generated": session.counterfactuals_generated,
            "learnings_extracted": session.learnings_extracted,
            "updates_applied": session.updates_applied,
            "patterns": session.results.get("patterns", [])
        }
    
    def get_full_statistics(self) -> Dict[str, Any]:
        """Get complete system statistics"""
        bg_stats = self.background_engine.get_statistics()
        system2_stats = self.system2.get_statistics()
        task_stats = self.background_engine.get_task_statistics()
        
        return {
            "background_engine": bg_stats,
            "system2_reasoner": system2_stats,
            "task_breakdown": task_stats,
            "running": self.background_engine.running
        }
    
    def get_recent_learnings(self, limit: int = 10) -> list:
        """Get recent extracted learnings"""
        return self.system2.extracted_learnings[-limit:]
    
    def get_pending_prompt_updates(self) -> list:
        """Get pending prompt template updates"""
        return self.system2.prompt_updates


def create_long_term_reasoning_system(
    regret_memory,
    autodidactic_loop,
    reflection_window,
    enable_auto_start: bool = True
) -> LongTermReasoningSystem:
    """
    Create complete long-term reasoning system
    
    This is the main entry point for System 2 reasoning capability.
    
    Args:
        regret_memory: RegretMemoryStore instance
        autodidactic_loop: AutodidacticLoop instance
        reflection_window: ReflectionWindow instance (existing)
        enable_auto_start: Start background thinking automatically
    
    Returns:
        Configured LongTermReasoningSystem
    
    Example:
        # Create system
        system = create_long_term_reasoning_system(
            regret_memory=jessica.regret_memory,
            autodidactic_loop=jessica.autodidactic_loop,
            reflection_window=jessica.reflection_window
        )
        
        # It automatically runs in background during idle time
        
        # Mark user activity to interrupt thinking
        system.mark_activity()
        
        # Get statistics
        stats = system.get_full_statistics()
        print(f"Counterfactuals generated: {stats['system2_reasoner']['total_counterfactuals']}")
        
        # Get recent learnings
        learnings = system.get_recent_learnings(limit=5)
        for learning in learnings:
            print(f"- {learning.summary} (confidence={learning.confidence:.2f})")
    """
    return LongTermReasoningSystem(
        regret_memory=regret_memory,
        autodidactic_loop=autodidactic_loop,
        reflection_window=reflection_window,
        enable_auto_start=enable_auto_start
    )
