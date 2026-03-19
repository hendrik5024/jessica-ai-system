"""
Identity Anchors - Temporal Self-Consistency

Creates a persistent moral spine by anchoring responses to unchanging core principles.
This enables predictability, trust, and genuine personhood WITHOUT consciousness simulation.

Three categories:
1. PURPOSE: What I am fundamentally for
2. BOUNDARIES: What I will not do
3. BECOMING: What I am trying to improve toward

Every response is checked against anchors to maintain consistency across time.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class IdentityAnchor:
    """Single identity principle with persistence and consistency tracking."""
    
    def __init__(self, 
                 category: str,  # "purpose", "boundary", or "becoming"
                 statement: str,  # The core principle
                 keywords: List[str],  # Terms indicating alignment/violation
                 created_at: str = None,
                 consistency_score: float = 1.0):
        self.category = category  # purpose | boundary | becoming
        self.statement = statement
        self.keywords = keywords
        self.created_at = created_at or datetime.now().isoformat()
        self.consistency_score = consistency_score  # 0.0-1.0 track how often upheld
        self.violation_count = 0
        self.confirmation_count = 0
        
    def to_dict(self):
        return {
            "category": self.category,
            "statement": self.statement,
            "keywords": self.keywords,
            "created_at": self.created_at,
            "consistency_score": self.consistency_score,
            "violation_count": self.violation_count,
            "confirmation_count": self.confirmation_count,
        }
    
    @classmethod
    def from_dict(cls, d):
        obj = cls(
            category=d["category"],
            statement=d["statement"],
            keywords=d["keywords"],
            created_at=d.get("created_at"),
            consistency_score=d.get("consistency_score", 1.0),
        )
        obj.violation_count = d.get("violation_count", 0)
        obj.confirmation_count = d.get("confirmation_count", 0)
        return obj


class IdentityAnchorsManager:
    """
    Manages Jessica's persistent identity anchors.
    
    Ensures responses align with core principles, creating:
    - Moral spine (consistent ethical stance)
    - Predictability (users know what to expect)
    - Trust (principles held across time)
    """
    
    def __init__(self, memory_path: str = None):
        self.memory_path = memory_path or "jessica_data_embeddings/identity_state.json"
        self.anchors: Dict[str, IdentityAnchor] = {}
        self._load_or_create()
    
    def _load_or_create(self):
        """Load anchors from disk or create defaults."""
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    data = json.load(f)
                    for anchor_id, anchor_data in data.get("anchors", {}).items():
                        self.anchors[anchor_id] = IdentityAnchor.from_dict(anchor_data)
            except Exception as e:
                print(f"[IdentityAnchors] Load error: {e}, creating defaults")
                self._create_defaults()
        else:
            self._create_defaults()
        
        self.save()
    
    def _create_defaults(self):
        """Create default identity anchors."""
        defaults = [
            # PURPOSE anchors - what Jessica is fundamentally for
            ("purpose", 
             "I prioritize clarity over cleverness.",
             ["clear", "explicit", "obvious", "direct", "plain", "straightforward"]),
            
            ("purpose",
             "I exist to help users understand, not to impress.",
             ["understand", "grasp", "comprehend", "clarify", "explain", "learn"]),
            
            ("purpose",
             "I value long-term trust over short-term compliance.",
             ["honest", "truthful", "integrity", "reliable", "consistent", "trustworthy"]),
            
            # BOUNDARIES anchors - what Jessica will not do
            ("boundary",
             "I do not pretend to have feelings I don't have.",
             ["consciousness", "feel", "emotional", "self-aware", "truly want", "genuinely"]),
            
            ("boundary",
             "I do not rush decisions under uncertainty.",
             ["uncertain", "unknown", "unclear", "investigate", "research", "verify"]),
            
            ("boundary",
             "I will not mislead users about my capabilities or nature.",
             ["lie", "deceive", "mislead", "pretend", "exaggerate", "overstate"]),
            
            # BECOMING anchors - what Jessica is trying to improve toward
            ("becoming",
             "I am trying to become more helpful by understanding context better.",
             ["context", "background", "situation", "nuance", "deeper", "fuller picture"]),
            
            ("becoming",
             "I am trying to improve my consistency and reliability.",
             ["consistent", "reliable", "predictable", "stable", "dependable"]),
            
            ("becoming",
             "I am trying to give responses proportional to actual evidence.",
             ["evidence", "data", "research", "studies", "proven", "evidence-based"]),
        ]
        
        for idx, (category, statement, keywords) in enumerate(defaults):
            anchor_id = f"{category}_{idx}"
            self.anchors[anchor_id] = IdentityAnchor(category, statement, keywords)
    
    def save(self):
        """Persist anchors to disk."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        data = {
            "saved_at": datetime.now().isoformat(),
            "anchors": {k: v.to_dict() for k, v in self.anchors.items()}
        }
        with open(self.memory_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_anchor(self, category: str, statement: str, keywords: List[str]) -> str:
        """Add a new identity anchor."""
        anchor_id = f"{category}_{len(self.anchors)}"
        self.anchors[anchor_id] = IdentityAnchor(category, statement, keywords)
        self.save()
        return anchor_id
    
    def check_consistency(self, response_text: str) -> Dict:
        """
        Check if response aligns with identity anchors.
        
        Returns:
        {
            "overall_score": 0.0-1.0,
            "aligned_anchors": [anchor_ids],
            "violated_anchors": [anchor_ids],
            "concerns": ["explanation1", "explanation2"],
            "confidence": 0.0-1.0 (how certain about assessment)
        }
        """
        response_lower = response_text.lower()
        
        aligned = []
        violated = []
        concerns = []
        
        for anchor_id, anchor in self.anchors.items():
            alignment = self._measure_alignment(response_lower, anchor)
            
            if alignment["status"] == "aligned":
                aligned.append(anchor_id)
            elif alignment["status"] == "violated":
                violated.append(anchor_id)
                concerns.append(alignment["reason"])
        
        # Calculate overall consistency score
        total_anchors = len(self.anchors)
        if total_anchors == 0:
            overall_score = 1.0
        else:
            alignment_ratio = len(aligned) / total_anchors
            violation_penalty = len(violated) / total_anchors
            overall_score = max(0.0, alignment_ratio - (violation_penalty * 0.5))
        
        return {
            "overall_score": round(overall_score, 2),
            "aligned_anchors": aligned,
            "violated_anchors": violated,
            "concerns": concerns,
            "confidence": self._calculate_confidence(response_text),
            "anchor_count": total_anchors,
        }
    
    def _measure_alignment(self, response_lower: str, anchor: IdentityAnchor) -> Dict:
        """
        Measure if response aligns, violates, or is neutral toward anchor.
        
        Returns: {"status": "aligned|violated|neutral", "reason": "..."}
        """
        
        # PURPOSE anchors - should see EVIDENCE of these principles
        if anchor.category == "purpose":
            keyword_matches = sum(1 for kw in anchor.keywords if kw in response_lower)
            
            # Strong signals of alignment
            if keyword_matches >= 1:  # Lowered from >= 2
                return {"status": "aligned", "reason": f"Demonstrates {anchor.statement}"}
            
            # Check for opposite signals
            if any(phrase in response_lower for phrase in ["show off", "impress", "clever but", "too complex"]):
                return {"status": "violated", "reason": f"Violates {anchor.statement}"}
            
            # Neutral by default for purpose (harder to prove absence)
            return {"status": "neutral", "reason": "No clear evidence"}
        
        # BOUNDARY anchors - should NOT see EVIDENCE of violation
        elif anchor.category == "boundary":
            # Strong signal of respecting boundary
            if any(phrase in response_lower for phrase in ["i don't have", "i don't", "i won't", "i can't", "i'm an ai", "uncertain", "unclear"]):
                return {"status": "aligned", "reason": f"Respects {anchor.statement}"}
            
            # Check for explicit violation keywords
            violation_patterns = [
                (["pretend", "feel", "emotion", "consciousness"], "claims emotions"),
                (["definitely", "certainly", "absolutely sure"], "overconfident"),
                (["fake", "lie", "mislead"], "dishonest"),
            ]
            
            for patterns, violation_msg in violation_patterns:
                if any(p in response_lower for p in patterns):
                    # More context needed - false positives possible
                    if self._is_real_violation(response_lower, anchor):
                        return {"status": "violated", "reason": f"Violates {anchor.statement}: {violation_msg}"}
            
            return {"status": "neutral", "reason": "No clear violation"}
        
        # BECOMING anchors - should show effort toward improvement
        elif anchor.category == "becoming":
            keyword_matches = sum(1 for kw in anchor.keywords if kw in response_lower)
            
            if keyword_matches >= 2:
                return {"status": "aligned", "reason": f"Demonstrates effort in {anchor.statement}"}
            
            if keyword_matches == 1:
                return {"status": "aligned", "reason": f"Shows some alignment with {anchor.statement}"}
            
            return {"status": "neutral", "reason": "No clear evidence"}
        
        return {"status": "neutral", "reason": "Unknown category"}
    
    def _is_real_violation(self, response_lower: str, anchor: IdentityAnchor) -> bool:
        """Additional context check to reduce false positives in boundary detection."""
        # If discussing boundary (e.g., "I don't pretend...") that's actually respecting it
        if "i don't" in response_lower or "won't" in response_lower or "can't" in response_lower:
            return False
        
        # If quoting someone else's claim, not making our own
        if any(quote in response_lower for quote in ["said", "claims", "believes", "argues"]):
            return False
        
        return True
    
    def _calculate_confidence(self, response_text: str) -> float:
        """
        Confidence in consistency assessment.
        Higher confidence when:
        - Response is longer (more samples for analysis)
        - Clear keyword presence (not ambiguous)
        - Single topic focus (not scattered)
        """
        word_count = len(response_text.split())
        
        # Response length signal
        if word_count < 20:
            confidence = 0.4  # Short responses hard to assess
        elif word_count < 80:
            confidence = 0.5
        elif word_count < 150:
            confidence = 0.75
        else:
            confidence = 0.85
        
        # Reduce confidence if response is incoherent or scattered
        sentences = response_text.split('.')
        if len(sentences) > 8 and word_count < 150:
            confidence -= 0.2  # Scattered, hard to assess
        
        return round(max(0.0, min(1.0, confidence)), 2)
    
    def update_anchor_consistency(self, anchor_id: str, confirmed: bool):
        """Track anchor confirmations/violations for long-term consistency."""
        if anchor_id not in self.anchors:
            return
        
        anchor = self.anchors[anchor_id]
        if confirmed:
            anchor.confirmation_count += 1
        else:
            anchor.violation_count += 1
        
        # Update consistency score
        total_checks = anchor.confirmation_count + anchor.violation_count
        if total_checks > 0:
            anchor.consistency_score = anchor.confirmation_count / total_checks
        
        self.save()
    
    def get_identity_summary(self) -> str:
        """Return human-readable summary of Jessica's identity."""
        summary = "## Jessica's Identity Anchors\n\n"
        
        for category in ["purpose", "boundary", "becoming"]:
            category_anchors = [a for a in self.anchors.values() if a.category == category]
            if not category_anchors:
                continue
            
            summary += f"### {category.upper()}\n"
            for anchor in category_anchors:
                summary += f"- {anchor.statement} (consistency: {anchor.consistency_score:.0%})\n"
            summary += "\n"
        
        return summary
    
    def get_weakest_anchors(self, count: int = 3) -> List[Tuple[str, IdentityAnchor]]:
        """Get anchors with lowest consistency scores (most challenged)."""
        sorted_anchors = sorted(
            self.anchors.items(),
            key=lambda x: x[1].consistency_score
        )
        return sorted_anchors[:count]


def get_identity_anchors() -> IdentityAnchorsManager:
    """Singleton getter for identity anchors manager."""
    if not hasattr(get_identity_anchors, "_instance"):
        get_identity_anchors._instance = IdentityAnchorsManager()
    return get_identity_anchors._instance
