"""
Domain-agnostic mapper: converts domain-specific knowledge into operator inputs.

This layer translates:
  - Chess skill data → Component list for DETECT_BOTTLENECK
  - Coding skill data → Component list for DETECT_BOTTLENECK
  
The operator itself never sees domain vocabulary.
"""

from typing import List, Dict, Any
from jessica.unified_world_model.causal_operator import Component


class DomainMapper:
    """Converts domain-specific problem into domain-agnostic operator input."""
    
    @staticmethod
    def chess_skill_to_components(skill_assessment: Dict[str, float]) -> List[Component]:
        """
        Convert chess skill breakdown into component list.
        
        Args:
            skill_assessment: Dict with keys like "opening", "midgame", etc.
                             Values are 0-1 performance scores
        
        Returns:
            List of Component objects for DETECT_BOTTLENECK operator
        
        Example:
            input = {"opening": 0.7, "midgame": 0.6, "endgame": 0.8, "tactics": 0.4}
            output = [
                Component(name="opening", throughput=0.7),
                Component(name="midgame", throughput=0.6),
                Component(name="endgame", throughput=0.8),
                Component(name="tactics", throughput=0.4),
            ]
        """
        return [
            Component(name=skill, throughput=score, effect_on_total=1.0)
            for skill, score in skill_assessment.items()
        ]
    
    @staticmethod
    def coding_skill_to_components(skill_assessment: Dict[str, float]) -> List[Component]:
        """
        Convert coding skill breakdown into component list.
        
        Args:
            skill_assessment: Dict with keys like "syntax", "debugging", etc.
                             Values are 0-1 performance scores
        
        Returns:
            List of Component objects for DETECT_BOTTLENECK operator
        
        Example:
            input = {"syntax": 0.9, "debugging": 0.7, "design": 0.5, "systems": 0.4}
            output = [
                Component(name="syntax", throughput=0.9),
                Component(name="debugging", throughput=0.7),
                Component(name="design", throughput=0.5),
                Component(name="systems", throughput=0.4),
            ]
        """
        return [
            Component(name=skill, throughput=score, effect_on_total=1.0)
            for skill, score in skill_assessment.items()
        ]
    
    @staticmethod
    def extract_components_from_any_domain(
        domain_data: Dict[str, float]
    ) -> List[Component]:
        """
        Generic mapper: any domain-specific data → operator input.
        
        Precondition: domain_data is a dict with string keys and float (0-1) values.
        No domain knowledge required.
        
        This is the key abstraction: operator doesn't care what "syntax" or "opening" means.
        It only sees numerical scores.
        """
        return [
            Component(name=key, throughput=value, effect_on_total=1.0)
            for key, value in domain_data.items()
            if isinstance(value, (int, float)) and 0 <= value <= 1
        ]
