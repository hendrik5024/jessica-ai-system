"""
Integration layer - connects unified world model with existing domain models.

Provides:
- WorldModel: Central orchestration of entities, patterns, and inference
- DomainAdapter: Converts domain-specific knowledge into unified representation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple
from .entity_system import (
    Entity, Actor, Goal, Constraint, Resource, State, 
    Relation, CausalLink, EntityType
)
from .inference_engine import InferenceEngine, Pattern, InferenceRule
from .unified_variables import (
    TimeVariable, EnergyVariable, AttentionVariable, RiskVariable
)


class DomainAdapter:
    """
    Adapts domain-specific knowledge into unified representation.
    
    Each domain (chess, cooking, travel, etc.) has an adapter that:
    1. Extracts entities from domain-specific data
    2. Converts domain rules into causal links
    3. Maps domain variables to unified variables
    """
    
    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self.entity_mappings: Dict[str, str] = {}  # Domain term → Entity ID
        self.variable_mappings: Dict[str, str] = {}  # Domain variable → Unified variable
    
    def adapt_causal_rule(self, 
                         domain_rule: Dict[str, Any]) -> CausalLink:
        """
        Convert domain-specific rule to causal link.
        
        Args:
            domain_rule: Dictionary with 'conditions', 'outcomes', 'confidence'
        
        Returns:
            CausalLink in unified representation
        """
        causal_link = CausalLink(
            name=f"{self.domain_name}_{domain_rule.get('name', 'rule')}",
            domain=self.domain_name,
            cause_conditions=domain_rule.get("conditions", []),
            effect_outcomes=domain_rule.get("outcomes", []),
            confidence=domain_rule.get("confidence", 0.8),
            delay=domain_rule.get("delay", 0.0),
            domain_agnostic=False
        )
        
        return causal_link
    
    def extract_actors(self, domain_context: Dict[str, Any]) -> List[Actor]:
        """Extract actors from domain context."""
        actors = []
        
        # Domain-specific extraction
        if self.domain_name == "chess":
            # Chess player as actor
            player = Actor(
                name="chess_player",
                domain=self.domain_name,
                capabilities={"calculate_tactics", "evaluate_position", "plan_strategy"},
                resources={"time": domain_context.get("time_remaining", 300), 
                          "mental_energy": domain_context.get("mental_energy", 100)}
            )
            actors.append(player)
        
        elif self.domain_name == "cooking":
            # Chef as actor
            chef = Actor(
                name="chef",
                domain=self.domain_name,
                capabilities={"prepare_ingredients", "cook", "multitask"},
                resources={"time": domain_context.get("cooking_time", 60),
                          "physical_energy": domain_context.get("energy", 100),
                          "attention": domain_context.get("attention", 100)}
            )
            actors.append(chef)
        
        return actors
    
    def extract_goals(self, domain_context: Dict[str, Any]) -> List[Goal]:
        """Extract goals from domain context."""
        goals = []
        
        if self.domain_name == "chess":
            goal = Goal(
                name="win_game",
                domain=self.domain_name,
                success_criteria=["checkmate_opponent"],
                priority=1.0
            )
            goals.append(goal)
        
        elif self.domain_name == "cooking":
            goal = Goal(
                name="prepare_meal",
                domain=self.domain_name,
                success_criteria=domain_context.get("success_criteria", ["all_courses_ready"]),
                deadline=domain_context.get("deadline", None)
            )
            goals.append(goal)
        
        return goals
    
    def extract_constraints(self, domain_context: Dict[str, Any]) -> List[Constraint]:
        """Extract constraints from domain context."""
        constraints = []
        
        # Common time constraint
        if "time_limit" in domain_context:
            time_constraint = Constraint(
                name="time_limit",
                domain=self.domain_name,
                constraint_type=domain_context.get("constraint_type", "hard"),
                condition=f"Must complete within {domain_context['time_limit']} units"
            )
            constraints.append(time_constraint)
        
        return constraints


class WorldModel:
    """
    Central unified world model that orchestrates entities, patterns, and inference.
    
    This is the integration point for all domain knowledge, providing:
    - Entity storage and retrieval
    - Pattern extraction and matching
    - Cross-domain inference
    - Unified variable tracking
    """
    
    def __init__(self):
        # Core components
        self.entities: Dict[str, Entity] = {}
        self.inference_engine = InferenceEngine()
        
        # Domain adapters
        self.adapters: Dict[str, DomainAdapter] = {}
        
        # Unified variables
        self.time_var = TimeVariable()
        self.energy_var = EnergyVariable()
        self.attention_var = AttentionVariable()
        self.risk_var = RiskVariable()
        
        # Relations and causal links
        self.relations: List[Relation] = []
        self.causal_links: List[CausalLink] = []
    
    def register_domain(self, domain_name: str) -> DomainAdapter:
        """Register a new domain and return its adapter."""
        if domain_name not in self.adapters:
            self.adapters[domain_name] = DomainAdapter(domain_name)
        return self.adapters[domain_name]
    
    def add_entity(self, entity: Entity) -> str:
        """Add entity to world model. Returns entity ID."""
        self.entities[entity.id] = entity
        return entity.id
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)
    
    def find_entities_by_type(self, entity_type: EntityType, domain: Optional[str] = None) -> List[Entity]:
        """Find all entities of a given type, optionally filtered by domain."""
        results = []
        for entity in self.entities.values():
            if entity.entity_type == entity_type:
                if domain is None or entity.domain == domain:
                    results.append(entity)
        return results
    
    def add_causal_link(self, causal_link: CausalLink) -> None:
        """
        Add causal link and extract pattern.
        """
        self.causal_links.append(causal_link)
        
        # Extract pattern from causal link
        if causal_link.domain:
            pattern = self.inference_engine.extract_pattern(causal_link, causal_link.domain)
    
    def predict_cross_domain(self,
                           source_domain: str,
                           target_domain: str,
                           target_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict outcomes in target domain using patterns from source domain.
        
        Args:
            source_domain: Domain with known patterns (e.g., "chess")
            target_domain: Domain to make predictions in (e.g., "cooking")
            target_context: Current state in target domain
        
        Returns:
            Dictionary with predictions, confidence, reasoning
        """
        return self.inference_engine.apply_cross_domain(
            source_domain, target_domain, target_context
        )
    
    def compare_variable_across_domains(self,
                                       variable_name: str,
                                       domain_a: str,
                                       context_a: Dict[str, Any],
                                       domain_b: str,
                                       context_b: Dict[str, Any]) -> str:
        """
        Compare a unified variable across two domains.
        
        Args:
            variable_name: "time", "energy", "attention", or "risk"
            domain_a, domain_b: Domain names
            context_a, context_b: Contexts in each domain
        
        Returns:
            Comparison string
        """
        # Select variable
        if variable_name == "time":
            var = self.time_var
        elif variable_name == "energy":
            var = self.energy_var
        elif variable_name == "attention":
            var = self.attention_var
        elif variable_name == "risk":
            var = self.risk_var
        else:
            return f"Unknown variable: {variable_name}"
        
        # Get domain-specific values
        value_a = var.domain_specific_value(domain_a, context_a)
        value_b = var.domain_specific_value(domain_b, context_b)
        
        # Compare
        return var.compare_across_domains(domain_a, value_a, domain_b, value_b)
    
    def find_analogous_problems(self,
                               problem_domain: str,
                               problem_conditions: Set[str],
                               min_similarity: float = 0.6) -> List[Tuple[str, float, List[str]]]:
        """
        Find analogous problems in other domains.
        
        Args:
            problem_domain: Current domain
            problem_conditions: Current problem conditions
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of (domain, similarity, predicted_outcomes)
        """
        results = []
        
        # Find patterns that match problem conditions
        matches = self.inference_engine.find_similar_patterns(
            problem_conditions, problem_domain, min_similarity
        )
        
        for match in matches:
            # For each matching pattern, find domains where it applies
            for other_domain in match.pattern.domains_observed:
                if other_domain != problem_domain:
                    results.append((
                        other_domain,
                        match.similarity,
                        match.predicted_outcomes
                    ))
        
        return results
    
    def create_cross_domain_mapping(self,
                                   source_domain: str,
                                   target_domain: str,
                                   feature_mapping: Dict[str, str]) -> InferenceRule:
        """
        Create explicit mapping between domains for transfer.
        
        Args:
            source_domain: Source domain with patterns
            target_domain: Target domain to apply patterns
            feature_mapping: How features map (source → target)
        
        Returns:
            Inference rule
        """
        # Find patterns from source domain
        source_patterns = [
            pattern for pattern in self.inference_engine.patterns.values()
            if source_domain in pattern.domains_observed
        ]
        
        if not source_patterns:
            raise ValueError(f"No patterns found in {source_domain}")
        
        # Use first pattern as template (in real use, would select best match)
        pattern = source_patterns[0]
        
        return self.inference_engine.create_transfer_rule(
            pattern, source_domain, target_domain, feature_mapping
        )
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get current state of world model."""
        return {
            "entities": {
                "total": len(self.entities),
                "by_type": {
                    entity_type.value: len(self.find_entities_by_type(entity_type))
                    for entity_type in EntityType
                }
            },
            "domains": list(self.adapters.keys()),
            "causal_links": len(self.causal_links),
            "inference_stats": self.inference_engine.get_statistics()
        }
    
    def load_domain_knowledge(self, 
                            domain_name: str,
                            domain_data: Dict[str, Any]) -> None:
        """
        Load knowledge from an existing domain into unified model.
        
        Args:
            domain_name: Name of domain (e.g., "chess", "cooking")
            domain_data: Domain-specific data including rules, entities, context
        """
        # Register domain
        adapter = self.register_domain(domain_name)
        
        # Extract and add entities
        if "context" in domain_data:
            context = domain_data["context"]
            
            # Extract actors
            for actor in adapter.extract_actors(context):
                self.add_entity(actor)
            
            # Extract goals
            for goal in adapter.extract_goals(context):
                self.add_entity(goal)
            
            # Extract constraints
            for constraint in adapter.extract_constraints(context):
                self.add_entity(constraint)
        
        # Load causal rules
        if "rules" in domain_data:
            for rule in domain_data["rules"]:
                causal_link = adapter.adapt_causal_rule(rule)
                self.add_causal_link(causal_link)
