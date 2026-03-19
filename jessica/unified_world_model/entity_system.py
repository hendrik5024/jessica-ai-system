"""
Entity representation system - canonical types that span all domains.

Provides unified representation for:
- Actors (agents with goals and capabilities)
- Goals (desired states with constraints)
- Constraints (hard/soft boundaries)
- Resources (consumable/renewable)
- States (world conditions)
- Relations (entity connections)
- Causal links (cause→effect patterns)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
import uuid


class EntityType(Enum):
    """Canonical entity types."""
    ACTOR = "actor"
    GOAL = "goal"
    CONSTRAINT = "constraint"
    RESOURCE = "resource"
    STATE = "state"
    RELATION = "relation"
    CAUSAL_LINK = "causal_link"


class ConstraintType(Enum):
    """Types of constraints."""
    HARD = "hard"  # Must not violate
    SOFT = "soft"  # Prefer not to violate
    PREFERENCE = "preference"  # Nice to have


class ResourceType(Enum):
    """Types of resources."""
    CONSUMABLE = "consumable"  # Depletes when used
    RENEWABLE = "renewable"  # Regenerates over time
    FIXED = "fixed"  # Constant capacity


@dataclass
class Entity:
    """Base entity with properties common across all types."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType = EntityType.STATE
    name: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    domain: Optional[str] = None  # Which domain this entity originates from
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get property value with default."""
        return self.properties.get(key, default)
    
    def set_property(self, key: str, value: Any) -> None:
        """Set property value."""
        self.properties[key] = value
    
    def has_tag(self, tag: str) -> bool:
        """Check if entity has a specific tag."""
        return tag in self.tags
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the entity."""
        self.tags.add(tag)


@dataclass
class Actor(Entity):
    """
    Actors are agents with goals, capabilities, and resource constraints.
    
    Examples:
    - Human user (goals: solve problem; capabilities: reasoning; resources: time, attention)
    - Chess player (goals: win game; capabilities: tactics; resources: time, mental energy)
    - Chef (goals: prepare meal; capabilities: cooking skills; resources: ingredients, time)
    """
    
    entity_type: EntityType = field(default=EntityType.ACTOR, init=False)
    goals: List[str] = field(default_factory=list)  # Goal IDs
    capabilities: Set[str] = field(default_factory=set)  # What this actor can do
    resources: Dict[str, float] = field(default_factory=dict)  # Resource_id -> current_level
    constraints: List[str] = field(default_factory=list)  # Constraint IDs
    
    def has_capability(self, capability: str) -> bool:
        """Check if actor has a specific capability."""
        return capability in self.capabilities
    
    def get_resource_level(self, resource: str) -> float:
        """Get current level of a resource."""
        return self.resources.get(resource, 0.0)
    
    def consume_resource(self, resource: str, amount: float) -> bool:
        """
        Consume a resource. Returns True if successful, False if insufficient.
        """
        current = self.get_resource_level(resource)
        if current >= amount:
            self.resources[resource] = current - amount
            return True
        return False


@dataclass
class Goal(Entity):
    """
    Goals are desired states with success criteria and constraints.
    
    Examples:
    - Win chess game (success: checkmate; constraints: legal moves, time limit)
    - Prepare dinner (success: 3 courses ready; constraints: 90 minutes, $50 budget)
    - Learn programming (success: build working app; constraints: 3 months)
    """
    
    entity_type: EntityType = field(default=EntityType.GOAL, init=False)
    success_criteria: List[str] = field(default_factory=list)  # Conditions for success
    constraints: List[str] = field(default_factory=list)  # Constraint IDs
    priority: float = 1.0  # Higher = more important
    deadline: Optional[float] = None  # Time by which goal must be achieved
    parent_goal: Optional[str] = None  # Parent goal ID if this is a sub-goal
    sub_goals: List[str] = field(default_factory=list)  # Sub-goal IDs
    
    def is_sub_goal(self) -> bool:
        """Check if this is a sub-goal."""
        return self.parent_goal is not None


@dataclass
class Constraint(Entity):
    """
    Constraints are boundaries that must (hard) or should (soft) be respected.
    
    Examples:
    - Hard: Cannot violate safety principles
    - Soft: Prefer responses under 200 words
    - Preference: User prefers concise communication style
    """
    
    entity_type: EntityType = field(default=EntityType.CONSTRAINT, init=False)
    constraint_type: ConstraintType = ConstraintType.HARD
    condition: str = ""  # Description of the constraint
    penalty: float = 0.0  # Cost of violating (for soft constraints)
    
    def is_hard(self) -> bool:
        """Check if this is a hard constraint."""
        return self.constraint_type == ConstraintType.HARD
    
    def is_soft(self) -> bool:
        """Check if this is a soft constraint."""
        return self.constraint_type == ConstraintType.SOFT


@dataclass
class Resource(Entity):
    """
    Resources are consumable or renewable assets with capacity limits.
    
    Examples:
    - Time (consumable, fixed total)
    - Energy (renewable, regenerates with rest)
    - Attention (renewable, limited capacity)
    - Money (consumable, can be replenished)
    """
    
    entity_type: EntityType = field(default=EntityType.RESOURCE, init=False)
    resource_type: ResourceType = ResourceType.CONSUMABLE
    current_level: float = 0.0
    max_capacity: float = 100.0
    regeneration_rate: float = 0.0  # Amount regenerated per time unit
    
    def is_depleted(self) -> bool:
        """Check if resource is depleted."""
        return self.current_level <= 0.0
    
    def is_full(self) -> bool:
        """Check if resource is at max capacity."""
        return self.current_level >= self.max_capacity
    
    def consume(self, amount: float) -> bool:
        """Consume resource. Returns True if successful."""
        if self.current_level >= amount:
            self.current_level -= amount
            return True
        return False
    
    def regenerate(self, time_units: float) -> None:
        """Regenerate resource over time."""
        if self.resource_type == ResourceType.RENEWABLE:
            self.current_level = min(
                self.max_capacity,
                self.current_level + (self.regeneration_rate * time_units)
            )


@dataclass
class State(Entity):
    """
    States represent world conditions or entity status.
    
    Examples:
    - Chess board position (piece locations, turn)
    - Recipe progress (ingredients prepared, cooking stage)
    - User emotional state (frustrated, confident, confused)
    """
    
    entity_type: EntityType = field(default=EntityType.STATE, init=False)
    variables: Dict[str, Any] = field(default_factory=dict)  # State variables
    timestamp: Optional[float] = None  # When this state was observed
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get state variable value."""
        return self.variables.get(name, default)
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set state variable value."""
        self.variables[name] = value


@dataclass
class Relation(Entity):
    """
    Relations connect entities with typed relationships.
    
    Examples:
    - Actor "owns" Resource
    - Goal "requires" Resource
    - Actor "pursues" Goal
    - State "satisfies" Goal
    """
    
    entity_type: EntityType = field(default=EntityType.RELATION, init=False)
    source_id: str = ""  # Source entity ID
    target_id: str = ""  # Target entity ID
    relation_type: str = ""  # Type of relation (e.g., "owns", "requires", "causes")
    strength: float = 1.0  # Strength of relation (0.0 to 1.0)
    
    def get_endpoints(self) -> Tuple[str, str]:
        """Get source and target IDs."""
        return (self.source_id, self.target_id)


@dataclass
class CausalLink(Entity):
    """
    Causal links represent cause→effect patterns.
    
    Examples:
    - Pressure increases → mistakes increase (chess, cooking, decisions)
    - Rest increases → energy regenerates (all domains)
    - Practice increases → skill increases (learning domains)
    """
    
    entity_type: EntityType = field(default=EntityType.CAUSAL_LINK, init=False)
    cause_conditions: List[str] = field(default_factory=list)  # Conditions that trigger effect
    effect_outcomes: List[str] = field(default_factory=list)  # Resulting outcomes
    confidence: float = 1.0  # Confidence in this causal link (0.0 to 1.0)
    delay: float = 0.0  # Time delay between cause and effect
    domain_agnostic: bool = False  # True if this applies across domains
    
    def is_applicable(self, current_conditions: Set[str]) -> bool:
        """Check if cause conditions are met."""
        required = set(self.cause_conditions)
        return required.issubset(current_conditions)
    
    def predict_effect(self) -> List[str]:
        """Predict outcomes if this causal link fires."""
        return self.effect_outcomes.copy()
