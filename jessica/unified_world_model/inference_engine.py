"""
Inference engine - cross-domain pattern matching and application.

Enables:
- Pattern extraction from one domain
- Similarity matching to find analogous structures
- Pattern application to novel domains
- Confidence estimation for transfer validity
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple
from .entity_system import Entity, CausalLink, Actor, Goal, Constraint, Resource


@dataclass
class Pattern:
    """
    Abstracted pattern that can be matched across domains.
    
    Example: "Pressure increases → mistakes increase"
    - Abstract: high_stress_condition → performance_degradation
    - Chess: time_pressure → blunder_rate_increase
    - Cooking: simultaneous_tasks → coordination_errors
    - Decisions: deadline_pressure → hasty_choices
    """
    
    pattern_id: str
    abstract_structure: str  # Human-readable description
    cause_signature: Set[str]  # Required cause features
    effect_signature: Set[str]  # Expected effect features
    confidence: float = 1.0
    domains_observed: Set[str] = field(default_factory=set)
    instances: List[Dict[str, Any]] = field(default_factory=list)
    
    def matches_cause(self, conditions: Set[str]) -> float:
        """
        Check how well conditions match cause signature.
        Returns similarity score 0.0 to 1.0.
        """
        if not self.cause_signature:
            return 0.0
        
        intersection = self.cause_signature & conditions
        union = self.cause_signature | conditions
        
        # Jaccard similarity
        return len(intersection) / len(union) if union else 0.0
    
    def is_domain_agnostic(self) -> bool:
        """Check if pattern applies across multiple domains."""
        return len(self.domains_observed) >= 2


@dataclass
class InferenceRule:
    """
    Rule for applying patterns from one domain to another.
    
    Example:
    - Source: chess (time_pressure → blunders)
    - Target: cooking (simultaneous_tasks → ?)
    - Mapping: time_pressure ≈ simultaneous_tasks (both are stress)
    - Inference: simultaneous_tasks → cooking_errors
    """
    
    rule_id: str
    source_domain: str
    target_domain: str
    feature_mapping: Dict[str, str]  # Source feature → target feature
    pattern: Pattern
    validity_confidence: float = 0.5
    
    def apply(self, target_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply pattern to target domain context.
        Returns predicted outcomes with confidence.
        """
        # Map source features to target features
        mapped_conditions = set()
        for source_feature, target_feature in self.feature_mapping.items():
            if source_feature in self.pattern.cause_signature:
                if target_feature in target_context.get("conditions", set()):
                    mapped_conditions.add(target_feature)
        
        # Check if mapped conditions match pattern cause
        match_score = self.pattern.matches_cause(mapped_conditions)
        
        if match_score > 0.5:
            # Predict effects in target domain
            effects = []
            for effect in self.pattern.effect_signature:
                # Map effect to target domain
                target_effect = self.feature_mapping.get(effect, effect)
                effects.append(target_effect)
            
            return {
                "predicted_effects": effects,
                "confidence": match_score * self.validity_confidence,
                "reasoning": f"Pattern from {self.source_domain} applies to {self.target_domain}",
                "match_score": match_score
            }
        
        return {
            "predicted_effects": [],
            "confidence": 0.0,
            "reasoning": "Pattern conditions not met in target context"
        }


@dataclass
class PatternMatch:
    """Result of pattern matching attempt."""
    
    pattern: Pattern
    similarity: float
    applicable: bool
    reasoning: str
    predicted_outcomes: List[str] = field(default_factory=list)


class InferenceEngine:
    """
    Cross-domain inference engine for pattern extraction and application.
    """
    
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.rules: List[InferenceRule] = []
        self.domain_signatures: Dict[str, Set[str]] = {}
    
    def extract_pattern(self, causal_link: CausalLink, domain: str) -> Pattern:
        """
        Extract abstract pattern from a causal link.
        
        Args:
            causal_link: Domain-specific causal link
            domain: Domain name
        
        Returns:
            Abstract pattern that can be matched across domains
        """
        # Convert specific conditions to abstract features
        cause_features = self._abstract_features(causal_link.cause_conditions, domain)
        effect_features = self._abstract_features(causal_link.effect_outcomes, domain)
        
        # Check if pattern already exists
        pattern_id = f"pattern_{len(self.patterns)}"
        for existing_id, existing_pattern in self.patterns.items():
            if (existing_pattern.cause_signature == cause_features and
                existing_pattern.effect_signature == effect_features):
                # Pattern exists, add this domain
                existing_pattern.domains_observed.add(domain)
                existing_pattern.instances.append({
                    "domain": domain,
                    "causal_link": causal_link
                })
                return existing_pattern
        
        # Create new pattern
        pattern = Pattern(
            pattern_id=pattern_id,
            abstract_structure=f"{', '.join(cause_features)} → {', '.join(effect_features)}",
            cause_signature=cause_features,
            effect_signature=effect_features,
            confidence=causal_link.confidence,
            domains_observed={domain},
            instances=[{"domain": domain, "causal_link": causal_link}]
        )
        
        self.patterns[pattern_id] = pattern
        return pattern
    
    def find_similar_patterns(self, 
                            conditions: Set[str], 
                            source_domain: str,
                            min_similarity: float = 0.6) -> List[PatternMatch]:
        """
        Find patterns that match given conditions.
        
        Args:
            conditions: Current conditions to match
            source_domain: Domain to search in
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of matching patterns with similarity scores
        """
        matches = []
        
        for pattern in self.patterns.values():
            # Skip if pattern not from this domain
            if source_domain not in pattern.domains_observed:
                continue
            
            similarity = pattern.matches_cause(conditions)
            
            if similarity >= min_similarity:
                match = PatternMatch(
                    pattern=pattern,
                    similarity=similarity,
                    applicable=True,
                    reasoning=f"Conditions match pattern cause (similarity: {similarity:.2f})",
                    predicted_outcomes=list(pattern.effect_signature)
                )
                matches.append(match)
        
        # Sort by similarity
        matches.sort(key=lambda m: m.similarity, reverse=True)
        return matches
    
    def create_transfer_rule(self,
                           pattern: Pattern,
                           source_domain: str,
                           target_domain: str,
                           feature_mapping: Dict[str, str]) -> InferenceRule:
        """
        Create rule for transferring pattern from source to target domain.
        
        Args:
            pattern: Pattern to transfer
            source_domain: Source domain
            target_domain: Target domain
            feature_mapping: How features map between domains
        
        Returns:
            Inference rule
        """
        # Calculate validity confidence based on pattern history
        validity = 0.5  # Base validity
        if pattern.is_domain_agnostic():
            validity += 0.3  # Bonus for multi-domain patterns
        
        rule = InferenceRule(
            rule_id=f"rule_{source_domain}_to_{target_domain}_{len(self.rules)}",
            source_domain=source_domain,
            target_domain=target_domain,
            feature_mapping=feature_mapping,
            pattern=pattern,
            validity_confidence=validity
        )
        
        self.rules.append(rule)
        return rule
    
    def apply_cross_domain(self,
                          source_domain: str,
                          target_domain: str,
                          target_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply patterns from source domain to target domain.
        
        Args:
            source_domain: Domain with known patterns
            target_domain: Domain to apply patterns to
            target_context: Current state in target domain
        
        Returns:
            Predictions and confidence
        """
        # Find applicable rules
        applicable_rules = [
            rule for rule in self.rules
            if rule.source_domain == source_domain and rule.target_domain == target_domain
        ]
        
        if not applicable_rules:
            return {
                "predictions": [],
                "confidence": 0.0,
                "reasoning": f"No transfer rules from {source_domain} to {target_domain}"
            }
        
        # Apply rules and collect predictions
        all_predictions = []
        for rule in applicable_rules:
            result = rule.apply(target_context)
            if result["confidence"] > 0.5:
                all_predictions.append(result)
        
        if not all_predictions:
            return {
                "predictions": [],
                "confidence": 0.0,
                "reasoning": "No applicable patterns matched target context"
            }
        
        # Return highest confidence prediction
        best_prediction = max(all_predictions, key=lambda p: p["confidence"])
        return {
            "predictions": best_prediction["predicted_effects"],
            "confidence": best_prediction["confidence"],
            "reasoning": best_prediction["reasoning"],
            "match_score": best_prediction.get("match_score", 0.0)
        }
    
    def _abstract_features(self, specific_features: List[str], domain: str) -> Set[str]:
        """
        Convert domain-specific features to abstract features.
        
        Example:
        - chess: "time_pressure" → "stress_condition"
        - cooking: "simultaneous_tasks" → "stress_condition"
        """
        # Feature abstraction mapping
        abstraction_map = {
            # Stress conditions
            "time_pressure": "stress_condition",
            "simultaneous_tasks": "stress_condition",
            "deadline_pressure": "stress_condition",
            "high_complexity": "stress_condition",
            
            # Performance degradation
            "blunder_rate_increase": "performance_degradation",
            "coordination_errors": "performance_degradation",
            "hasty_choices": "performance_degradation",
            "quality_reduction": "performance_degradation",
            
            # Resource depletion
            "time_running_out": "resource_depletion",
            "energy_depleted": "resource_depletion",
            "attention_exhausted": "resource_depletion",
            
            # Skill improvement
            "practice_increase": "skill_building",
            "repetition": "skill_building",
            "deliberate_practice": "skill_building",
            
            # Quality improvement
            "skill_increase": "quality_improvement",
            "mastery_gained": "quality_improvement",
            "expertise_developed": "quality_improvement"
        }
        
        abstract = set()
        for feature in specific_features:
            # Try to abstract, otherwise keep original
            abstract_feature = abstraction_map.get(feature, feature)
            abstract.add(abstract_feature)
        
        return abstract
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get inference engine statistics."""
        domain_agnostic = sum(1 for p in self.patterns.values() if p.is_domain_agnostic())
        
        return {
            "total_patterns": len(self.patterns),
            "domain_agnostic_patterns": domain_agnostic,
            "total_rules": len(self.rules),
            "domains_tracked": len(self.domain_signatures)
        }
