"""
Causal World Models - Understanding Cause → Effect

Instead of just knowing facts, Jessica understands causal relationships
and can simulate outcomes before advising.

Lightweight models for domains:
- Productivity (sleep, interruptions, focus, mistakes)
- Emotions (stress, rest, social, mood)
- Learning (practice, review, sleep, understanding)
- Habits (triggers, behavior, reward, reinforcement)
- Systems (inputs, processes, outputs, feedback loops)

Model structure:
Variables → (connected by causal edges)
     ↓
Simulation → (what happens if X changes?)
     ↓
Predictions → (outcomes for decision-making)
"""

import json
import os
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class CausalVariable:
    """Represents a variable in a causal system."""
    name: str
    domain: str          # Domain this belongs to
    description: str
    range_min: float = 0.0
    range_max: float = 10.0
    unit: str = "score"
    value: float = 5.0   # Current value
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@dataclass
class CausalEdge:
    """Represents a cause→effect relationship."""
    source: str          # Variable causing change
    target: str          # Variable being affected
    strength: float      # Magnitude of effect (-1.0 to 1.0)
    delay: int = 0       # Time steps before effect appears
    nonlinear: bool = False  # Non-linear relationship?
    description: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class CausalDomain:
    """
    A domain with variables and causal relationships.
    
    Examples:
    - Productivity: sleep, focus, interruptions, mistakes, tasks_completed
    - Emotions: stress, rest, social_connection, mood, energy
    - Learning: study_time, review_frequency, sleep, understanding, retention
    - Habits: trigger, behavior, reward, repetitions, strength
    - Systems: input_quality, process_efficiency, output_quality, feedback
    """
    
    def __init__(self, domain: str, description: str = ""):
        self.domain = domain
        self.description = description
        self.variables: Dict[str, CausalVariable] = {}
        self.edges: List[CausalEdge] = []
        self.feedback_loops: List[List[str]] = []  # Detected cycles
    
    def add_variable(self, var: CausalVariable):
        """Add a variable to the domain."""
        var.domain = self.domain
        self.variables[var.name] = var
    
    def add_edge(self, source: str, target: str, strength: float, 
                 description: str = "", delay: int = 0, nonlinear: bool = False):
        """Add a causal relationship."""
        if source not in self.variables or target not in self.variables:
            raise ValueError(f"Variable not in domain: {source} or {target}")
        
        self.edges.append(CausalEdge(
            source=source,
            target=target,
            strength=strength,
            delay=delay,
            description=description,
            nonlinear=nonlinear
        ))
    
    def detect_feedback_loops(self) -> List[List[str]]:
        """Identify feedback loops in the causal model."""
        loops = []
        
        # Simple cycle detection using DFS
        def find_cycles(node, path, visited):
            if node in visited and node in path:
                cycle = path[path.index(node):]
                if cycle not in loops and cycle[::-1] not in loops:
                    loops.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            # Follow edges from this node
            for edge in self.edges:
                if edge.source == node:
                    find_cycles(edge.target, path.copy(), visited.copy())
        
        for var_name in self.variables:
            find_cycles(var_name, [], set())
        
        self.feedback_loops = loops
        return loops
    
    def simulate_intervention(self, intervention: Dict[str, float], 
                            steps: int = 3) -> Dict[str, List[float]]:
        """
        Simulate what happens when we intervene (change variables).
        
        Args:
            intervention: {"variable_name": new_value}
            steps: How many time steps to simulate
            
        Returns:
            {"variable": [value_t0, value_t1, ..., value_tn]}
        """
        # Initialize state
        state = {var_name: var.value for var_name, var in self.variables.items()}
        
        # Apply intervention
        for var_name, value in intervention.items():
            if var_name in state:
                state[var_name] = max(
                    self.variables[var_name].range_min,
                    min(self.variables[var_name].range_max, value)
                )
        
        # Track trajectory
        trajectory = {var_name: [state[var_name]] for var_name in state}
        
        # Simulate forward
        for step in range(steps):
            new_state = state.copy()
            
            for edge in self.edges:
                # Check if this edge should activate at this step
                if edge.delay > step:
                    continue
                
                source_val = state[edge.source]
                target_var = self.variables[edge.target]
                
                # Apply causal effect
                if edge.nonlinear:
                    # Nonlinear: acceleration at extremes
                    normalized = (source_val - target_var.range_min) / (target_var.range_max - target_var.range_min)
                    effect = edge.strength * normalized * (source_val - target_var.range_min)
                else:
                    # Linear effect
                    effect = edge.strength * (source_val - target_var.value)
                
                # Apply with damping (systems return toward equilibrium)
                new_state[edge.target] += effect * 0.3
                
                # Clamp to valid range
                new_state[edge.target] = max(
                    target_var.range_min,
                    min(target_var.range_max, new_state[edge.target])
                )
            
            state = new_state
            for var_name in state:
                trajectory[var_name].append(state[var_name])
        
        return trajectory
    
    def to_dict(self):
        return {
            "domain": self.domain,
            "description": self.description,
            "variables": {k: v.to_dict() for k, v in self.variables.items()},
            "edges": [e.to_dict() for e in self.edges],
            "feedback_loops": self.feedback_loops
        }
    
    @classmethod
    def from_dict(cls, d):
        domain_obj = cls(d["domain"], d.get("description", ""))
        
        for var_data in d.get("variables", {}).values():
            domain_obj.variables[var_data["name"]] = CausalVariable.from_dict(var_data)
        
        for edge_data in d.get("edges", []):
            edge = CausalEdge.from_dict(edge_data)
            domain_obj.edges.append(edge)
        
        domain_obj.feedback_loops = d.get("feedback_loops", [])
        return domain_obj


class CausalWorldModels:
    """
    Manager for multiple causal domain models.
    Enables planning and outcome prediction across different life domains.
    """
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or "jessica_data_embeddings/causal_models_state.json"
        self.domains: Dict[str, CausalDomain] = {}
        self._load_or_create()
    
    def _load_or_create(self):
        """Load models from disk or create defaults."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for domain_data in data.get("domains", []):
                        domain = CausalDomain.from_dict(domain_data)
                        self.domains[domain.domain] = domain
                return
            except Exception as e:
                print(f"[CausalModels] Load error: {e}, creating defaults")
        
        self._create_defaults()
    
    def _create_defaults(self):
        """Create default causal models for key domains."""
        
        # ==================== PRODUCTIVITY DOMAIN ====================
        prod = CausalDomain(
            "productivity",
            "How sleep, interruptions, and environment affect work output"
        )
        
        prod.add_variable(CausalVariable("sleep_hours", "productivity", 
            "Hours of sleep (affects focus)", 0, 12, "hours", 7.0))
        prod.add_variable(CausalVariable("focus_level", "productivity",
            "Mental focus ability (0-10)", 0, 10, "score", 7.0))
        prod.add_variable(CausalVariable("interruptions", "productivity",
            "Number of interruptions per hour", 0, 10, "count", 2.0))
        prod.add_variable(CausalVariable("task_completion", "productivity",
            "Tasks completed per hour", 0, 10, "count", 6.0))
        prod.add_variable(CausalVariable("error_rate", "productivity",
            "Mistakes per task (lower is better)", 0, 10, "percentage", 3.0))
        prod.add_variable(CausalVariable("env_quality", "productivity",
            "Environment quality (0-10)", 0, 10, "score", 6.0))
        
        # Causal relationships
        prod.add_edge("sleep_hours", "focus_level", 0.8,
            "More sleep → better focus")
        prod.add_edge("focus_level", "task_completion", 0.7,
            "Better focus → more tasks done")
        prod.add_edge("interruptions", "focus_level", -0.6,
            "More interruptions → broken focus")
        prod.add_edge("focus_level", "error_rate", -0.5,
            "Better focus → fewer errors")
        prod.add_edge("env_quality", "focus_level", 0.4,
            "Better environment → better focus")
        prod.add_edge("error_rate", "task_completion", -0.3,
            "More errors → redoing work")
        
        # Feedback loops
        prod.add_edge("task_completion", "focus_level", 0.2,
            "Success builds momentum (positive feedback)")
        prod.add_edge("error_rate", "focus_level", -0.15,
            "Frustration reduces focus (negative feedback)")
        
        self.domains["productivity"] = prod
        
        # ==================== EMOTIONS DOMAIN ====================
        emot = CausalDomain(
            "emotions",
            "How rest, stress, and social connection affect mood"
        )
        
        emot.add_variable(CausalVariable("stress_level", "emotions",
            "Current stress (0-10)", 0, 10, "score", 4.0))
        emot.add_variable(CausalVariable("rest_quality", "emotions",
            "Quality of rest/sleep (0-10)", 0, 10, "score", 6.0))
        emot.add_variable(CausalVariable("social_connection", "emotions",
            "Social support/connection (0-10)", 0, 10, "score", 7.0))
        emot.add_variable(CausalVariable("mood", "emotions",
            "Overall mood state (0-10)", 0, 10, "score", 6.5))
        emot.add_variable(CausalVariable("energy", "emotions",
            "Energy level (0-10)", 0, 10, "score", 6.0))
        emot.add_variable(CausalVariable("resilience", "emotions",
            "Ability to bounce back (0-10)", 0, 10, "score", 6.0))
        
        # Causal relationships
        emot.add_edge("rest_quality", "mood", 0.7,
            "Better rest → better mood")
        emot.add_edge("rest_quality", "energy", 0.8,
            "Better rest → more energy")
        emot.add_edge("stress_level", "mood", -0.6,
            "Higher stress → worse mood")
        emot.add_edge("stress_level", "energy", -0.5,
            "Higher stress → less energy")
        emot.add_edge("social_connection", "mood", 0.5,
            "Social connection → better mood")
        emot.add_edge("social_connection", "resilience", 0.6,
            "Social support → better resilience")
        emot.add_edge("energy", "resilience", 0.4,
            "Higher energy → more resilience")
        
        # Feedback loops
        emot.add_edge("mood", "stress_level", -0.3,
            "Better mood → lower stress (positive feedback)")
        emot.add_edge("resilience", "stress_level", -0.25,
            "Better resilience → stress affects less (positive feedback)")
        
        self.domains["emotions"] = emot
        
        # ==================== LEARNING DOMAIN ====================
        learn = CausalDomain(
            "learning",
            "How study practice, review, and sleep affect learning"
        )
        
        learn.add_variable(CausalVariable("study_time", "learning",
            "Hours spent studying (0-10)", 0, 10, "hours", 2.0))
        learn.add_variable(CausalVariable("review_frequency", "learning",
            "Times material reviewed (0-10)", 0, 10, "count", 2.0))
        learn.add_variable(CausalVariable("sleep_hours", "learning",
            "Hours of sleep", 0, 12, "hours", 7.0))
        learn.add_variable(CausalVariable("understanding", "learning",
            "Conceptual understanding (0-10)", 0, 10, "score", 5.0))
        learn.add_variable(CausalVariable("retention", "learning",
            "Memory retention (0-10)", 0, 10, "score", 5.0))
        learn.add_variable(CausalVariable("test_score", "learning",
            "Test performance (0-100)", 0, 100, "percentage", 65.0))
        
        # Causal relationships
        learn.add_edge("study_time", "understanding", 0.7,
            "More study → better understanding")
        learn.add_edge("review_frequency", "retention", 0.8,
            "More review → better retention (spaced repetition)")
        learn.add_edge("sleep_hours", "retention", 0.7,
            "Sleep consolidates memories")
        learn.add_edge("understanding", "test_score", 0.8,
            "Understanding → better test performance")
        learn.add_edge("retention", "test_score", 0.7,
            "Good memory → better test performance")
        learn.add_edge("study_time", "retention", 0.3,
            "Study time (direct memory effect)")
        
        # Feedback loops
        learn.add_edge("test_score", "study_time", 0.2,
            "Good scores → motivation → more study (positive feedback)")
        
        self.domains["learning"] = learn
        
        # ==================== HABITS DOMAIN ====================
        habits = CausalDomain(
            "habits",
            "How triggers, behavior, and rewards form/strengthen habits"
        )
        
        habits.add_variable(CausalVariable("trigger_frequency", "habits",
            "How often the trigger occurs (0-10)", 0, 10, "score", 5.0))
        habits.add_variable(CausalVariable("behavior_repetitions", "habits",
            "Times behavior repeated (0-10)", 0, 10, "count", 3.0))
        habits.add_variable(CausalVariable("reward_strength", "habits",
            "How rewarding the behavior is (0-10)", 0, 10, "score", 6.0))
        habits.add_variable(CausalVariable("habit_strength", "habits",
            "How automatic/strong the habit is (0-10)", 0, 10, "score", 4.0))
        habits.add_variable(CausalVariable("resistance", "habits",
            "Willpower needed to do behavior (0-10)", 0, 10, "score", 7.0))
        
        # Causal relationships
        habits.add_edge("trigger_frequency", "behavior_repetitions", 0.8,
            "More triggers → more repetitions")
        habits.add_edge("behavior_repetitions", "habit_strength", 0.7,
            "Repetition → habit becomes automatic")
        habits.add_edge("reward_strength", "habit_strength", 0.6,
            "Strong rewards reinforce habit")
        habits.add_edge("habit_strength", "resistance", -0.8,
            "Stronger habit → less willpower needed")
        
        # Feedback loop
        habits.add_edge("habit_strength", "trigger_frequency", 0.3,
            "Strong habits make you seek triggers (positive feedback)")
        habits.add_edge("reward_strength", "behavior_repetitions", 0.5,
            "Rewards encourage more repetitions")
        
        self.domains["habits"] = habits
        
        # ==================== SYSTEMS DOMAIN ====================
        systems = CausalDomain(
            "systems",
            "General systems thinking: inputs, processes, outputs, feedback"
        )
        
        systems.add_variable(CausalVariable("input_quality", "systems",
            "Quality of inputs (0-10)", 0, 10, "score", 6.0))
        systems.add_variable(CausalVariable("input_quantity", "systems",
            "Quantity of inputs (0-10)", 0, 10, "score", 5.0))
        systems.add_variable(CausalVariable("process_efficiency", "systems",
            "How efficiently system works (0-10)", 0, 10, "score", 6.0))
        systems.add_variable(CausalVariable("output_quality", "systems",
            "Quality of outputs (0-10)", 0, 10, "score", 5.0))
        systems.add_variable(CausalVariable("output_quantity", "systems",
            "Quantity of outputs (0-10)", 0, 10, "score", 5.0))
        systems.add_variable(CausalVariable("feedback_loop_strength", "systems",
            "How strong feedback is (0-10)", 0, 10, "score", 4.0))
        
        # Causal relationships
        systems.add_edge("input_quality", "output_quality", 0.7,
            "Good inputs → good outputs")
        systems.add_edge("input_quantity", "output_quantity", 0.8,
            "More input → more output (if capacity)")
        systems.add_edge("process_efficiency", "output_quality", 0.6,
            "Better process → better quality")
        systems.add_edge("output_quality", "feedback_loop_strength", 0.4,
            "Good outputs → positive feedback")
        
        # Feedback loops
        systems.add_edge("output_quality", "process_efficiency", 0.3,
            "Success informs optimization")
        systems.add_edge("feedback_loop_strength", "process_efficiency", 0.4,
            "Strong feedback → continuous improvement")
        
        self.domains["systems"] = systems
        
        self.save()
    
    def save(self):
        """Persist models to disk."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "saved_at": datetime.now().isoformat(),
            "domains": [domain.to_dict() for domain in self.domains.values()]
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def predict_outcome(self, domain: str, intervention: Dict[str, float],
                       steps: int = 3) -> Dict[str, Any]:
        """
        Predict outcomes of an intervention in a domain.
        
        Returns:
        {
            "domain": str,
            "intervention": dict,
            "trajectory": dict,
            "summary": str,
            "key_findings": [...]
        }
        """
        if domain not in self.domains:
            return {"error": f"Domain not found: {domain}"}
        
        domain_obj = self.domains[domain]
        trajectory = domain_obj.simulate_intervention(intervention, steps)
        
        # Generate summary
        findings = []
        for var_name, values in trajectory.items():
            initial = values[0]
            final = values[-1]
            change = final - initial
            
            if abs(change) > 0.5:
                direction = "increases" if change > 0 else "decreases"
                findings.append(f"{var_name.replace('_', ' ')}: {direction} "
                              f"by {abs(change):.1f} points")
        
        return {
            "domain": domain,
            "intervention": intervention,
            "trajectory": trajectory,
            "summary": f"Over {steps} steps: " + "; ".join(findings),
            "key_findings": findings,
            "confidence": 0.7  # Causal models are uncertain
        }
    
    def plan_intervention(self, domain: str, goal: Dict[str, float]) -> Dict[str, Any]:
        """
        Plan an intervention to achieve a goal.
        Finds which variables to change to reach desired outcome.
        """
        if domain not in self.domains:
            return {"error": f"Domain not found: {domain}"}
        
        domain_obj = self.domains[domain]
        
        # Try different interventions, pick the one that gets closest to goal
        best_intervention = None
        best_score = float('inf')
        
        # Generate candidate interventions
        candidates = self._generate_candidates(domain_obj, goal)
        
        for intervention in candidates:
            trajectory = domain_obj.simulate_intervention(intervention, steps=3)
            
            # Score how close we get to goal
            score = 0
            for var, target in goal.items():
                if var in trajectory:
                    final_value = trajectory[var][-1]
                    score += abs(final_value - target) ** 2
            
            if score < best_score:
                best_score = score
                best_intervention = intervention
        
        if best_intervention is None:
            return {"error": "Could not find feasible intervention"}
        
        result = self.predict_outcome(domain, best_intervention, steps=3)
        result["plan"] = best_intervention
        result["optimality_score"] = 1 - min(1.0, best_score / 100)
        
        return result
    
    def _generate_candidates(self, domain: CausalDomain, 
                           goal: Dict[str, float]) -> List[Dict[str, float]]:
        """Generate candidate interventions."""
        candidates = []
        
        # Candidate 1: Change each variable directly
        for var_name, target_value in goal.items():
            if var_name in domain.variables:
                candidates.append({var_name: target_value})
        
        # Candidate 2: Change multiple variables
        for var1_name, target1 in goal.items():
            for var2_name, target2 in goal.items():
                if var1_name != var2_name:
                    if var1_name in domain.variables and var2_name in domain.variables:
                        candidates.append({
                            var1_name: target1,
                            var2_name: target2
                        })
        
        return candidates[:20]  # Limit to prevent explosion
    
    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze the structure of a domain model."""
        if domain not in self.domains:
            return {"error": f"Domain not found: {domain}"}
        
        domain_obj = self.domains[domain]
        loops = domain_obj.detect_feedback_loops()
        
        return {
            "domain": domain,
            "description": domain_obj.description,
            "variables": list(domain_obj.variables.keys()),
            "variable_count": len(domain_obj.variables),
            "relationship_count": len(domain_obj.edges),
            "feedback_loops": loops,
            "feedback_loop_count": len(loops),
            "structure_summary": self._describe_structure(domain_obj)
        }
    
    def _describe_structure(self, domain: CausalDomain) -> str:
        """Describe the causal structure of a domain."""
        edges_in = {}
        edges_out = {}
        
        for edge in domain.edges:
            edges_in[edge.target] = edges_in.get(edge.target, 0) + 1
            edges_out[edge.source] = edges_out.get(edge.source, 0) + 1
        
        # Find root causes (no incoming edges)
        roots = [v for v in domain.variables if v not in edges_in]
        
        # Find outcomes (no outgoing edges)
        outcomes = [v for v in domain.variables if v not in edges_out]
        
        return (f"Root causes: {', '.join(roots[:3])} | "
               f"Outcomes: {', '.join(outcomes[:3])} | "
               f"Feedback loops: {len(domain.feedback_loops)}")
    
    def get_domain_summary(self, domain: str) -> str:
        """Get human-readable summary of a domain."""
        if domain not in self.domains:
            return f"Domain '{domain}' not found"
        
        domain_obj = self.domains[domain]
        
        summary = f"## {domain_obj.domain.upper()} Domain\n\n"
        summary += f"{domain_obj.description}\n\n"
        
        summary += "### Variables\n"
        for var_name, var in domain_obj.variables.items():
            summary += f"- **{var_name.replace('_', ' ')}**: {var.description}\n"
            summary += f"  Range: {var.range_min}-{var.range_max} {var.unit} | "
            summary += f"Current: {var.value:.1f}\n"
        
        summary += "\n### Key Relationships\n"
        for edge in domain_obj.edges[:10]:  # Show first 10
            direction = "→" if edge.strength > 0 else "↘"
            summary += f"- {edge.source} {direction} {edge.target}: {edge.description}\n"
        
        if domain_obj.feedback_loops:
            summary += f"\n### Feedback Loops ({len(domain_obj.feedback_loops)})\n"
            for loop in domain_obj.feedback_loops[:3]:
                summary += f"- {' → '.join(loop)} → ...\n"
        
        return summary


def get_causal_models() -> CausalWorldModels:
    """Singleton getter for causal world models."""
    if not hasattr(get_causal_models, "_instance"):
        get_causal_models._instance = CausalWorldModels()
    return get_causal_models._instance
