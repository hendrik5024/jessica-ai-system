"""
Collaborative Multi-Agent Swarms - Debate Framework

Instead of simple tool routing, models act as autonomous agents that:
- Propose solutions from different perspectives
- Debate and critique each other's approaches
- MetaObserver judges based on alignment and quality
- Consensus-based decision making

Enables AGI-level collaborative reasoning.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in the swarm"""
    GENERALIST = "generalist"  # Big picture thinking
    SPECIALIST = "specialist"  # Technical expertise
    CRITIC = "critic"  # Challenge assumptions
    JUDGE = "judge"  # MetaObserver - evaluate and select
    INTEGRATOR = "integrator"  # Synthesize solutions


class DebatePhase(Enum):
    """Phases of the debate process"""
    PROBLEM_FRAMING = "problem_framing"  # Understand the problem
    PROPOSAL = "proposal"  # Initial solutions proposed
    CRITIQUE = "critique"  # Agents critique each other
    REBUTTAL = "rebuttal"  # Counter-arguments
    SYNTHESIS = "synthesis"  # Combine best ideas
    JUDGMENT = "judgment"  # Judge selects best solution
    CONSENSUS = "consensus"  # Final agreement


@dataclass
class Solution:
    """A proposed solution from an agent"""
    agent_id: str
    agent_role: AgentRole
    proposal: str  # The actual solution text
    reasoning: str  # Why this solution
    confidence: float  # 0-1 how confident in this solution
    tradeoffs: List[str]  # Known tradeoffs
    alignment_score: float = 0.0  # Filled by judge
    critique_count: int = 0  # How many times critiqued
    refinements: List[str] = field(default_factory=list)  # Changes made


@dataclass
class Critique:
    """Critique of another agent's solution"""
    from_agent_id: str
    to_solution_id: str
    criticism: str  # What's wrong
    alternative: Optional[str] = None  # Better approach
    severity: str = "minor"  # minor, moderate, critical
    constructive_suggestion: str = ""


@dataclass
class DebateSession:
    """Record of a debate session"""
    session_id: str
    problem: str
    start_time: float
    phases_completed: List[DebatePhase] = field(default_factory=list)
    solutions: List[Solution] = field(default_factory=list)
    critiques: List[Critique] = field(default_factory=list)
    final_solution: Optional[Solution] = None
    consensus_votes: Dict[str, int] = field(default_factory=dict)
    duration: float = 0.0
    quality_score: float = 0.0


class Agent:
    """Base class for autonomous swarm agent"""
    
    def __init__(self, agent_id: str, role: AgentRole, model_name: str):
        self.agent_id = agent_id
        self.role = role
        self.model_name = model_name
        self.proposals: List[Solution] = []
        self.critiques: List[Critique] = []
        
    def propose_solution(
        self,
        problem: str,
        context: Dict[str, Any],
        other_proposals: Optional[List[Solution]] = None
    ) -> Solution:
        """Propose a solution to the problem"""
        raise NotImplementedError
    
    def critique_solution(
        self,
        solution: Solution,
        problem: str,
        context: Dict[str, Any]
    ) -> Critique:
        """Critique another agent's solution"""
        raise NotImplementedError
    
    def refine_solution(
        self,
        original_solution: Solution,
        critiques: List[Critique],
        problem: str
    ) -> Solution:
        """Refine solution based on critiques"""
        raise NotImplementedError


class GeneralistAgent(Agent):
    """Mistral - Big picture thinking, holistic perspective"""
    
    def __init__(self, model_interface):
        super().__init__("mistral_generalist", AgentRole.GENERALIST, "Mistral")
        self.model = model_interface
    
    def propose_solution(
        self,
        problem: str,
        context: Dict[str, Any],
        other_proposals: Optional[List[Solution]] = None
    ) -> Solution:
        """Propose holistic solution"""
        logger.info(f"[GENERALIST] Analyzing problem holistically...")
        
        prompt = f"""
Problem: {problem}

Context:
{self._format_context(context)}

As a generalist, provide a holistic solution that considers:
1. Overall impact and user experience
2. Long-term sustainability
3. Stakeholder alignment
4. Risk distribution across areas

Provide your solution with clear reasoning and known tradeoffs.
"""
        
        # Mock response (would call actual model)
        response = self._generate_response(prompt, context)
        
        solution = Solution(
            agent_id=self.agent_id,
            agent_role=self.role,
            proposal=response.get("proposal", ""),
            reasoning=response.get("reasoning", ""),
            confidence=response.get("confidence", 0.75),
            tradeoffs=response.get("tradeoffs", [])
        )
        
        self.proposals.append(solution)
        return solution
    
    def critique_solution(
        self,
        solution: Solution,
        problem: str,
        context: Dict[str, Any]
    ) -> Critique:
        """Critique with holistic perspective"""
        logger.info(f"[GENERALIST] Critiquing solution from {solution.agent_id}...")
        
        prompt = f"""
Solution to critique:
{solution.proposal}

Problem: {problem}

From a holistic perspective, what are the issues with this solution?
Consider user experience, stakeholder impact, long-term effects.
"""
        
        critique_text = self._generate_critique_response(prompt)
        
        critique = Critique(
            from_agent_id=self.agent_id,
            to_solution_id=solution.agent_id,
            criticism=critique_text.get("criticism", ""),
            alternative=critique_text.get("alternative", None),
            severity=critique_text.get("severity", "minor"),
            constructive_suggestion=critique_text.get("suggestion", "")
        )
        
        self.critiques.append(critique)
        return critique
    
    def refine_solution(
        self,
        original_solution: Solution,
        critiques: List[Critique],
        problem: str
    ) -> Solution:
        """Refine based on critiques"""
        logger.info(f"[GENERALIST] Refining solution based on {len(critiques)} critiques...")
        
        refined = Solution(
            agent_id=self.agent_id,
            agent_role=self.role,
            proposal=original_solution.proposal,  # Would be updated
            reasoning=original_solution.reasoning,
            confidence=min(0.95, original_solution.confidence + 0.1),
            tradeoffs=original_solution.tradeoffs,
            refinements=[c.constructive_suggestion for c in critiques if c.constructive_suggestion]
        )
        
        return refined
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompt"""
        return "\n".join(f"{k}: {v}" for k, v in context.items())
    
    def _generate_response(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock: would call actual model"""
        return {
            "proposal": "Holistic solution focusing on user experience...",
            "reasoning": "This approach balances all stakeholder needs",
            "confidence": 0.78,
            "tradeoffs": ["May take longer to implement", "Requires stakeholder alignment"]
        }
    
    def _generate_critique_response(self, prompt: str) -> Dict[str, Any]:
        """Mock: would call actual model"""
        return {
            "criticism": "Missing consideration of...",
            "alternative": "Alternative approach could be...",
            "severity": "moderate",
            "suggestion": "Consider adding..."
        }


class SpecialistAgent(Agent):
    """CodeLlama - Technical expertise, implementation details"""
    
    def __init__(self, model_interface):
        super().__init__("codellama_specialist", AgentRole.SPECIALIST, "CodeLlama")
        self.model = model_interface
    
    def propose_solution(
        self,
        problem: str,
        context: Dict[str, Any],
        other_proposals: Optional[List[Solution]] = None
    ) -> Solution:
        """Propose technically optimal solution"""
        logger.info(f"[SPECIALIST] Analyzing problem technically...")
        
        prompt = f"""
Problem: {problem}

Technical context:
{self._format_technical_context(context)}

As a technical specialist, provide an implementation-focused solution:
1. Architecture and design patterns
2. Performance characteristics
3. Scalability considerations
4. Technical debt implications

Provide code examples where relevant.
"""
        
        response = self._generate_response(prompt, context)
        
        solution = Solution(
            agent_id=self.agent_id,
            agent_role=self.role,
            proposal=response.get("proposal", ""),
            reasoning=response.get("reasoning", ""),
            confidence=response.get("confidence", 0.82),
            tradeoffs=response.get("tradeoffs", [])
        )
        
        self.proposals.append(solution)
        return solution
    
    def critique_solution(
        self,
        solution: Solution,
        problem: str,
        context: Dict[str, Any]
    ) -> Critique:
        """Critique from technical perspective"""
        logger.info(f"[SPECIALIST] Critiquing solution for technical soundness...")
        
        prompt = f"""
Solution to evaluate:
{solution.proposal}

From technical perspective:
- Will this scale?
- Performance implications?
- Technical debt introduced?
- Better alternatives?
"""
        
        critique_text = self._generate_critique_response(prompt)
        
        return Critique(
            from_agent_id=self.agent_id,
            to_solution_id=solution.agent_id,
            criticism=critique_text.get("criticism", ""),
            alternative=critique_text.get("technical_alternative", None),
            severity=critique_text.get("severity", "minor"),
            constructive_suggestion=critique_text.get("suggestion", "")
        )
    
    def refine_solution(
        self,
        original_solution: Solution,
        critiques: List[Critique],
        problem: str
    ) -> Solution:
        """Refine with technical improvements"""
        refined = Solution(
            agent_id=self.agent_id,
            agent_role=self.role,
            proposal=original_solution.proposal,
            reasoning=original_solution.reasoning,
            confidence=min(0.95, original_solution.confidence + 0.12),
            tradeoffs=original_solution.tradeoffs,
            refinements=[c.constructive_suggestion for c in critiques if c.constructive_suggestion]
        )
        return refined
    
    def _format_technical_context(self, context: Dict[str, Any]) -> str:
        """Format technical context"""
        return "\n".join(f"- {k}: {v}" for k, v in context.items())
    
    def _generate_response(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock response"""
        return {
            "proposal": "Technical architecture using microservices...",
            "reasoning": "Ensures scalability and modularity",
            "confidence": 0.84,
            "tradeoffs": ["Increased operational complexity", "Network latency concerns"]
        }
    
    def _generate_critique_response(self, prompt: str) -> Dict[str, Any]:
        """Mock critique"""
        return {
            "criticism": "Performance bottleneck in data layer",
            "technical_alternative": "Use caching layer with redis",
            "severity": "critical",
            "suggestion": "Implement connection pooling"
        }


class CriticAgent(Agent):
    """Devil's Advocate - Challenges assumptions, finds flaws"""
    
    def __init__(self, model_interface):
        super().__init__("critic_agent", AgentRole.CRITIC, "Critic")
        self.model = model_interface
    
    def propose_solution(
        self,
        problem: str,
        context: Dict[str, Any],
        other_proposals: Optional[List[Solution]] = None
    ) -> Solution:
        """Propose alternative from contrarian perspective"""
        logger.info(f"[CRITIC] Proposing contrarian solution...")
        
        # Critic proposes by taking opposite of consensus
        if other_proposals:
            consensus_themes = self._extract_themes(other_proposals)
            prompt = f"""
Problem: {problem}

Most solutions focus on: {consensus_themes}

What if we take the opposite approach? 
Propose a contrarian solution that:
1. Challenges the consensus
2. Focuses on different tradeoffs
3. May reveal hidden assumptions

Why might this be better?
"""
        else:
            prompt = f"Problem: {problem}\n\nPropose a bold, contrarian solution."
        
        response = self._generate_response(prompt)
        
        solution = Solution(
            agent_id=self.agent_id,
            agent_role=self.role,
            proposal=response.get("proposal", ""),
            reasoning=response.get("reasoning", ""),
            confidence=response.get("confidence", 0.65),
            tradeoffs=response.get("tradeoffs", [])
        )
        
        return solution
    
    def critique_solution(
        self,
        solution: Solution,
        problem: str,
        context: Dict[str, Any]
    ) -> Critique:
        """Relentless critique - find all flaws"""
        logger.info(f"[CRITIC] Finding flaws in solution...")
        
        prompt = f"""
Solution: {solution.proposal}

Find the deepest flaws in this approach:
1. What assumptions is it making?
2. What could go wrong?
3. Who gets hurt by this solution?
4. What unintended consequences?
5. Better alternatives?
"""
        
        critique_text = self._generate_critique_response(prompt)
        
        return Critique(
            from_agent_id=self.agent_id,
            to_solution_id=solution.agent_id,
            criticism=critique_text.get("criticism", ""),
            alternative=critique_text.get("alternative", None),
            severity=critique_text.get("severity", "critical"),
            constructive_suggestion=critique_text.get("suggestion", "")
        )
    
    def refine_solution(
        self,
        original_solution: Solution,
        critiques: List[Critique],
        problem: str
    ) -> Solution:
        """Strengthen by addressing weaknesses head-on"""
        refined = Solution(
            agent_id=self.agent_id,
            agent_role=self.role,
            proposal=original_solution.proposal,
            reasoning=f"{original_solution.reasoning}\n\nAddressed critiques: {len(critiques)}",
            confidence=min(0.90, original_solution.confidence + 0.15),
            tradeoffs=original_solution.tradeoffs,
            refinements=[c.constructive_suggestion for c in critiques if c.constructive_suggestion]
        )
        return refined
    
    def _extract_themes(self, proposals: List[Solution]) -> str:
        """Extract common themes from proposals"""
        themes = set()
        for p in proposals:
            if "user" in p.proposal.lower():
                themes.add("user-centric")
            if "scale" in p.proposal.lower():
                themes.add("scalability")
            if "cost" in p.proposal.lower():
                themes.add("cost-optimization")
        return ", ".join(themes) if themes else "consensus approach"
    
    def _generate_response(self, prompt: str) -> Dict[str, Any]:
        """Mock response"""
        return {
            "proposal": "Radical simplification: do the opposite of current trend",
            "reasoning": "Often the most overlooked path",
            "confidence": 0.68,
            "tradeoffs": ["Risky", "May not be accepted", "Could disrupt workflows"]
        }
    
    def _generate_critique_response(self, prompt: str) -> Dict[str, Any]:
        """Mock critique"""
        return {
            "criticism": "This ignores fundamental constraint...",
            "alternative": "What if we worked within the constraint?",
            "severity": "critical",
            "suggestion": "Reframe the problem statement first"
        }


class JudgeAgent(Agent):
    """MetaObserver - Evaluates solutions based on alignment and quality"""
    
    def __init__(self, model_interface, meta_observer):
        super().__init__("judge_meta_observer", AgentRole.JUDGE, "MetaObserver")
        self.model = model_interface
        self.meta_observer = meta_observer  # Access to alignment checker
    
    def evaluate_solution(
        self,
        solution: Solution,
        problem: str,
        identity_anchors: Dict[str, Any]
    ) -> Tuple[float, str]:
        """
        Evaluate solution on:
        1. Quality (0-1)
        2. Alignment with identity anchors (0-1)
        3. Alignment with long-term goals (0-1)
        4. Risk assessment (0-1)
        
        Returns: (alignment_score, reasoning)
        """
        logger.info(f"[JUDGE] Evaluating solution from {solution.agent_id}...")
        
        quality_score = self._assess_quality(solution)
        alignment_score = self._assess_alignment(solution, identity_anchors)
        feasibility_score = self._assess_feasibility(solution, problem)
        risk_score = self._assess_risk(solution)
        
        # Weighted combination
        final_score = (
            quality_score * 0.25 +
            alignment_score * 0.30 +
            feasibility_score * 0.25 +
            (1.0 - risk_score) * 0.20  # Lower risk is better
        )
        
        reasoning = f"""
Quality: {quality_score:.2f}
Alignment: {alignment_score:.2f}
Feasibility: {feasibility_score:.2f}
Risk (lower is better): {risk_score:.2f}
─────────────────────────
Final Score: {final_score:.2f}
"""
        
        solution.alignment_score = final_score
        return final_score, reasoning
    
    def select_best_solution(
        self,
        solutions: List[Solution],
        evaluated_scores: Dict[str, float]
    ) -> Tuple[Solution, str]:
        """Select the best solution from candidates"""
        logger.info(f"[JUDGE] Selecting best from {len(solutions)} candidates...")
        
        if not solutions:
            raise ValueError("No solutions to evaluate")
        
        best_solution = max(
            solutions,
            key=lambda s: evaluated_scores.get(s.agent_id, 0.0)
        )
        
        best_score = evaluated_scores.get(best_solution.agent_id, 0.0)
        second_best_score = sorted(
            evaluated_scores.values(), reverse=True
        )[1] if len(evaluated_scores) > 1 else 0.0
        
        confidence = min(0.99, best_score - second_best_score + 0.5)
        
        reasoning = f"""
Selected: Solution from {best_solution.agent_id} ({best_solution.agent_role.value})
Score: {best_score:.2f}
Confidence: {confidence:.0%}

Reasoning:
{best_solution.reasoning}

Confidence margin: {(best_score - second_best_score):.2f}
"""
        
        return best_solution, reasoning
    
    def _assess_quality(self, solution: Solution) -> float:
        """Assess solution quality (clarity, completeness, soundness)"""
        # Mock assessment
        score = 0.7
        if len(solution.tradeoffs) >= 2:
            score += 0.15
        if solution.reasoning:
            score += 0.15
        return min(1.0, score)
    
    def _assess_alignment(
        self,
        solution: Solution,
        identity_anchors: Dict[str, Any]
    ) -> float:
        """Assess alignment with Jessica's identity and values"""
        # Would check against identity anchors
        return 0.75
    
    def _assess_feasibility(self, solution: Solution, problem: str) -> float:
        """Assess feasibility to implement"""
        # Would check against constraints
        return 0.80
    
    def _assess_risk(self, solution: Solution) -> float:
        """Assess risk level (0 = safe, 1 = risky)"""
        risk = len(solution.tradeoffs) * 0.1  # More tradeoffs = more risk
        return min(1.0, risk)


class DebateFramework:
    """Orchestrates the multi-agent debate process"""
    
    def __init__(
        self,
        generalist: GeneralistAgent,
        specialist: SpecialistAgent,
        critic: CriticAgent,
        judge: JudgeAgent,
        meta_observer: Any = None
    ):
        self.generalist = generalist
        self.specialist = specialist
        self.critic = critic
        self.judge = judge
        self.meta_observer = meta_observer
        self.agents = [generalist, specialist, critic]
        self.debate_history: List[DebateSession] = []
    
    def debate(
        self,
        problem: str,
        context: Dict[str, Any],
        identity_anchors: Dict[str, Any],
        num_rounds: int = 2
    ) -> Tuple[Solution, DebateSession]:
        """
        Run a full debate process
        
        Flow:
        1. Problem Framing
        2. Proposal (all agents propose)
        3. Critique (agents critique each other)
        4. Rebuttal (agents refine solutions)
        5. Synthesis (combine best ideas)
        6. Judgment (judge selects best)
        7. Consensus (validate final solution)
        """
        session_id = f"debate_{int(time.time())}"
        session = DebateSession(
            session_id=session_id,
            problem=problem,
            start_time=time.time()
        )
        
        logger.info(f"=== DEBATE SESSION {session_id} ===")
        logger.info(f"Problem: {problem}\n")
        
        # Phase 1: Problem Framing
        logger.info("PHASE 1: Problem Framing")
        self._frame_problem(problem, context, session)
        session.phases_completed.append(DebatePhase.PROBLEM_FRAMING)
        
        # Phase 2: Initial Proposals
        logger.info("\nPHASE 2: Initial Proposals")
        proposals = self._proposal_phase(problem, context, session)
        session.solutions.extend(proposals)
        session.phases_completed.append(DebatePhase.PROPOSAL)
        
        # Phase 3 & 4: Multiple rounds of critique and rebuttal
        for round_num in range(num_rounds):
            logger.info(f"\nPHASE 3.{round_num+1}: Critique Round {round_num+1}")
            self._critique_phase(session)
            session.phases_completed.append(DebatePhase.CRITIQUE)
            
            logger.info(f"\nPHASE 4.{round_num+1}: Rebuttal Round {round_num+1}")
            self._rebuttal_phase(session, problem)
            session.phases_completed.append(DebatePhase.REBUTTAL)
        
        # Phase 5: Synthesis
        logger.info("\nPHASE 5: Synthesis")
        synthesized = self._synthesis_phase(session, problem)
        session.solutions.append(synthesized)
        session.phases_completed.append(DebatePhase.SYNTHESIS)
        
        # Phase 6: Judgment
        logger.info("\nPHASE 6: Judgment")
        final_solution, judgment_reasoning = self._judgment_phase(
            session, problem, identity_anchors
        )
        session.final_solution = final_solution
        session.phases_completed.append(DebatePhase.JUDGMENT)
        logger.info(judgment_reasoning)
        
        # Phase 7: Consensus
        logger.info("\nPHASE 7: Consensus")
        consensus_score = self._consensus_phase(session, final_solution)
        session.consensus_votes = consensus_score
        session.phases_completed.append(DebatePhase.CONSENSUS)
        
        session.duration = time.time() - session.start_time
        self.debate_history.append(session)
        
        logger.info(f"\n=== DEBATE COMPLETE ===")
        logger.info(f"Duration: {session.duration:.1f}s")
        logger.info(f"Winner: {final_solution.agent_role.value}\n")
        
        return final_solution, session
    
    def _frame_problem(
        self,
        problem: str,
        context: Dict[str, Any],
        session: DebateSession
    ):
        """Understand and frame the problem"""
        logger.info(f"Problem: {problem}")
        logger.info(f"Context: {context}\n")
    
    def _proposal_phase(
        self,
        problem: str,
        context: Dict[str, Any],
        session: DebateSession
    ) -> List[Solution]:
        """All agents propose solutions"""
        proposals = []
        
        # Generalist proposal
        logger.info("\n[GENERALIST] Proposing holistic solution...")
        gen_proposal = self.generalist.propose_solution(problem, context)
        logger.info(f"  → Proposal: {gen_proposal.proposal[:100]}...")
        logger.info(f"  → Confidence: {gen_proposal.confidence:.0%}")
        proposals.append(gen_proposal)
        
        # Specialist proposal
        logger.info("\n[SPECIALIST] Proposing technical solution...")
        spec_proposal = self.specialist.propose_solution(
            problem, context, other_proposals=proposals
        )
        logger.info(f"  → Proposal: {spec_proposal.proposal[:100]}...")
        logger.info(f"  → Confidence: {spec_proposal.confidence:.0%}")
        proposals.append(spec_proposal)
        
        # Critic proposal
        logger.info("\n[CRITIC] Proposing contrarian solution...")
        crit_proposal = self.critic.propose_solution(
            problem, context, other_proposals=proposals
        )
        logger.info(f"  → Proposal: {crit_proposal.proposal[:100]}...")
        logger.info(f"  → Confidence: {crit_proposal.confidence:.0%}")
        proposals.append(crit_proposal)
        
        return proposals
    
    def _critique_phase(self, session: DebateSession):
        """Agents critique each other's solutions"""
        logger.info("\nAgents critiquing each other's solutions:\n")
        
        for proposal in session.solutions:
            if proposal.agent_id == self.generalist.agent_id:
                # Specialist and Critic critique Generalist
                spec_critique = self.specialist.critique_solution(
                    proposal, session.problem, {}
                )
                crit_critique = self.critic.critique_solution(
                    proposal, session.problem, {}
                )
                session.critiques.extend([spec_critique, crit_critique])
                proposal.critique_count += 2
                
                logger.info(f"[SPECIALIST] Critiques Generalist: {spec_critique.criticism[:80]}...")
                logger.info(f"[CRITIC] Critiques Generalist: {crit_critique.criticism[:80]}...")
    
    def _rebuttal_phase(self, session: DebateSession, problem: str):
        """Agents refine their solutions based on critiques"""
        logger.info("\nAgents refining solutions based on critiques:\n")
        
        for proposal in session.solutions:
            relevant_critiques = [
                c for c in session.critiques
                if c.to_solution_id == proposal.agent_id
            ]
            
            if relevant_critiques:
                if proposal.agent_id == self.generalist.agent_id:
                    refined = self.generalist.refine_solution(
                        proposal, relevant_critiques, problem
                    )
                elif proposal.agent_id == self.specialist.agent_id:
                    refined = self.specialist.refine_solution(
                        proposal, relevant_critiques, problem
                    )
                else:
                    refined = self.critic.refine_solution(
                        proposal, relevant_critiques, problem
                    )
                
                logger.info(f"[{proposal.agent_role.value.upper()}] Refined confidence: {refined.confidence:.0%}")
                # Update original with refinements
                proposal.refinements = refined.refinements
                proposal.confidence = refined.confidence
    
    def _synthesis_phase(self, session: DebateSession, problem: str) -> Solution:
        """Combine best ideas from all solutions"""
        logger.info("\nSynthesizing best elements from all proposals...\n")
        
        best_ideas = []
        for proposal in session.solutions:
            best_ideas.append({
                "from": proposal.agent_id,
                "idea": proposal.proposal[:100],
                "confidence": proposal.confidence
            })
        
        # Integrator combines
        synthesized_proposal = (
            f"Synthesis combining:\n" +
            "\n".join(f"- {b['from']}: {b['idea']}" for b in best_ideas)
        )
        
        synthesized = Solution(
            agent_id="integrator_synthesis",
            agent_role=AgentRole.INTEGRATOR,
            proposal=synthesized_proposal,
            reasoning="Combined best elements from all perspectives",
            confidence=sum(s.confidence for s in session.solutions) / len(session.solutions),
            tradeoffs=[]
        )
        
        logger.info(f"Synthesized solution confidence: {synthesized.confidence:.0%}")
        
        return synthesized
    
    def _judgment_phase(
        self,
        session: DebateSession,
        problem: str,
        identity_anchors: Dict[str, Any]
    ) -> Tuple[Solution, str]:
        """Judge evaluates and selects best solution"""
        logger.info("\nJudge evaluating all solutions:\n")
        
        evaluated_scores = {}
        
        for solution in session.solutions:
            if solution.agent_id != "integrator_synthesis":
                score, reasoning = self.judge.evaluate_solution(
                    solution, problem, identity_anchors
                )
                evaluated_scores[solution.agent_id] = score
                logger.info(f"\n{solution.agent_role.value.upper()} Score: {score:.2f}")
                logger.info(reasoning)
        
        # Also evaluate synthesized
        if session.solutions[-1].agent_id == "integrator_synthesis":
            score, _ = self.judge.evaluate_solution(
                session.solutions[-1], problem, identity_anchors
            )
            evaluated_scores["integrator"] = score
            logger.info(f"\nINTEGRATOR Score: {score:.2f}")
        
        # Select best
        best_solution, selection_reasoning = self.judge.select_best_solution(
            session.solutions, evaluated_scores
        )
        
        return best_solution, selection_reasoning
    
    def _consensus_phase(
        self,
        session: DebateSession,
        final_solution: Solution
    ) -> Dict[str, int]:
        """Validate consensus - agents vote on final solution"""
        logger.info("\nAgents voting on final solution:\n")
        
        votes = {}
        for agent in self.agents:
            # Would be agent.vote(final_solution)
            vote = 1  # Mock: all agree
            votes[agent.agent_id] = vote
            logger.info(f"{agent.agent_id}: {vote}")
        
        consensus_level = sum(votes.values()) / len(votes)
        logger.info(f"\nConsensus Level: {consensus_level:.0%}")
        
        return votes
    
    def get_debate_summary(self, session: DebateSession) -> Dict[str, Any]:
        """Get summary of debate"""
        return {
            "session_id": session.session_id,
            "problem": session.problem,
            "duration": session.duration,
            "phases": [p.value for p in session.phases_completed],
            "proposals_count": len([s for s in session.solutions if s.agent_role != AgentRole.INTEGRATOR]),
            "critiques_count": len(session.critiques),
            "final_solution_agent": session.final_solution.agent_role.value if session.final_solution else None,
            "final_score": session.final_solution.alignment_score if session.final_solution else 0,
            "consensus": session.consensus_votes
        }


def create_debate_framework(
    model_interfaces: Dict[str, Any],
    meta_observer: Any = None
) -> DebateFramework:
    """Create a debate framework with all agent types"""
    
    generalist = GeneralistAgent(model_interfaces.get("mistral"))
    specialist = SpecialistAgent(model_interfaces.get("codellama"))
    critic = CriticAgent(model_interfaces.get("model_3"))
    judge = JudgeAgent(model_interfaces.get("model_4"), meta_observer)
    
    return DebateFramework(
        generalist=generalist,
        specialist=specialist,
        critic=critic,
        judge=judge,
        meta_observer=meta_observer
    )
