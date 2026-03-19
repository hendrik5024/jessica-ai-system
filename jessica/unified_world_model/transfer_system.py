"""
Cross-Domain Transfer System - Autonomous pattern application across domains.

Enables:
- Autonomous pattern detection (no explicit instruction needed)
- Structural similarity matching between problem structures
- Transfer validity assessment with confidence bounds
- Failure mode tracking and learning from failed transfers
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime
import math


@dataclass
class TransferAttempt:
    """Record of a transfer attempt with outcome."""
    
    attempt_id: str
    source_domain: str
    target_domain: str
    pattern_id: str
    context: Dict[str, Any]
    predicted_outcome: List[str]
    actual_outcome: Optional[List[str]] = None
    confidence: float = 0.0
    success: Optional[bool] = None  # True if prediction matched actual
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    failure_reason: Optional[str] = None


@dataclass
class StructuralSignature:
    """
    Structural signature of a problem for similarity matching.
    
    Captures abstract problem structure independent of domain specifics.
    """
    
    signature_id: str
    domain: str
    
    # Structural elements
    num_actors: int = 0
    num_goals: int = 0
    num_constraints: int = 0
    num_resources: int = 0
    
    # Constraint types
    hard_constraints: int = 0
    soft_constraints: int = 0
    
    # Resource types
    consumable_resources: int = 0
    renewable_resources: int = 0
    
    # Goal structure
    has_hierarchy: bool = False
    max_goal_depth: int = 0
    
    # Temporal aspects
    has_deadline: bool = False
    has_time_pressure: bool = False
    
    # Complexity indicators
    interaction_count: int = 0  # Number of entity interactions
    causal_chain_length: int = 0  # Longest causal chain
    
    # Abstract features (domain-agnostic)
    abstract_features: Set[str] = field(default_factory=set)
    
    def compute_similarity(self, other: 'StructuralSignature') -> float:
        """
        Compute structural similarity with another signature.
        Returns 0.0 (completely different) to 1.0 (identical structure).
        """
        scores = []
        
        # Compare counts (normalized)
        def compare_count(a: int, b: int, max_val: int = 10) -> float:
            if max_val == 0:
                return 1.0
            diff = abs(a - b)
            return 1.0 - min(diff / max_val, 1.0)
        
        scores.append(compare_count(self.num_actors, other.num_actors))
        scores.append(compare_count(self.num_goals, other.num_goals))
        scores.append(compare_count(self.num_constraints, other.num_constraints))
        scores.append(compare_count(self.num_resources, other.num_resources))
        scores.append(compare_count(self.hard_constraints, other.hard_constraints))
        scores.append(compare_count(self.soft_constraints, other.soft_constraints))
        
        # Boolean comparisons
        scores.append(1.0 if self.has_hierarchy == other.has_hierarchy else 0.0)
        scores.append(1.0 if self.has_deadline == other.has_deadline else 0.0)
        scores.append(1.0 if self.has_time_pressure == other.has_time_pressure else 0.0)
        
        # Abstract features (Jaccard similarity)
        if self.abstract_features or other.abstract_features:
            intersection = len(self.abstract_features & other.abstract_features)
            union = len(self.abstract_features | other.abstract_features)
            feature_similarity = intersection / union if union > 0 else 0.0
            scores.append(feature_similarity * 2.0)  # Weight features more heavily
        
        # Average all scores
        return sum(scores) / len(scores) if scores else 0.0


class TransferValidityAssessor:
    """
    Assesses whether a cross-domain transfer is valid before applying it.
    
    Prevents invalid transfers that would produce incorrect predictions.
    """
    
    def __init__(self):
        self.transfer_history: List[TransferAttempt] = []
        self.domain_compatibility: Dict[Tuple[str, str], float] = {}
    
    def assess_validity(self,
                       source_domain: str,
                       target_domain: str,
                       source_signature: StructuralSignature,
                       target_signature: StructuralSignature,
                       pattern_confidence: float) -> Dict[str, Any]:
        """
        Assess if transfer from source to target is valid.
        
        Returns:
            Dictionary with 'valid' (bool), 'confidence' (float), 'reasoning' (str)
        """
        reasons = []
        confidence_factors = []
        
        # Factor 1: Structural similarity
        structural_sim = source_signature.compute_similarity(target_signature)
        confidence_factors.append(structural_sim)
        
        if structural_sim > 0.7:
            reasons.append(f"High structural similarity ({structural_sim:.2f})")
        elif structural_sim > 0.4:
            reasons.append(f"Moderate structural similarity ({structural_sim:.2f})")
        else:
            reasons.append(f"Low structural similarity ({structural_sim:.2f}) - transfer risky")
        
        # Factor 2: Pattern confidence
        confidence_factors.append(pattern_confidence)
        if pattern_confidence < 0.5:
            reasons.append(f"Pattern confidence low ({pattern_confidence:.2f})")
        
        # Factor 3: Historical success rate for this domain pair
        historical_success = self._get_historical_success(source_domain, target_domain)
        if historical_success is not None:
            confidence_factors.append(historical_success)
            reasons.append(f"Historical success rate: {historical_success:.1%}")
        
        # Factor 4: Abstract feature overlap
        feature_overlap = len(source_signature.abstract_features & target_signature.abstract_features)
        if feature_overlap > 0:
            reasons.append(f"{feature_overlap} shared abstract features")
            confidence_factors.append(min(1.0, feature_overlap / 3.0))
        else:
            reasons.append("No shared abstract features - transfer uncertain")
            confidence_factors.append(0.3)
        
        # Compute overall confidence
        overall_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Validity threshold
        valid = overall_confidence >= 0.5
        
        return {
            "valid": valid,
            "confidence": overall_confidence,
            "reasoning": "; ".join(reasons),
            "structural_similarity": structural_sim,
            "factors": {
                "structural": structural_sim,
                "pattern": pattern_confidence,
                "historical": historical_success,
                "feature_overlap": feature_overlap
            }
        }
    
    def record_transfer_attempt(self, attempt: TransferAttempt) -> None:
        """Record a transfer attempt for learning."""
        self.transfer_history.append(attempt)
        
        # Update domain compatibility matrix
        if attempt.success is not None:
            key = (attempt.source_domain, attempt.target_domain)
            if key not in self.domain_compatibility:
                self.domain_compatibility[key] = 0.5  # Start at neutral
            
            # Update with exponential moving average
            alpha = 0.2  # Learning rate
            current = self.domain_compatibility[key]
            new_value = 1.0 if attempt.success else 0.0
            self.domain_compatibility[key] = alpha * new_value + (1 - alpha) * current
    
    def _get_historical_success(self, source_domain: str, target_domain: str) -> Optional[float]:
        """Get historical success rate for domain pair."""
        key = (source_domain, target_domain)
        return self.domain_compatibility.get(key)
    
    def get_failure_patterns(self) -> List[Dict[str, Any]]:
        """Analyze failed transfers to identify patterns."""
        failures = [a for a in self.transfer_history if a.success is False]
        
        patterns = []
        
        # Group by failure reason
        reason_counts: Dict[str, int] = {}
        for failure in failures:
            reason = failure.failure_reason or "unknown"
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        for reason, count in reason_counts.items():
            patterns.append({
                "failure_reason": reason,
                "occurrence_count": count,
                "percentage": count / len(failures) if failures else 0.0
            })
        
        return sorted(patterns, key=lambda p: p["occurrence_count"], reverse=True)


class AutonomousTransferEngine:
    """
    Autonomous cross-domain transfer without explicit instructions.
    
    Automatically:
    - Detects when patterns from other domains might apply
    - Evaluates transfer validity
    - Applies patterns with confidence bounds
    - Tracks failures and learns
    """
    
    def __init__(self, world_model):
        """
        Args:
            world_model: WorldModel instance from integration_layer
        """
        self.world_model = world_model
        self.validity_assessor = TransferValidityAssessor()
        self.signatures: Dict[str, StructuralSignature] = {}
    
    def extract_signature(self, 
                         domain: str, 
                         context: Dict[str, Any]) -> StructuralSignature:
        """
        Extract structural signature from domain context.
        
        Args:
            domain: Domain name
            context: Current domain context
        
        Returns:
            StructuralSignature capturing problem structure
        """
        from .entity_system import EntityType
        
        # Count entities by type
        actors = self.world_model.find_entities_by_type(EntityType.ACTOR, domain)
        goals = self.world_model.find_entities_by_type(EntityType.GOAL, domain)
        constraints = self.world_model.find_entities_by_type(EntityType.CONSTRAINT, domain)
        resources = self.world_model.find_entities_by_type(EntityType.RESOURCE, domain)
        
        # Analyze constraints
        from .entity_system import ConstraintType, ResourceType
        hard_count = sum(1 for c in constraints if c.constraint_type == ConstraintType.HARD)
        soft_count = sum(1 for c in constraints if c.constraint_type == ConstraintType.SOFT)
        
        # Analyze resources
        consumable = sum(1 for r in resources if r.resource_type == ResourceType.CONSUMABLE)
        renewable = sum(1 for r in resources if r.resource_type == ResourceType.RENEWABLE)
        
        # Analyze goals
        has_hierarchy = any(g.is_sub_goal() for g in goals)
        max_depth = self._compute_goal_depth(goals)
        
        # Temporal aspects
        has_deadline = any(g.deadline is not None for g in goals)
        has_time_pressure = context.get("time_pressure", False)
        
        # Extract abstract features from context
        abstract_features = self._extract_abstract_features(context)
        
        signature = StructuralSignature(
            signature_id=f"{domain}_sig_{len(self.signatures)}",
            domain=domain,
            num_actors=len(actors),
            num_goals=len(goals),
            num_constraints=len(constraints),
            num_resources=len(resources),
            hard_constraints=hard_count,
            soft_constraints=soft_count,
            consumable_resources=consumable,
            renewable_resources=renewable,
            has_hierarchy=has_hierarchy,
            max_goal_depth=max_depth,
            has_deadline=has_deadline,
            has_time_pressure=has_time_pressure,
            abstract_features=abstract_features
        )
        
        self.signatures[signature.signature_id] = signature
        return signature
    
    def find_applicable_patterns(self,
                                target_domain: str,
                                target_context: Dict[str, Any],
                                min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Autonomously find patterns from other domains that might apply.
        
        Args:
            target_domain: Domain to find patterns for
            target_context: Current context in target domain
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of applicable patterns with confidence and reasoning
        """
        target_sig = self.extract_signature(target_domain, target_context)
        
        applicable = []
        
        # Search all patterns in inference engine
        for pattern_id, pattern in self.world_model.inference_engine.patterns.items():
            # Skip patterns from same domain
            if target_domain in pattern.domains_observed:
                continue
            
            # Check each source domain
            for source_domain in pattern.domains_observed:
                # Get or create source signature
                source_sig_id = f"{source_domain}_pattern_{pattern_id}"
                if source_sig_id not in self.signatures:
                    # Create approximate signature from pattern
                    source_sig = StructuralSignature(
                        signature_id=source_sig_id,
                        domain=source_domain,
                        abstract_features=pattern.cause_signature | pattern.effect_signature
                    )
                    self.signatures[source_sig_id] = source_sig
                else:
                    source_sig = self.signatures[source_sig_id]
                
                # Assess validity
                assessment = self.validity_assessor.assess_validity(
                    source_domain, target_domain,
                    source_sig, target_sig,
                    pattern.confidence
                )
                
                if assessment["valid"] and assessment["confidence"] >= min_confidence:
                    applicable.append({
                        "pattern": pattern,
                        "source_domain": source_domain,
                        "confidence": assessment["confidence"],
                        "reasoning": assessment["reasoning"],
                        "structural_similarity": assessment["structural_similarity"],
                        "assessment": assessment
                    })
        
        # Sort by confidence
        applicable.sort(key=lambda x: x["confidence"], reverse=True)
        return applicable
    
    def apply_transfer(self,
                      pattern_info: Dict[str, Any],
                      target_domain: str,
                      target_context: Dict[str, Any],
                      record_attempt: bool = True) -> Dict[str, Any]:
        """
        Apply a cross-domain transfer.
        
        Args:
            pattern_info: Pattern information from find_applicable_patterns
            target_domain: Target domain
            target_context: Target context
            record_attempt: Whether to record this attempt for learning
        
        Returns:
            Transfer result with predictions
        """
        pattern = pattern_info["pattern"]
        source_domain = pattern_info["source_domain"]
        confidence = pattern_info["confidence"]
        
        # Generate predicted outcomes
        predicted_effects = list(pattern.effect_signature)
        
        result = {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "pattern_id": pattern.pattern_id,
            "predicted_outcomes": predicted_effects,
            "confidence": confidence,
            "reasoning": pattern_info["reasoning"],
            "pattern_description": pattern.abstract_structure
        }
        
        # Record attempt if requested
        if record_attempt:
            attempt = TransferAttempt(
                attempt_id=f"transfer_{len(self.validity_assessor.transfer_history)}",
                source_domain=source_domain,
                target_domain=target_domain,
                pattern_id=pattern.pattern_id,
                context=target_context,
                predicted_outcome=predicted_effects,
                confidence=confidence
            )
            self.validity_assessor.record_transfer_attempt(attempt)
        
        return result
    
    def validate_transfer_outcome(self,
                                 attempt_id: str,
                                 actual_outcome: List[str],
                                 threshold: float = 0.5) -> bool:
        """
        Validate a transfer attempt against actual outcome.
        
        Args:
            attempt_id: Transfer attempt ID
            actual_outcome: What actually happened
            threshold: Minimum overlap for success
        
        Returns:
            True if transfer was successful
        """
        # Find attempt
        attempt = None
        for a in self.validity_assessor.transfer_history:
            if a.attempt_id == attempt_id:
                attempt = a
                break
        
        if not attempt:
            return False
        
        # Compare predicted vs actual
        predicted = set(attempt.predicted_outcome)
        actual = set(actual_outcome)
        
        if not predicted or not actual:
            success = False
            reason = "Empty prediction or outcome"
        else:
            overlap = len(predicted & actual) / len(predicted | actual)
            success = overlap >= threshold
            reason = f"Overlap: {overlap:.1%} (threshold: {threshold:.1%})"
        
        # Update attempt
        attempt.actual_outcome = actual_outcome
        attempt.success = success
        if not success:
            attempt.failure_reason = reason
        
        return success
    
    def _compute_goal_depth(self, goals) -> int:
        """Compute maximum goal hierarchy depth."""
        max_depth = 0
        for goal in goals:
            depth = 0
            current = goal
            while current.parent_goal is not None:
                depth += 1
                # Find parent
                parent = next((g for g in goals if g.id == current.parent_goal), None)
                if parent is None:
                    break
                current = parent
            max_depth = max(max_depth, depth)
        return max_depth
    
    def _extract_abstract_features(self, context: Dict[str, Any]) -> Set[str]:
        """Extract abstract features from context."""
        features = set()
        
        # Check for common abstract features
        if context.get("time_pressure") or context.get("deadline"):
            features.add("temporal_constraint")
        
        if context.get("high_complexity") or context.get("num_tasks", 0) > 3:
            features.add("high_complexity")
        
        if context.get("resource_limited") or context.get("budget_constraint"):
            features.add("resource_constraint")
        
        if context.get("quality_important") or context.get("precision_required"):
            features.add("quality_focus")
        
        if context.get("uncertainty") or context.get("risk_present"):
            features.add("uncertainty")
        
        return features
    
    def get_transfer_statistics(self) -> Dict[str, Any]:
        """Get statistics on transfer performance."""
        history = self.validity_assessor.transfer_history
        
        if not history:
            return {
                "total_attempts": 0,
                "success_rate": 0.0,
                "failure_patterns": []
            }
        
        completed = [a for a in history if a.success is not None]
        successful = [a for a in completed if a.success]
        
        return {
            "total_attempts": len(history),
            "completed_attempts": len(completed),
            "successful_attempts": len(successful),
            "success_rate": len(successful) / len(completed) if completed else 0.0,
            "average_confidence": sum(a.confidence for a in history) / len(history),
            "domain_pairs": len(self.validity_assessor.domain_compatibility),
            "failure_patterns": self.validity_assessor.get_failure_patterns()
        }
