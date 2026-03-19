"""
Regret & Alternative-History Memory

Tracks mistakes, corrections, and "what I should have done instead."
Over time, regret shapes behavior more than rewards - this is wisdom accumulation.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class RegretToken:
    """A single regret - a mistake and its lesson."""
    regret_id: str
    timestamp: str
    trigger_type: str  # "correction", "failure", "confusion", "negative_feedback"
    
    # The situation
    situation: str  # What was happening
    context: Dict[str, Any]  # Full context (query, state, etc.)
    
    # What went wrong
    chosen_action: str  # What Jessica did
    outcome: str  # What happened as a result
    
    # What should have been done
    better_alternative: str  # What should have been done instead
    alternative_source: str  # "user_correction", "self_reflection", "pattern_analysis"
    
    # The lesson
    lesson: str  # Core lesson learned
    severity: int  # 1-10, how bad was the mistake
    
    # Wisdom tracking
    times_recalled: int  # How often this regret was remembered
    times_avoided: int  # Times this mistake was avoided later
    wisdom_score: float  # 0-1, how much this shaped behavior
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegretToken':
        """Create from dictionary."""
        return cls(**data)


class RegretMemory:
    """
    Alternative-history memory system that learns from mistakes.
    
    Usage:
        memory = RegretMemory()
        
        # Log a regret when user corrects Jessica
        memory.add_regret(
            trigger_type="correction",
            situation="User asked for Python code to reverse a string",
            chosen_action="Generated Java code instead",
            outcome="User said 'No, I need Python'",
            better_alternative="Generate Python code with proper syntax",
            lesson="Always match the requested programming language"
        )
        
        # Query regrets
        similar = memory.find_similar_regrets("reverse a string")
        lessons = memory.get_lessons_learned("programming")
    """
    
    def __init__(self, storage_dir: str = "jessica_data_embeddings"):
        self.storage_dir = storage_dir
        self.storage_path = os.path.join(storage_dir, "regret_memory.json")
        self.regrets: List[RegretToken] = []
        self.load()
    
    def add_regret(self, 
                  trigger_type: str,
                  situation: str,
                  chosen_action: str,
                  outcome: str,
                  better_alternative: str,
                  lesson: str,
                  context: Optional[Dict[str, Any]] = None,
                  alternative_source: str = "user_correction",
                  severity: int = 5) -> RegretToken:
        """
        Log a regret token.
        
        Args:
            trigger_type: What caused this regret ("correction", "failure", "confusion", "negative_feedback")
            situation: What was happening
            chosen_action: What Jessica did
            outcome: What happened as a result
            better_alternative: What should have been done
            lesson: Core lesson learned
            context: Additional context
            alternative_source: Where the alternative came from
            severity: 1-10, how bad was the mistake
            
        Returns:
            RegretToken object
        """
        regret = RegretToken(
            regret_id=f"regret_{len(self.regrets)}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            trigger_type=trigger_type,
            situation=situation,
            context=context or {},
            chosen_action=chosen_action,
            outcome=outcome,
            better_alternative=better_alternative,
            alternative_source=alternative_source,
            lesson=lesson,
            severity=max(1, min(10, severity)),
            times_recalled=0,
            times_avoided=0,
            wisdom_score=0.0
        )
        
        self.regrets.append(regret)
        self.save()
        
        return regret
    
    def add_correction(self, 
                      situation: str,
                      what_i_said: str,
                      what_user_said: str,
                      context: Optional[Dict[str, Any]] = None) -> RegretToken:
        """
        Convenience method for user corrections.
        
        Args:
            situation: What was being discussed
            what_i_said: Jessica's response
            what_user_said: User's correction
            context: Additional context
        """
        lesson = self._extract_lesson(what_i_said, what_user_said)
        
        return self.add_regret(
            trigger_type="correction",
            situation=situation,
            chosen_action=f"I said: {what_i_said}",
            outcome="User corrected me",
            better_alternative=f"I should have said: {what_user_said}",
            lesson=lesson,
            context=context,
            alternative_source="user_correction",
            severity=6
        )
    
    def add_confusion(self,
                     situation: str,
                     what_i_said: str,
                     confusion_indicators: List[str],
                     context: Optional[Dict[str, Any]] = None) -> RegretToken:
        """
        Log when user seems confused by Jessica's response.
        
        Args:
            situation: What was being discussed
            what_i_said: Jessica's response
            confusion_indicators: Signs of confusion ("what?", "huh?", "I don't understand")
            context: Additional context
        """
        return self.add_regret(
            trigger_type="confusion",
            situation=situation,
            chosen_action=f"I said: {what_i_said}",
            outcome=f"User seemed confused: {', '.join(confusion_indicators)}",
            better_alternative="I should have been clearer and more specific",
            lesson="Be more clear and specific in explanations",
            context=context,
            alternative_source="self_reflection",
            severity=5
        )
    
    def add_failed_advice(self,
                         situation: str,
                         advice_given: str,
                         why_it_failed: str,
                         what_worked: str,
                         context: Optional[Dict[str, Any]] = None) -> RegretToken:
        """
        Log when advice didn't work.
        
        Args:
            situation: What problem user was trying to solve
            advice_given: What Jessica recommended
            why_it_failed: Why the advice didn't work
            what_worked: What actually worked (if known)
            context: Additional context
        """
        return self.add_regret(
            trigger_type="failure",
            situation=situation,
            chosen_action=f"I advised: {advice_given}",
            outcome=f"It failed because: {why_it_failed}",
            better_alternative=f"Should have advised: {what_worked}",
            lesson=f"Learn from this failure: {why_it_failed}",
            context=context,
            alternative_source="pattern_analysis",
            severity=7
        )
    
    def find_similar_regrets(self, situation: str, limit: int = 5) -> List[RegretToken]:
        """
        Find regrets from similar situations.
        
        Args:
            situation: Current situation to match against
            limit: Max results
            
        Returns:
            List of similar regrets
        """
        # Simple keyword matching (could be enhanced with embeddings)
        keywords = set(situation.lower().split())
        
        scored_regrets = []
        for regret in self.regrets:
            regret_keywords = set(regret.situation.lower().split())
            overlap = len(keywords & regret_keywords)
            
            if overlap > 0:
                # Weight by wisdom score and overlap
                score = overlap * (1 + regret.wisdom_score)
                scored_regrets.append((score, regret))
        
        # Sort by score and return top N
        scored_regrets.sort(key=lambda x: x[0], reverse=True)
        return [regret for _, regret in scored_regrets[:limit]]
    
    def get_lessons_learned(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get consolidated lessons learned.
        
        Args:
            domain: Filter by domain (e.g., "programming", "advice")
            
        Returns:
            List of lessons with frequency and wisdom scores
        """
        lesson_stats = defaultdict(lambda: {
            "lesson": "",
            "count": 0,
            "avg_severity": 0,
            "total_wisdom": 0,
            "examples": []
        })
        
        for regret in self.regrets:
            # Filter by domain if specified
            if domain and domain.lower() not in regret.situation.lower():
                continue
            
            lesson = regret.lesson
            stats = lesson_stats[lesson]
            
            stats["lesson"] = lesson
            stats["count"] += 1
            stats["avg_severity"] += regret.severity
            stats["total_wisdom"] += regret.wisdom_score
            stats["examples"].append({
                "situation": regret.situation,
                "what_i_did": regret.chosen_action,
                "better_alternative": regret.better_alternative
            })
        
        # Calculate averages
        lessons = []
        for stats in lesson_stats.values():
            if stats["count"] > 0:
                stats["avg_severity"] /= stats["count"]
                stats["avg_wisdom"] = stats["total_wisdom"] / stats["count"]
                lessons.append(stats)
        
        # Sort by importance (count * avg_severity * avg_wisdom)
        lessons.sort(
            key=lambda x: x["count"] * x["avg_severity"] * x["avg_wisdom"],
            reverse=True
        )
        
        return lessons
    
    def mark_regret_recalled(self, regret_id: str) -> None:
        """
        Mark that a regret was recalled before acting.
        This increases wisdom score.
        """
        for regret in self.regrets:
            if regret.regret_id == regret_id:
                regret.times_recalled += 1
                regret.wisdom_score = min(1.0, regret.wisdom_score + 0.1)
                self.save()
                break
    
    def mark_mistake_avoided(self, regret_id: str) -> None:
        """
        Mark that a similar mistake was avoided.
        This significantly increases wisdom score.
        """
        for regret in self.regrets:
            if regret.regret_id == regret_id:
                regret.times_avoided += 1
                regret.wisdom_score = min(1.0, regret.wisdom_score + 0.2)
                self.save()
                break
    
    def get_wisdom_report(self) -> Dict[str, Any]:
        """
        Generate a wisdom accumulation report.
        
        Returns:
            Statistics about learning from regrets
        """
        if not self.regrets:
            return {
                "total_regrets": 0,
                "total_wisdom": 0,
                "top_lessons": [],
                "most_avoided_mistakes": [],
                "trigger_breakdown": {}
            }
        
        # Calculate stats
        total_wisdom = sum(r.wisdom_score for r in self.regrets)
        avg_wisdom = total_wisdom / len(self.regrets)
        
        # Top lessons by wisdom score
        top_lessons = sorted(
            self.regrets,
            key=lambda r: r.wisdom_score,
            reverse=True
        )[:5]
        
        # Most avoided mistakes
        most_avoided = sorted(
            self.regrets,
            key=lambda r: r.times_avoided,
            reverse=True
        )[:5]
        
        # Trigger breakdown
        trigger_counts = defaultdict(int)
        for regret in self.regrets:
            trigger_counts[regret.trigger_type] += 1
        
        return {
            "total_regrets": len(self.regrets),
            "total_wisdom": total_wisdom,
            "avg_wisdom_per_regret": avg_wisdom,
            "top_lessons": [
                {
                    "lesson": r.lesson,
                    "wisdom_score": r.wisdom_score,
                    "times_avoided": r.times_avoided,
                    "situation": r.situation
                }
                for r in top_lessons
            ],
            "most_avoided_mistakes": [
                {
                    "lesson": r.lesson,
                    "times_avoided": r.times_avoided,
                    "situation": r.situation
                }
                for r in most_avoided if r.times_avoided > 0
            ],
            "trigger_breakdown": dict(trigger_counts)
        }
    
    def get_alternative_history(self, regret_id: str) -> Dict[str, Any]:
        """
        Get the alternative history for a specific regret.
        
        Returns:
            {
                "what_happened": {...},
                "what_could_have_happened": {...}
            }
        """
        regret = None
        for r in self.regrets:
            if r.regret_id == regret_id:
                regret = r
                break
        
        if not regret:
            return {"error": "Regret not found"}
        
        return {
            "what_happened": {
                "situation": regret.situation,
                "my_action": regret.chosen_action,
                "outcome": regret.outcome,
                "severity": regret.severity
            },
            "what_could_have_happened": {
                "better_action": regret.better_alternative,
                "lesson_learned": regret.lesson,
                "source": regret.alternative_source,
                "wisdom_accumulated": regret.wisdom_score
            },
            "impact": {
                "times_recalled": regret.times_recalled,
                "times_avoided": regret.times_avoided,
                "changed_behavior": regret.times_avoided > 0
            }
        }
    
    def _extract_lesson(self, wrong: str, right: str) -> str:
        """
        Extract a lesson from wrong vs right responses.
        Simple heuristic - could be enhanced with LLM.
        """
        # Simple extraction based on patterns
        if "python" in right.lower() and "java" in wrong.lower():
            return "Match the requested programming language"
        elif len(right) > len(wrong) * 2:
            return "Provide more detailed and complete responses"
        elif "?" in wrong and "." in right:
            return "Give definitive answers, not questions"
        else:
            return "Pay closer attention to user's actual request"
    
    def clear_old_regrets(self, days: int = 90) -> int:
        """
        Clear regrets older than N days (keep only recent learning).
        
        Returns:
            Number of regrets cleared
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.regrets)
        
        self.regrets = [
            r for r in self.regrets
            if datetime.fromisoformat(r.timestamp) >= cutoff
        ]
        
        cleared = original_count - len(self.regrets)
        if cleared > 0:
            self.save()
        
        return cleared
    
    def save(self) -> None:
        """Persist regrets to disk."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
        data = {
            "saved_at": datetime.now().isoformat(),
            "regret_count": len(self.regrets),
            "total_wisdom": sum(r.wisdom_score for r in self.regrets),
            "regrets": [r.to_dict() for r in self.regrets]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> None:
        """Load regrets from disk."""
        if not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.regrets = [
                RegretToken.from_dict(r)
                for r in data.get("regrets", [])
            ]
        except Exception as e:
            print(f"Warning: Could not load regrets: {e}")
            self.regrets = []
