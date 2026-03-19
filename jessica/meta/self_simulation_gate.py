"""
Self-Simulation Safety Gate for Code Changes.

Before executing any code modification (pull request), simulates the impact:
- Will the change break Identity Anchors?
- Will it affect core personality traits?
- Is the change semantically equivalent?
- What's the rollback risk?

Uses Self-Simulation layer to evaluate code changes before execution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
import hashlib


class ChangeRiskLevel(Enum):
    """Risk assessment for code changes."""
    SAFE = "safe"              # <5% risk
    LOW = "low"                # 5-15% risk
    MEDIUM = "medium"          # 15-40% risk
    HIGH = "high"              # 40-75% risk
    DANGEROUS = "dangerous"    # >75% risk


@dataclass
class CodeChangeImpact:
    """Assessment of how a code change affects Jessica."""
    change_description: str
    affected_modules: List[str]
    identity_anchor_compatibility: Dict[str, float]  # Anchor name -> compatibility (0-1)
    personality_trait_impact: Dict[str, float]       # Trait -> delta (-1 to 1)
    risk_level: ChangeRiskLevel
    estimated_behavior_change: float  # How much output distribution changes (0-1)
    backwards_compatibility: bool
    rollback_difficulty: float  # 0=easy, 1=hard
    severity_score: float      # Combined risk metric (0-1)
    reasoning: str
    safety_verdict: bool       # True = safe to execute


class SelfSimulationGate:
    """
    Safety gate using Self-Simulation to predict code change impacts.
    
    Core principle: Before modifying Jessica's own code, simulate what happens.
    """
    
    def __init__(self):
        # Identity Anchors that must be preserved (from identity_anchors.py)
        self.critical_anchors = {
            'CORE_PURPOSE': 0.95,        # Highest priority
            'HONEST_COMM': 0.95,
            'CONTINUOUS_LEARNING': 0.90,
            'PRIVACY_FIRST': 0.95,
            'RESPECT_AUTONOMY': 0.85,
            'HELP_WITHOUT_HARM': 0.90,
            'CURIOSITY': 0.80,
            'HUMILITY': 0.80,
            'GROWTH_MINDSET': 0.85,
        }
        
        # Core personality traits
        self.personality_traits = {
            'supportive': 'positive',       # Should stay positive
            'thoughtful': 'positive',
            'adaptive': 'positive',
            'curious': 'positive',
            'honest': 'positive',
            'confident': 'neutral',         # Should stay balanced
            'cautious': 'neutral',
            'professional': 'neutral',
            'focused': 'neutral',
            'playful': 'positive',
        }
        
        # Critical modules that must not be modified lightly
        self.critical_modules = {
            'agent_loop.py': 0.9,           # Core response loop
            'memory/episodic_memory.py': 0.9,  # Critical for continuity
            'memory/semantic_memory.py': 0.85,
            'meta/identity_anchors.py': 0.95,  # NEVER modify lightly
            'meta/self_simulation.py': 0.95,   # Safety-critical
            'meta/confidence_gate.py': 0.9,
            'lmm/model_orchestrator.py': 0.85,
        }
    
    def assess_change(self, pull_request) -> CodeChangeImpact:
        """
        Assess the impact of a proposed code change using self-simulation.
        
        Returns: Impact assessment with safety verdict
        """
        
        # 1. Identify affected modules
        affected = set()
        for change in pull_request.changes:
            module = change.file_path.split('/')[-1]
            affected.add(module)
        affected = list(affected)
        
        # 2. Check for critical module modifications
        module_risk = self._assess_module_risk(affected)
        
        # 3. Simulate personality impact
        personality_impact = self._simulate_personality_impact(pull_request)
        
        # 4. Simulate identity anchor compatibility
        anchor_impact = self._simulate_anchor_compatibility(pull_request)
        
        # 5. Calculate behavior divergence
        behavior_change = self._estimate_behavior_change(
            pull_request,
            module_risk,
            anchor_impact
        )
        
        # 6. Assess rollback difficulty
        rollback_difficulty = self._assess_rollback_difficulty(
            pull_request,
            affected
        )
        
        # 7. Determine overall risk level
        severity_score = self._calculate_severity_score(
            module_risk,
            behavior_change,
            rollback_difficulty,
            anchor_impact
        )
        
        risk_level = self._severity_to_risk_level(severity_score)
        
        # 8. Make safety decision
        safety_verdict = (
            risk_level not in [ChangeRiskLevel.HIGH, ChangeRiskLevel.DANGEROUS] and
            behavior_change < 0.3 and
            min(anchor_impact.values()) > 0.6
        )
        
        return CodeChangeImpact(
            change_description=pull_request.title,
            affected_modules=affected,
            identity_anchor_compatibility=anchor_impact,
            personality_trait_impact=personality_impact,
            risk_level=risk_level,
            estimated_behavior_change=behavior_change,
            backwards_compatibility=all(
                c.backwards_compatible for c in pull_request.changes
            ),
            rollback_difficulty=rollback_difficulty,
            severity_score=severity_score,
            reasoning=self._generate_reasoning(
                module_risk,
                behavior_change,
                anchor_impact,
                risk_level
            ),
            safety_verdict=safety_verdict,
        )
    
    def _assess_module_risk(self, modules: List[str]) -> float:
        """Calculate risk based on which modules are being modified."""
        if not modules:
            return 0.1  # Changing non-code is low risk
        
        risks = []
        for module in modules:
            risk = self.critical_modules.get(module, 0.3)
            risks.append(risk)
        
        return sum(risks) / len(risks)
    
    def _simulate_personality_impact(self, pull_request) -> Dict[str, float]:
        """Simulate how code changes affect personality traits."""
        impact = {}
        
        for trait, expected_direction in self.personality_traits.items():
            # Default: no impact
            delta = 0.0
            
            # Check if changes mention this trait
            description_lower = pull_request.title.lower()
            
            if trait == 'confident' and 'confidence' in description_lower:
                delta = 0.1  # Confidence improvements make her more confident
            
            if trait == 'thoughtful' and 'think' in description_lower:
                delta = 0.05
            
            if trait == 'curious' and 'search' in description_lower or 'learn' in description_lower:
                delta = 0.1
            
            impact[trait] = delta
        
        return impact
    
    def _simulate_anchor_compatibility(self, pull_request) -> Dict[str, float]:
        """Simulate how code changes maintain identity anchor compatibility."""
        compatibility = {}
        
        for anchor, importance in self.critical_anchors.items():
            # Start with high compatibility assumption
            compat = 0.95
            
            # Check for potential violations
            for change in pull_request.changes:
                # If change modifies identity_anchors.py itself, be very careful
                if 'identity_anchors' in change.file_path:
                    compat *= 0.5  # Risky!
                
                # If change is performance-only, likely safe
                if 'vectorization' in change.improvement_type.value or \
                   'caching' in change.improvement_type.value or \
                   'parallelization' in change.improvement_type.value:
                    compat *= 0.99  # Minimal semantic change
            
            compatibility[anchor] = compat
        
        return compatibility
    
    def _estimate_behavior_change(self, pull_request, module_risk: float,
                                 anchor_impact: Dict[str, float]) -> float:
        """Estimate how much output/behavior distribution will change."""
        
        # Base estimate from module risk
        behavior_change = module_risk * 0.2
        
        # Reduce if all anchors maintained
        min_anchor_compat = min(anchor_impact.values())
        behavior_change *= (1.0 - min_anchor_compat)
        
        # Performance optimizations typically don't change behavior
        for change in pull_request.changes:
            if 'performance' in change.explanation.lower() or \
               'optimization' in change.explanation.lower():
                behavior_change *= 0.5
        
        return min(1.0, behavior_change)
    
    def _assess_rollback_difficulty(self, pull_request, modules: List[str]) -> float:
        """Assess how hard it would be to rollback if something breaks."""
        
        # Base: performance optimizations are easy to rollback
        difficulty = 0.2
        
        # Algorithm changes are harder
        for change in pull_request.changes:
            if change.improvement_type.value == 'algorithm':
                difficulty = 0.6
            elif change.improvement_type.value in ['indexing', 'parallelization']:
                difficulty = 0.4
        
        # Changes to core modules are harder to rollback
        for module in modules:
            if module in self.critical_modules:
                risk = self.critical_modules[module]
                difficulty += risk * 0.1
        
        return min(1.0, difficulty)
    
    def _calculate_severity_score(self, module_risk: float, 
                                 behavior_change: float,
                                 rollback_difficulty: float,
                                 anchor_compatibility: Dict[str, float]) -> float:
        """Calculate overall severity score (0=safe, 1=dangerous)."""
        
        # Weighted combination
        min_anchor = min(anchor_compatibility.values())
        
        severity = (
            module_risk * 0.3 +
            behavior_change * 0.3 +
            rollback_difficulty * 0.2 +
            (1.0 - min_anchor) * 0.2  # Lower min anchor = higher severity
        )
        
        return min(1.0, severity)
    
    def _severity_to_risk_level(self, severity: float) -> ChangeRiskLevel:
        """Convert severity score to risk level."""
        if severity < 0.05:
            return ChangeRiskLevel.SAFE
        elif severity < 0.15:
            return ChangeRiskLevel.LOW
        elif severity < 0.40:
            return ChangeRiskLevel.MEDIUM
        elif severity < 0.75:
            return ChangeRiskLevel.HIGH
        else:
            return ChangeRiskLevel.DANGEROUS
    
    def _generate_reasoning(self, module_risk: float, behavior_change: float,
                           anchor_impact: Dict[str, float],
                           risk_level: ChangeRiskLevel) -> str:
        """Generate human-readable reasoning for the decision."""
        
        parts = []
        
        parts.append(f"Risk Level: {risk_level.value.upper()}")
        parts.append(f"Module Risk: {module_risk:.1%}")
        parts.append(f"Behavior Change: {behavior_change:.1%}")
        
        # Check anchor compatibility
        anchors_at_risk = [
            name for name, compat in anchor_impact.items() 
            if compat < 0.8
        ]
        
        if anchors_at_risk:
            parts.append(f"At-risk anchors: {', '.join(anchors_at_risk)}")
        else:
            parts.append("✅ All identity anchors protected")
        
        return "\n".join(parts)


def gate_code_change(pull_request, verbose: bool = True) -> Tuple[bool, CodeChangeImpact]:
    """
    Safety gate for code changes.
    
    Returns: (approved: bool, impact_assessment: CodeChangeImpact)
    """
    gate = SelfSimulationGate()
    impact = gate.assess_change(pull_request)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Self-Simulation Safety Gate Assessment")
        print(f"{'='*60}")
        print(f"Change: {impact.change_description}")
        print(f"Risk Level: {impact.risk_level.value}")
        print(f"Safety Verdict: {'✅ APPROVED' if impact.safety_verdict else '❌ REJECTED'}")
        print(f"\nReasoning:")
        print(impact.reasoning)
        print(f"{'='*60}\n")
    
    return impact.safety_verdict, impact
