"""
Failure Tracker for Autodidactic Loop

Tracks failures, errors, and low-quality responses to identify
areas where Jessica needs improvement.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict


@dataclass
class FailureEvent:
    """A single failure event."""
    timestamp: str
    skill: str  # Which skill failed
    category: str  # Type of failure (error, low_quality, timeout, etc.)
    description: str
    context: Dict[str, Any]  # User query, system state, etc.
    severity: int  # 1-10, how bad was the failure
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FailureEvent':
        """Create from dictionary."""
        return cls(**data)


class FailureTracker:
    """
    Tracks and analyzes failures to identify learning opportunities.
    
    Usage:
        tracker = FailureTracker()
        
        # Log failures
        tracker.log_failure(
            skill="programming",
            category="syntax_error",
            description="Generated invalid Python code",
            context={"query": "write a function..."},
            severity=7
        )
        
        # Analyze
        clusters = tracker.get_failure_clusters(days=7)
        weakest = tracker.identify_weakest_skills(threshold=0.3)
    """
    
    def __init__(self, storage_dir: str = "jessica_data_embeddings"):
        self.storage_dir = storage_dir
        self.storage_path = os.path.join(storage_dir, "failure_log.json")
        self.failures: List[FailureEvent] = []
        self.load()
    
    def log_failure(self, skill: str, category: str, description: str,
                   context: Optional[Dict[str, Any]] = None,
                   severity: int = 5) -> None:
        """
        Log a failure event.
        
        Args:
            skill: Which skill failed (programming, advice, chess, etc.)
            category: Type of failure (error, low_quality, timeout, incorrect_answer, etc.)
            description: What went wrong
            context: Additional context (user query, system state, etc.)
            severity: 1-10, how bad was the failure
        """
        event = FailureEvent(
            timestamp=datetime.now().isoformat(),
            skill=skill,
            category=category,
            description=description,
            context=context or {},
            severity=max(1, min(10, severity))
        )
        
        self.failures.append(event)
        self.save()
    
    def log_success(self, skill: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a successful interaction (helps with success rate calculation).
        
        Args:
            skill: Which skill succeeded
            context: Additional context
        """
        event = FailureEvent(
            timestamp=datetime.now().isoformat(),
            skill=skill,
            category="success",
            description="Successful interaction",
            context=context or {},
            severity=0  # Success has no severity
        )
        
        self.failures.append(event)
        self.save()
    
    def get_failure_clusters(self, days: int = 7) -> Dict[str, List[FailureEvent]]:
        """
        Get failures clustered by skill from the last N days.
        
        Returns:
            {"skill_name": [failure1, failure2, ...]}
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_failures = [
            f for f in self.failures
            if datetime.fromisoformat(f.timestamp) >= cutoff
            and f.category != "success"
        ]
        
        clusters = defaultdict(list)
        for failure in recent_failures:
            clusters[failure.skill].append(failure)
        
        return dict(clusters)
    
    def identify_weakest_skills(self, days: int = 7, min_samples: int = 3) -> List[Dict[str, Any]]:
        """
        Identify skills with highest failure rates.
        
        Args:
            days: Look back this many days
            min_samples: Only consider skills with at least this many interactions
            
        Returns:
            List of skills sorted by failure rate (worst first):
            [
                {
                    "skill": "programming",
                    "total_interactions": 50,
                    "failures": 15,
                    "success_rate": 0.7,
                    "avg_severity": 6.2,
                    "top_categories": ["syntax_error", "logic_error"]
                },
                ...
            ]
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_events = [
            e for e in self.failures
            if datetime.fromisoformat(e.timestamp) >= cutoff
        ]
        
        # Group by skill
        skill_stats = defaultdict(lambda: {
            "total": 0,
            "failures": 0,
            "severity_sum": 0,
            "categories": []
        })
        
        for event in recent_events:
            stats = skill_stats[event.skill]
            stats["total"] += 1
            
            if event.category != "success":
                stats["failures"] += 1
                stats["severity_sum"] += event.severity
                stats["categories"].append(event.category)
        
        # Calculate metrics
        weakest = []
        for skill, stats in skill_stats.items():
            if stats["total"] < min_samples:
                continue
            
            failure_count = stats["failures"]
            success_rate = 1 - (failure_count / stats["total"])
            avg_severity = stats["severity_sum"] / failure_count if failure_count > 0 else 0
            
            # Get top failure categories
            category_counts = Counter(stats["categories"])
            top_categories = [cat for cat, _ in category_counts.most_common(3)]
            
            weakest.append({
                "skill": skill,
                "total_interactions": stats["total"],
                "failures": failure_count,
                "success_rate": success_rate,
                "avg_severity": avg_severity,
                "top_categories": top_categories
            })
        
        # Sort by failure rate (lowest success rate first)
        weakest.sort(key=lambda x: x["success_rate"])
        
        return weakest
    
    def get_failure_patterns(self, skill: str, days: int = 30) -> Dict[str, Any]:
        """
        Analyze patterns in failures for a specific skill.
        
        Returns:
            {
                "common_errors": [("syntax_error", 15), ...],
                "severity_distribution": {1-10: count},
                "time_distribution": {hour: count},
                "example_failures": [failure1, failure2, ...]
            }
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        skill_failures = [
            f for f in self.failures
            if f.skill == skill
            and datetime.fromisoformat(f.timestamp) >= cutoff
            and f.category != "success"
        ]
        
        # Common error categories
        categories = Counter(f.category for f in skill_failures)
        
        # Severity distribution
        severity_dist = Counter(f.severity for f in skill_failures)
        
        # Time distribution (hour of day)
        time_dist = Counter(
            datetime.fromisoformat(f.timestamp).hour
            for f in skill_failures
        )
        
        # Example failures (worst ones)
        examples = sorted(skill_failures, key=lambda f: f.severity, reverse=True)[:5]
        
        return {
            "common_errors": categories.most_common(10),
            "severity_distribution": dict(severity_dist),
            "time_distribution": dict(time_dist),
            "example_failures": [f.to_dict() for f in examples]
        }
    
    def get_improvement_priority(self, days: int = 7) -> List[str]:
        """
        Get prioritized list of skills to improve.
        
        Priority based on:
        1. Failure rate
        2. Severity
        3. Frequency of use
        
        Returns:
            ["programming", "advice", "chess", ...]
        """
        weakest = self.identify_weakest_skills(days=days)
        
        # Calculate priority score
        for skill_data in weakest:
            # Lower success rate = higher priority
            failure_weight = (1 - skill_data["success_rate"]) * 10
            
            # Higher severity = higher priority
            severity_weight = skill_data["avg_severity"]
            
            # More usage = higher priority
            usage_weight = min(10, skill_data["total_interactions"] / 5)
            
            skill_data["priority_score"] = (
                failure_weight * 0.5 +
                severity_weight * 0.3 +
                usage_weight * 0.2
            )
        
        # Sort by priority score
        weakest.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return [s["skill"] for s in weakest]
    
    def clear_old_data(self, days: int = 90) -> int:
        """
        Clear failures older than N days.
        
        Returns:
            Number of failures cleared
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.failures)
        
        self.failures = [
            f for f in self.failures
            if datetime.fromisoformat(f.timestamp) >= cutoff
        ]
        
        cleared = original_count - len(self.failures)
        if cleared > 0:
            self.save()
        
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        if not self.failures:
            return {
                "total_events": 0,
                "total_failures": 0,
                "total_successes": 0,
                "overall_success_rate": 0.0,
                "skills_tracked": []
            }
        
        total_failures = sum(1 for f in self.failures if f.category != "success")
        total_successes = sum(1 for f in self.failures if f.category == "success")
        total_events = len(self.failures)
        
        success_rate = total_successes / total_events if total_events > 0 else 0
        
        skills = list(set(f.skill for f in self.failures))
        
        return {
            "total_events": total_events,
            "total_failures": total_failures,
            "total_successes": total_successes,
            "overall_success_rate": success_rate,
            "skills_tracked": sorted(skills)
        }
    
    def save(self) -> None:
        """Persist failures to disk."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        data = {
            "saved_at": datetime.now().isoformat(),
            "failure_count": len(self.failures),
            "failures": [f.to_dict() for f in self.failures]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> None:
        """Load failures from disk."""
        if not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.failures = [
                FailureEvent.from_dict(f)
                for f in data.get("failures", [])
            ]
        except Exception as e:
            print(f"Warning: Could not load failures: {e}")
            self.failures = []
