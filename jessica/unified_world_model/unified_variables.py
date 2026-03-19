"""
Unified variables - canonical representations of time, energy, attention, risk.

These variables provide domain-agnostic representations that enable cross-domain reasoning.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class UnifiedVariable(ABC):
    """
    Base class for unified variables that exist across domains.
    
    Examples of how variables map across domains:
    - Time: chess (move count, clock time), recipes (cooking duration), travel (itinerary pace)
    - Energy: chess (mental stamina), cooking (physical effort), decision-making (cognitive load)
    - Attention: chess (focus depth), recipes (simultaneous tasks), travel (planning complexity)
    - Risk: chess (position evaluation), decisions (outcome uncertainty), travel (safety)
    """
    
    @abstractmethod
    def measure(self, context: Dict[str, Any]) -> float:
        """Measure the variable in the given context."""
        pass
    
    @abstractmethod
    def domain_specific_value(self, domain: str, context: Dict[str, Any]) -> Any:
        """Get domain-specific representation of this variable."""
        pass
    
    @abstractmethod
    def compare_across_domains(self, domain_a: str, value_a: Any, domain_b: str, value_b: Any) -> str:
        """Compare values from different domains."""
        pass


@dataclass
class TimeVariable(UnifiedVariable):
    """
    Unified time representation across domains.
    
    Domain mappings:
    - Chess: move count, clock time remaining
    - Recipes: cooking duration, prep time, total time
    - Travel: days in itinerary, hours per activity
    - Decision-making: time to decide, deadline pressure
    - Professional: project timeline, meeting duration
    """
    
    unit: str = "minutes"  # Base unit for comparison
    
    def measure(self, context: Dict[str, Any]) -> float:
        """
        Measure time in the given context.
        Returns normalized value in base units (minutes).
        """
        domain = context.get("domain", "")
        
        if domain == "chess":
            # Convert chess time (seconds) to minutes
            time_seconds = context.get("time_remaining_seconds", 0)
            return time_seconds / 60.0
        
        elif domain == "cooking":
            # Cooking time already in minutes
            return context.get("cooking_time_minutes", 0)
        
        elif domain == "travel":
            # Travel time in hours, convert to minutes
            time_hours = context.get("activity_duration_hours", 0)
            return time_hours * 60.0
        
        elif domain == "decision_making":
            # Decision deadline in minutes
            return context.get("decision_time_minutes", 0)
        
        else:
            # Default: extract time in minutes
            return context.get("time_minutes", 0)
    
    def domain_specific_value(self, domain: str, context: Dict[str, Any]) -> Any:
        """Get time representation specific to domain."""
        base_minutes = self.measure(context)
        
        if domain == "chess":
            return {"seconds": base_minutes * 60, "moves_available": base_minutes / 2}
        elif domain == "cooking":
            return {"minutes": base_minutes, "stages": base_minutes / 15}
        elif domain == "travel":
            return {"hours": base_minutes / 60, "activities": base_minutes / 120}
        else:
            return {"minutes": base_minutes}
    
    def compare_across_domains(self, domain_a: str, value_a: Any, domain_b: str, value_b: Any) -> str:
        """
        Compare time pressure across domains.
        
        Example: "Chess with 2 minutes remaining is similar pressure to cooking with 15 minutes left for 3-course meal"
        """
        # Normalize to "time pressure" metric (lower = more pressure)
        pressure_a = self._calculate_pressure(domain_a, value_a)
        pressure_b = self._calculate_pressure(domain_b, value_b)
        
        ratio = pressure_a / pressure_b if pressure_b > 0 else 0
        
        if 0.8 <= ratio <= 1.2:
            return f"Similar time pressure in {domain_a} and {domain_b}"
        elif ratio < 0.8:
            return f"Higher time pressure in {domain_a} than {domain_b} ({ratio:.1f}x)"
        else:
            return f"Lower time pressure in {domain_a} than {domain_b} ({ratio:.1f}x)"
    
    def _calculate_pressure(self, domain: str, value: Any) -> float:
        """Calculate normalized time pressure (0 = extreme, 1 = relaxed)."""
        if domain == "chess":
            seconds = value.get("seconds", 0)
            return min(1.0, seconds / 300)  # Normalize: 5 minutes = relaxed
        elif domain == "cooking":
            minutes = value.get("minutes", 0)
            stages = value.get("stages", 1)
            return min(1.0, minutes / (stages * 20))  # 20 min per stage = relaxed
        else:
            minutes = value.get("minutes", 0)
            return min(1.0, minutes / 60)  # 60 minutes = relaxed


@dataclass
class EnergyVariable(UnifiedVariable):
    """
    Unified energy representation across domains.
    
    Domain mappings:
    - Chess: mental stamina, concentration capacity
    - Cooking: physical energy, multitasking capacity
    - Decision-making: cognitive load, willpower
    - Travel: physical endurance, mental alertness
    """
    
    max_capacity: float = 100.0
    
    def measure(self, context: Dict[str, Any]) -> float:
        """
        Measure energy level in context.
        Returns 0.0 (depleted) to 1.0 (full capacity).
        """
        domain = context.get("domain", "")
        
        if domain == "chess":
            moves_played = context.get("moves_played", 0)
            # Mental energy depletes with game length
            return max(0.0, 1.0 - (moves_played / 80.0))
        
        elif domain == "cooking":
            tasks_active = context.get("simultaneous_tasks", 0)
            # Energy depletes with multitasking
            return max(0.0, 1.0 - (tasks_active / 5.0))
        
        elif domain == "decision_making":
            decisions_made = context.get("decisions_made_today", 0)
            # Decision fatigue
            return max(0.0, 1.0 - (decisions_made / 50.0))
        
        else:
            # Default: extract energy level
            return context.get("energy_level", 1.0)
    
    def domain_specific_value(self, domain: str, context: Dict[str, Any]) -> Any:
        """Get energy representation specific to domain."""
        base_energy = self.measure(context)
        
        if domain == "chess":
            return {
                "mental_stamina": base_energy,
                "concentration_quality": "high" if base_energy > 0.7 else "medium" if base_energy > 0.3 else "low"
            }
        elif domain == "cooking":
            return {
                "physical_energy": base_energy,
                "multitasking_capacity": int(base_energy * 5)
            }
        elif domain == "decision_making":
            return {
                "cognitive_load": 1.0 - base_energy,
                "willpower": base_energy
            }
        else:
            return {"energy": base_energy}
    
    def compare_across_domains(self, domain_a: str, value_a: Any, domain_b: str, value_b: Any) -> str:
        """Compare energy levels across domains."""
        energy_a = self._extract_energy(value_a)
        energy_b = self._extract_energy(value_b)
        
        if abs(energy_a - energy_b) < 0.15:
            return f"Similar energy depletion in {domain_a} and {domain_b}"
        elif energy_a < energy_b:
            return f"More depleted in {domain_a} ({energy_a:.1%}) than {domain_b} ({energy_b:.1%})"
        else:
            return f"More depleted in {domain_b} ({energy_b:.1%}) than {domain_a} ({energy_a:.1%})"
    
    def _extract_energy(self, value: Any) -> float:
        """Extract normalized energy from domain-specific value."""
        if isinstance(value, dict):
            return value.get("mental_stamina") or value.get("physical_energy") or value.get("willpower") or value.get("energy", 0.5)
        return 0.5


@dataclass
class AttentionVariable(UnifiedVariable):
    """
    Unified attention representation across domains.
    
    Domain mappings:
    - Chess: focus depth, position evaluation quality
    - Cooking: number of simultaneous tasks tracked
    - Decision-making: factors considered simultaneously
    - Travel: planning complexity, detail tracking
    """
    
    def measure(self, context: Dict[str, Any]) -> float:
        """
        Measure attention capacity usage.
        Returns 0.0 (no load) to 1.0 (maximum capacity).
        """
        domain = context.get("domain", "")
        
        if domain == "chess":
            depth = context.get("calculation_depth", 0)
            # Deep calculation uses more attention
            return min(1.0, depth / 10.0)
        
        elif domain == "cooking":
            simultaneous = context.get("simultaneous_tasks", 0)
            # Multiple tasks split attention
            return min(1.0, simultaneous / 5.0)
        
        elif domain == "decision_making":
            factors = context.get("factors_considered", 0)
            # More factors = more attention
            return min(1.0, factors / 10.0)
        
        else:
            return context.get("attention_load", 0.0)
    
    def domain_specific_value(self, domain: str, context: Dict[str, Any]) -> Any:
        """Get attention representation specific to domain."""
        base_attention = self.measure(context)
        
        if domain == "chess":
            return {
                "focus_depth": base_attention,
                "calculation_depth": int(base_attention * 10)
            }
        elif domain == "cooking":
            return {
                "simultaneous_tasks": int(base_attention * 5),
                "coordination_quality": "high" if base_attention < 0.6 else "medium" if base_attention < 0.8 else "low"
            }
        elif domain == "decision_making":
            return {
                "factors_tracked": int(base_attention * 10),
                "cognitive_clarity": 1.0 - base_attention
            }
        else:
            return {"attention": base_attention}
    
    def compare_across_domains(self, domain_a: str, value_a: Any, domain_b: str, value_b: Any) -> str:
        """Compare attention load across domains."""
        load_a = self._extract_attention(value_a)
        load_b = self._extract_attention(value_b)
        
        if abs(load_a - load_b) < 0.15:
            return f"Similar attention load in {domain_a} and {domain_b}"
        elif load_a > load_b:
            return f"Higher attention load in {domain_a} ({load_a:.1%}) than {domain_b} ({load_b:.1%})"
        else:
            return f"Higher attention load in {domain_b} ({load_b:.1%}) than {domain_a} ({load_a:.1%})"
    
    def _extract_attention(self, value: Any) -> float:
        """Extract normalized attention from domain-specific value."""
        if isinstance(value, dict):
            return value.get("focus_depth") or value.get("attention", 0.5)
        return 0.5


@dataclass
class RiskVariable(UnifiedVariable):
    """
    Unified risk representation across domains.
    
    Domain mappings:
    - Chess: position evaluation (advantage/disadvantage)
    - Decision-making: outcome uncertainty
    - Travel: safety concerns, unpredictability
    - Financial: investment risk, loss potential
    """
    
    def measure(self, context: Dict[str, Any]) -> float:
        """
        Measure risk level.
        Returns 0.0 (safe) to 1.0 (high risk).
        """
        domain = context.get("domain", "")
        
        if domain == "chess":
            eval_centipawns = context.get("position_eval_centipawns", 0)
            # Negative eval = risk for current player
            if eval_centipawns < 0:
                return min(1.0, abs(eval_centipawns) / 300.0)
            return 0.0
        
        elif domain == "decision_making":
            uncertainty = context.get("outcome_uncertainty", 0.0)
            # Uncertainty directly maps to risk
            return min(1.0, uncertainty)
        
        elif domain == "travel":
            safety_rating = context.get("safety_rating", 10)
            # Low safety = high risk
            return max(0.0, (10 - safety_rating) / 10.0)
        
        elif domain == "financial":
            volatility = context.get("volatility", 0.0)
            return min(1.0, volatility)
        
        else:
            return context.get("risk_level", 0.0)
    
    def domain_specific_value(self, domain: str, context: Dict[str, Any]) -> Any:
        """Get risk representation specific to domain."""
        base_risk = self.measure(context)
        
        if domain == "chess":
            return {
                "position_risk": base_risk,
                "evaluation": "losing" if base_risk > 0.6 else "unclear" if base_risk > 0.2 else "safe"
            }
        elif domain == "decision_making":
            return {
                "uncertainty": base_risk,
                "confidence": 1.0 - base_risk
            }
        elif domain == "travel":
            return {
                "safety_concern": base_risk,
                "recommendation": "avoid" if base_risk > 0.7 else "caution" if base_risk > 0.3 else "safe"
            }
        else:
            return {"risk": base_risk}
    
    def compare_across_domains(self, domain_a: str, value_a: Any, domain_b: str, value_b: Any) -> str:
        """Compare risk levels across domains."""
        risk_a = self._extract_risk(value_a)
        risk_b = self._extract_risk(value_b)
        
        if abs(risk_a - risk_b) < 0.15:
            return f"Similar risk level in {domain_a} and {domain_b}"
        elif risk_a > risk_b:
            return f"Higher risk in {domain_a} ({risk_a:.1%}) than {domain_b} ({risk_b:.1%})"
        else:
            return f"Higher risk in {domain_b} ({risk_b:.1%}) than {domain_a} ({risk_a:.1%})"
    
    def _extract_risk(self, value: Any) -> float:
        """Extract normalized risk from domain-specific value."""
        if isinstance(value, dict):
            return value.get("position_risk") or value.get("uncertainty") or value.get("safety_concern") or value.get("risk", 0.5)
        return 0.5
