"""
Multi-Agent Swarm Integration with Model Orchestrator

This module connects the debate framework with Jessica's existing
model orchestration stack, enabling autonomous agent collaboration.

The orchestrator determines:
1. When to use debate (complex problems) vs simple routing (simple tasks)
2. Which agents are available
3. How to integrate results back into Jessica's decision-making
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class ProblemComplexityClassifier:
    """Determines if a problem requires multi-agent debate or simple routing"""
    
    # Complexity indicators
    SIMPLE_KEYWORDS = {
        "what", "how", "when", "where", "who", "is", "are", "define",
        "list", "explain", "summarize"
    }
    
    COMPLEX_KEYWORDS = {
        "design", "invent", "improve", "optimize", "solve", "decide",
        "choose", "evaluate", "compare", "analyze", "integrate", "tradeoff"
    }
    
    def __init__(self):
        self.debate_threshold = 0.5  # Complexity score to trigger debate
    
    def classify(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Tuple[str, float]:
        """
        Classify problem as SIMPLE or COMPLEX
        
        Returns: (classification, complexity_score)
        """
        score = self._calculate_complexity_score(problem, context)
        classification = "COMPLEX" if score >= self.debate_threshold else "SIMPLE"
        
        logger.info(f"Problem Classification: {classification} (score: {score:.2f})")
        
        return classification, score
    
    def _calculate_complexity_score(self, problem: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate complexity score (0-1)
        
        Factors:
        - Problem length (longer = more complex)
        - Keyword analysis (design, optimize = complex)
        - Context richness (more constraints = more complex)
        - Multiple stakeholders/tradeoffs mentioned
        """
        score = 0.0
        
        # Factor 1: Problem length (0-0.2 points)
        words = len(problem.split())
        if words > 20:
            score += 0.15
        elif words > 10:
            score += 0.08
        
        # Factor 2: Keywords analysis (0-0.4 points)
        problem_lower = problem.lower()
        
        complex_count = sum(1 for keyword in self.COMPLEX_KEYWORDS if keyword in problem_lower)
        simple_count = sum(1 for keyword in self.SIMPLE_KEYWORDS if keyword in problem_lower)
        
        if complex_count > simple_count:
            score += min(0.4, complex_count * 0.1)
        
        # Factor 3: Multiple perspectives needed (0-0.2 points)
        if any(word in problem_lower for word in ["vs", "tradeoff", "balance", "vs.", "versus"]):
            score += 0.2
        
        # Factor 4: Design/Architecture (0-0.2 points)
        if any(word in problem_lower for word in ["medical", "device", "system", "architecture", "design"]):
            score += 0.15
        
        # Factor 5: Context richness (0-0.1 points)
        if context:
            num_constraints = len(context.get("constraints", []))
            score += min(0.1, num_constraints * 0.05)
        
        return min(1.0, score)
    
    def requires_debate(self, classification: str) -> bool:
        """Check if problem should use debate"""
        return classification == "COMPLEX"


@dataclass
class RoutingDecision:
    """Decision on how to route a problem"""
    use_debate: bool
    reason: str
    complexity_score: float
    recommended_agents: List[str]
    estimated_time: float


class SmartRouter:
    """Routes problems to either debate framework or simple model calls"""
    
    def __init__(self, debate_framework, model_orchestrator, complexity_classifier):
        self.debate_framework = debate_framework
        self.model_orchestrator = model_orchestrator
        self.classifier = complexity_classifier
    
    def route(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None,
        identity_anchors: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """
        Route problem to appropriate handler
        
        Returns: RoutingDecision with recommendation
        """
        classification, complexity_score = self.classifier.classify(problem, context)
        
        if classification == "COMPLEX":
            decision = RoutingDecision(
                use_debate=True,
                reason="Problem requires multi-perspective analysis and tradeoff evaluation",
                complexity_score=complexity_score,
                recommended_agents=["generalist", "specialist", "critic"],
                estimated_time=8.0  # Seconds
            )
        else:
            decision = RoutingDecision(
                use_debate=False,
                reason="Problem can be solved with direct model call",
                complexity_score=complexity_score,
                recommended_agents=["best_model"],
                estimated_time=2.0  # Seconds
            )
        
        logger.info(f"Routing Decision: {decision.reason}")
        logger.info(f"Use Debate: {decision.use_debate}")
        
        return decision


class OrchestrationIntegration:
    """Integrates debate framework with Jessica's model orchestrator"""
    
    def __init__(
        self,
        debate_framework,
        model_orchestrator,
        identity_anchors: Optional[Dict[str, Any]] = None
    ):
        self.debate_framework = debate_framework
        self.model_orchestrator = model_orchestrator
        self.complexity_classifier = ProblemComplexityClassifier()
        self.smart_router = SmartRouter(
            debate_framework,
            model_orchestrator,
            self.complexity_classifier
        )
        self.identity_anchors = identity_anchors or {}
        self.debate_results_history: List[Dict[str, Any]] = []
    
    def process(
        self,
        problem: str,
        context: Optional[Dict[str, Any]] = None,
        force_debate: bool = False
    ) -> Dict[str, Any]:
        """
        Process a problem using intelligent routing
        
        Args:
            problem: The problem to solve
            context: Additional context/constraints
            force_debate: Force debate even for simple problems
        
        Returns: Solution with metadata
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {problem[:100]}...")
        logger.info(f"{'='*60}\n")
        
        # Decide how to route
        routing = self.smart_router.route(problem, context, self.identity_anchors)
        
        if routing.use_debate or force_debate:
            logger.info("→ Using DEBATE framework\n")
            result = self._handle_debate(problem, context, routing)
        else:
            logger.info("→ Using SIMPLE model routing\n")
            result = self._handle_simple(problem, context)
        
        self.debate_results_history.append(result)
        return result
    
    def _handle_debate(
        self,
        problem: str,
        context: Optional[Dict[str, Any]],
        routing: RoutingDecision
    ) -> Dict[str, Any]:
        """Handle problem using debate framework"""
        
        try:
            final_solution, session = self.debate_framework.debate(
                problem=problem,
                context=context or {},
                identity_anchors=self.identity_anchors,
                num_rounds=2
            )
            
            # Get summary
            summary = self.debate_framework.get_debate_summary(session)
            
            result = {
                "method": "debate",
                "solution": {
                    "proposal": final_solution.proposal,
                    "reasoning": final_solution.reasoning,
                    "confidence": final_solution.confidence,
                    "alignment_score": final_solution.alignment_score,
                    "agent": final_solution.agent_role.value,
                    "tradeoffs": final_solution.tradeoffs,
                    "refinements": final_solution.refinements
                },
                "debate_summary": summary,
                "complexity_score": routing.complexity_score,
                "process_time": session.duration
            }
            
        except Exception as e:
            logger.error(f"Debate failed: {e}, falling back to simple routing")
            result = self._handle_simple(problem, context)
        
        return result
    
    def _handle_simple(
        self,
        problem: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle problem using simple model routing"""
        
        # Would call: response = self.model_orchestrator.generate(problem, context)
        
        result = {
            "method": "simple",
            "solution": {
                "proposal": f"Direct response to: {problem}",
                "reasoning": "Routed to optimal model",
                "confidence": 0.75,
                "alignment_score": 0.80,
                "agent": "best_model",
                "tradeoffs": [],
                "refinements": []
            },
            "complexity_score": 0.3,
            "process_time": 2.0
        }
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics on routing and debate usage"""
        
        if not self.debate_results_history:
            return {"total_problems": 0}
        
        debate_count = sum(1 for r in self.debate_results_history if r["method"] == "debate")
        simple_count = len(self.debate_results_history) - debate_count
        
        avg_complexity = sum(r["complexity_score"] for r in self.debate_results_history) / len(self.debate_results_history)
        avg_process_time = sum(r["process_time"] for r in self.debate_results_history) / len(self.debate_results_history)
        
        return {
            "total_problems": len(self.debate_results_history),
            "debate_used": debate_count,
            "simple_routing": simple_count,
            "debate_percentage": f"{100 * debate_count / len(self.debate_results_history):.1f}%",
            "avg_complexity_score": f"{avg_complexity:.2f}",
            "avg_process_time": f"{avg_process_time:.2f}s",
            "last_10_methods": [r["method"] for r in self.debate_results_history[-10:]]
        }


class DebateResultAnalyzer:
    """Analyzes debate outcomes for continuous improvement"""
    
    def __init__(self, autodidactic_loop):
        self.autodidactic_loop = autodidactic_loop
        self.debate_outcomes: List[Dict[str, Any]] = []
    
    def analyze_debate(self, session, final_solution) -> Dict[str, Any]:
        """
        Analyze debate outcome:
        - Which agent won (and why)?
        - Were critiques valid?
        - Did consensus emerge?
        - Learnings for future debates?
        """
        
        logger.info("Analyzing debate outcome...\n")
        
        analysis = {
            "session_id": session.session_id,
            "winning_perspective": final_solution.agent_role.value,
            "winning_score": final_solution.alignment_score,
            "critique_count": len(session.critiques),
            "refinement_count": sum(len(s.refinements) for s in session.solutions),
            "consensus_level": len(session.consensus_votes),
            "duration": session.duration,
        }
        
        # Extract learnings
        learnings = self._extract_learnings(session, final_solution)
        analysis["learnings"] = learnings
        
        self.debate_outcomes.append(analysis)
        
        # Feed to autodidactic loop for continuous improvement
        if self.autodidactic_loop:
            self._feed_to_autodidactic_loop(analysis)
        
        return analysis
    
    def _extract_learnings(self, session, final_solution) -> List[str]:
        """Extract learnings from debate"""
        learnings = []
        
        # Which agent's perspective won?
        learnings.append(f"For this problem type, {final_solution.agent_role.value} perspective was best")
        
        # Did critiques improve solutions?
        refined_count = sum(len(s.refinements) for s in session.solutions)
        if refined_count > 0:
            learnings.append(f"Critique process triggered {refined_count} refinements")
        
        # Was there consensus?
        if len(session.consensus_votes) > 0:
            learnings.append("Agents reached consensus on final solution")
        
        return learnings
    
    def _feed_to_autodidactic_loop(self, analysis: Dict[str, Any]):
        """Feed debate results to autodidactic loop for learning"""
        if self.autodidactic_loop:
            # Would call: self.autodidactic_loop.learn_from_debate(analysis)
            logger.info("Feeding debate results to autodidactic loop for learning...")


def create_integrated_orchestration(
    debate_framework,
    model_orchestrator,
    identity_anchors: Optional[Dict[str, Any]] = None,
    autodidactic_loop = None
) -> OrchestrationIntegration:
    """Create fully integrated orchestration system"""
    
    integration = OrchestrationIntegration(
        debate_framework=debate_framework,
        model_orchestrator=model_orchestrator,
        identity_anchors=identity_anchors
    )
    
    # Add result analyzer
    if autodidactic_loop:
        analyzer = DebateResultAnalyzer(autodidactic_loop)
        integration.analyzer = analyzer
    
    return integration
