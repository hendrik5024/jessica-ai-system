"""
Background Cognition System - Thinking Slow (System 2)

Implements long-term recursive reasoning during idle periods.
Uses idle time to process failures, generate counterfactuals,
and improve future decision-making.

Key capabilities:
- Idle time detection and monitoring
- Background task scheduling
- Resource-aware computation
- Graceful interruption when user returns
"""

import time
import threading
from typing import Callable, List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class IdleState(Enum):
    """System idle states"""
    ACTIVE = "active"  # User actively engaged
    IDLE_SHORT = "idle_short"  # <5 min idle
    IDLE_MEDIUM = "idle_medium"  # 5-15 min idle
    IDLE_LONG = "idle_long"  # >15 min idle


class TaskPriority(Enum):
    """Background task priorities"""
    CRITICAL = 1  # Run immediately when idle
    HIGH = 2  # Run during medium idle
    MEDIUM = 3  # Run during long idle
    LOW = 4  # Run only during extended idle


@dataclass
class BackgroundTask:
    """Background cognition task"""
    task_id: str
    name: str
    function: Callable
    priority: TaskPriority
    estimated_duration: float  # seconds
    min_idle_duration: float  # minimum idle time required
    last_run: Optional[float] = None
    run_count: int = 0
    total_runtime: float = 0.0
    results: List[Any] = field(default_factory=list)
    
    def can_run(self, idle_duration: float, current_time: float) -> bool:
        """Check if task can run given current conditions"""
        # Must have sufficient idle time
        if idle_duration < self.min_idle_duration:
            return False
        
        # Respect run intervals (don't run too frequently)
        if self.last_run is not None:
            time_since_last = current_time - self.last_run
            min_interval = max(300, self.estimated_duration * 10)  # At least 5 min
            if time_since_last < min_interval:
                return False
        
        return True


@dataclass
class IdleSession:
    """Record of an idle period"""
    start_time: float
    end_time: Optional[float]
    duration: float
    tasks_run: List[str]
    results: Dict[str, Any]
    interrupted: bool = False


class BackgroundCognitionEngine:
    """
    Background cognition system for System 2 reasoning
    
    Monitors idle time and schedules long-term reasoning tasks:
    - Reflection windows
    - Counterfactual generation
    - Failure analysis
    - Strategy refinement
    """
    
    def __init__(
        self,
        idle_check_interval: float = 10.0,  # Check every 10 seconds
        short_idle_threshold: float = 300.0,  # 5 minutes
        medium_idle_threshold: float = 900.0,  # 15 minutes
        long_idle_threshold: float = 3600.0  # 1 hour
    ):
        self.idle_check_interval = idle_check_interval
        self.short_idle_threshold = short_idle_threshold
        self.medium_idle_threshold = medium_idle_threshold
        self.long_idle_threshold = long_idle_threshold
        
        # State tracking
        self.last_activity_time = time.time()
        self.current_idle_state = IdleState.ACTIVE
        self.idle_session_start: Optional[float] = None
        
        # Task management
        self.registered_tasks: Dict[str, BackgroundTask] = {}
        self.task_queue: List[BackgroundTask] = []
        self.current_task: Optional[BackgroundTask] = None
        
        # Background thread
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.interrupt_flag = threading.Event()
        
        # Session history
        self.idle_sessions: List[IdleSession] = []
        self.current_session: Optional[IdleSession] = None
        
        # Statistics
        self.total_idle_time = 0.0
        self.total_thinking_time = 0.0
        self.tasks_completed = 0
    
    def register_task(self, task: BackgroundTask):
        """Register a background cognition task"""
        self.registered_tasks[task.task_id] = task
        logger.info(f"Registered background task: {task.name} (priority={task.priority.value})")
    
    def mark_activity(self):
        """Mark user activity (resets idle timer)"""
        was_idle = self.current_idle_state != IdleState.ACTIVE
        
        self.last_activity_time = time.time()
        self.current_idle_state = IdleState.ACTIVE
        
        # If we were idle and had a session, end it
        if was_idle and self.current_session:
            self._end_idle_session(interrupted=True)
        
        # Interrupt any running background task
        if self.current_task:
            self.interrupt_flag.set()
            logger.info(f"Interrupted background task: {self.current_task.name}")
    
    def start(self):
        """Start background cognition engine"""
        if self.running:
            logger.warning("Background cognition already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._background_loop, daemon=True)
        self.thread.start()
        logger.info("Background cognition engine started")
    
    def stop(self):
        """Stop background cognition engine"""
        if not self.running:
            return
        
        self.running = False
        self.interrupt_flag.set()
        
        if self.thread:
            self.thread.join(timeout=5.0)
        
        logger.info("Background cognition engine stopped")
    
    def _background_loop(self):
        """Main background processing loop"""
        while self.running:
            try:
                current_time = time.time()
                
                # Update idle state
                idle_duration = current_time - self.last_activity_time
                self._update_idle_state(idle_duration)
                
                # Process background tasks if idle
                if self.current_idle_state != IdleState.ACTIVE:
                    self._process_background_tasks(idle_duration, current_time)
                
                # Sleep until next check
                time.sleep(self.idle_check_interval)
                
            except Exception as e:
                logger.error(f"Error in background cognition loop: {e}")
                time.sleep(60)  # Back off on error
    
    def _update_idle_state(self, idle_duration: float):
        """Update current idle state based on duration"""
        old_state = self.current_idle_state
        
        if idle_duration < self.short_idle_threshold:
            new_state = IdleState.ACTIVE
        elif idle_duration < self.medium_idle_threshold:
            new_state = IdleState.IDLE_SHORT
        elif idle_duration < self.long_idle_threshold:
            new_state = IdleState.IDLE_MEDIUM
        else:
            new_state = IdleState.IDLE_LONG
        
        # State transition
        if old_state != new_state:
            logger.info(f"Idle state transition: {old_state.value} → {new_state.value}")
            
            # Start new idle session
            if old_state == IdleState.ACTIVE and new_state != IdleState.ACTIVE:
                self._start_idle_session()
            
            self.current_idle_state = new_state
    
    def _start_idle_session(self):
        """Start tracking new idle session"""
        self.idle_session_start = time.time()
        self.current_session = IdleSession(
            start_time=self.idle_session_start,
            end_time=None,
            duration=0.0,
            tasks_run=[],
            results={}
        )
        logger.info("Started new idle session")
    
    def _end_idle_session(self, interrupted: bool = False):
        """End current idle session"""
        if not self.current_session:
            return
        
        current_time = time.time()
        self.current_session.end_time = current_time
        self.current_session.duration = current_time - self.current_session.start_time
        self.current_session.interrupted = interrupted
        
        self.idle_sessions.append(self.current_session)
        self.total_idle_time += self.current_session.duration
        
        logger.info(
            f"Ended idle session: duration={self.current_session.duration:.1f}s, "
            f"tasks={len(self.current_session.tasks_run)}, interrupted={interrupted}"
        )
        
        self.current_session = None
        self.idle_session_start = None
    
    def _process_background_tasks(self, idle_duration: float, current_time: float):
        """Select and run background tasks during idle time"""
        # Build queue of runnable tasks
        runnable = [
            task for task in self.registered_tasks.values()
            if task.can_run(idle_duration, current_time)
        ]
        
        if not runnable:
            return
        
        # Sort by priority
        runnable.sort(key=lambda t: t.priority.value)
        
        # Run highest priority task
        task = runnable[0]
        self._run_background_task(task)
    
    def _run_background_task(self, task: BackgroundTask):
        """Execute a background task with interruption support"""
        self.current_task = task
        self.interrupt_flag.clear()
        
        logger.info(f"Starting background task: {task.name}")
        start_time = time.time()
        
        try:
            # Run task function with interrupt flag
            result = task.function(interrupt_flag=self.interrupt_flag)
            
            # Record results
            elapsed = time.time() - start_time
            task.last_run = time.time()
            task.run_count += 1
            task.total_runtime += elapsed
            task.results.append(result)
            
            # Update session
            if self.current_session:
                self.current_session.tasks_run.append(task.task_id)
                self.current_session.results[task.task_id] = result
            
            self.total_thinking_time += elapsed
            self.tasks_completed += 1
            
            logger.info(
                f"Completed background task: {task.name} "
                f"(duration={elapsed:.1f}s, interrupted={self.interrupt_flag.is_set()})"
            )
            
        except Exception as e:
            logger.error(f"Error running background task {task.name}: {e}")
        
        finally:
            self.current_task = None
            self.interrupt_flag.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get background cognition statistics"""
        return {
            "current_state": self.current_idle_state.value,
            "total_idle_time": self.total_idle_time,
            "total_thinking_time": self.total_thinking_time,
            "tasks_completed": self.tasks_completed,
            "idle_sessions": len(self.idle_sessions),
            "registered_tasks": len(self.registered_tasks),
            "thinking_efficiency": self.total_thinking_time / self.total_idle_time if self.total_idle_time > 0 else 0,
            "avg_session_duration": sum(s.duration for s in self.idle_sessions) / len(self.idle_sessions) if self.idle_sessions else 0
        }
    
    def get_task_statistics(self) -> List[Dict[str, Any]]:
        """Get per-task statistics"""
        stats = []
        for task in self.registered_tasks.values():
            stats.append({
                "task_id": task.task_id,
                "name": task.name,
                "priority": task.priority.value,
                "run_count": task.run_count,
                "total_runtime": task.total_runtime,
                "avg_runtime": task.total_runtime / task.run_count if task.run_count > 0 else 0,
                "last_run": datetime.fromtimestamp(task.last_run).isoformat() if task.last_run else None
            })
        return stats


def create_background_engine(
    idle_check_interval: float = 10.0
) -> BackgroundCognitionEngine:
    """Create and configure background cognition engine"""
    engine = BackgroundCognitionEngine(
        idle_check_interval=idle_check_interval,
        short_idle_threshold=300.0,  # 5 min
        medium_idle_threshold=900.0,  # 15 min
        long_idle_threshold=3600.0  # 1 hour
    )
    
    return engine
