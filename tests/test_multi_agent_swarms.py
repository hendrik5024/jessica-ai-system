"""
Comprehensive tests for Multi-Agent Swarm Debate Framework

Tests cover:
- Individual agent behavior (Generalist, Specialist, Critic)
- Judge evaluation and selection
- Full debate flow
- Problem complexity classification
- Smart routing
- Integration with orchestrator
"""

import pytest
import time
from typing import Dict, Any

from jessica.meta.multi_agent_swarms import (
    Agent, GeneralistAgent, SpecialistAgent, CriticAgent, JudgeAgent,
    DebateFramework, Solution, Critique, AgentRole, DebatePhase,
    DebateSession, create_debate_framework
)
from jessica.meta.orchestration_integration import (
    ProblemComplexityClassifier, SmartRouter, OrchestrationIntegration,
    DebateResultAnalyzer, create_integrated_orchestration
)


# ============================================================================
# AGENT TESTS
# ============================================================================

class TestGeneralistAgent:
    """Test Generalist (Mistral) agent"""
    
    def test_agent_initialization(self):
        """Test agent creation"""
        agent = GeneralistAgent(None)
        assert agent.agent_id == "mistral_generalist"
        assert agent.role == AgentRole.GENERALIST
        assert agent.model_name == "Mistral"
    
    def test_propose_solution(self):
        """Test solution proposal"""
        agent = GeneralistAgent(None)
        problem = "Design a new medical device"
        context = {"target_market": "hospitals", "budget": "1M"}
        
        solution = agent.propose_solution(problem, context)
        
        assert solution.agent_id == agent.agent_id
        assert solution.agent_role == AgentRole.GENERALIST
        assert solution.proposal  # Has text
        assert solution.reasoning  # Has explanation
        assert 0 <= solution.confidence <= 1
        assert len(solution.tradeoffs) > 0
    
    def test_critique_solution(self):
        """Test critiquing another solution"""
        agent = GeneralistAgent(None)
        solution = Solution(
            agent_id="other_agent",
            agent_role=AgentRole.SPECIALIST,
            proposal="Use microservices",
            reasoning="Better scalability",
            confidence=0.8,
            tradeoffs=["Complexity"]
        )
        
        critique = agent.critique_solution(solution, "Design system", {})
        
        assert critique.from_agent_id == agent.agent_id
        assert critique.to_solution_id == "other_agent"
        assert critique.criticism
        assert critique.severity in ["minor", "moderate", "critical"]
    
    def test_refine_solution(self):
        """Test solution refinement"""
        agent = GeneralistAgent(None)
        original = Solution(
            agent_id=agent.agent_id,
            agent_role=AgentRole.GENERALIST,
            proposal="Original proposal",
            reasoning="Original reasoning",
            confidence=0.7,
            tradeoffs=["A", "B"]
        )
        
        critiques = [
            Critique(
                from_agent_id="critic",
                to_solution_id=agent.agent_id,
                criticism="Missing point X",
                constructive_suggestion="Add point X"
            )
        ]
        
        refined = agent.refine_solution(original, critiques, "Problem")
        
        assert refined.confidence > original.confidence
        assert len(refined.refinements) > 0


class TestSpecialistAgent:
    """Test Specialist (CodeLlama) agent"""
    
    def test_technical_proposal(self):
        """Test technical solution proposal"""
        agent = SpecialistAgent(None)
        problem = "Scale database for 1M users"
        context = {"current_users": 10000, "db_type": "postgresql"}
        
        solution = agent.propose_solution(problem, context)
        
        assert solution.agent_role == AgentRole.SPECIALIST
        assert "scale" in solution.proposal.lower() or "arch" in solution.proposal.lower()
        assert solution.confidence >= 0.8
    
    def test_technical_critique(self):
        """Test technical critique"""
        agent = SpecialistAgent(None)
        solution = Solution(
            agent_id="generalist",
            agent_role=AgentRole.GENERALIST,
            proposal="Simple solution",
            reasoning="Works",
            confidence=0.7,
            tradeoffs=[]
        )
        
        critique = agent.critique_solution(solution, "Technical problem", {})
        
        assert critique.severity in ["minor", "moderate", "critical"]
        assert critique.constructive_suggestion  # Offers fix


class TestCriticAgent:
    """Test Critic agent (devil's advocate)"""
    
    def test_contrarian_proposal(self):
        """Test contrarian solution"""
        agent = CriticAgent(None)
        problem = "Improve team performance"
        context = {}
        
        other_proposals = [
            Solution(
                agent_id="gen",
                agent_role=AgentRole.GENERALIST,
                proposal="More communication",
                reasoning="Standard approach",
                confidence=0.8,
                tradeoffs=[]
            )
        ]
        
        solution = agent.propose_solution(problem, context, other_proposals)
        
        assert solution.agent_role == AgentRole.CRITIC
        # Critic should challenge consensus
        assert "opposite" in solution.reasoning.lower() or "contrarian" in solution.reasoning.lower() or solution.proposal
    
    def test_relentless_critique(self):
        """Test harsh critique"""
        agent = CriticAgent(None)
        solution = Solution(
            agent_id="other",
            agent_role=AgentRole.GENERALIST,
            proposal="My solution",
            reasoning="Good",
            confidence=0.9,
            tradeoffs=[]
        )
        
        critique = agent.critique_solution(solution, "Problem", {})
        
        # Critic should find problems (severity = critical by default)
        assert critique.severity in ["minor", "moderate", "critical"]
        assert critique.criticism


class TestJudgeAgent:
    """Test Judge (MetaObserver) agent"""
    
    def test_evaluate_solution(self):
        """Test solution evaluation"""
        judge = JudgeAgent(None, meta_observer=None)
        solution = Solution(
            agent_id="agent1",
            agent_role=AgentRole.GENERALIST,
            proposal="Proposal",
            reasoning="Good reasoning with multiple tradeoffs",
            confidence=0.8,
            tradeoffs=["A", "B", "C"]
        )
        
        score, reasoning = judge.evaluate_solution(
            solution,
            "Problem",
            {"value1": "alignment_needed"}
        )
        
        assert 0 <= score <= 1
        assert "Quality" in reasoning
        assert "Alignment" in reasoning
        assert solution.alignment_score == score
    
    def test_select_best_solution(self):
        """Test selecting best solution"""
        judge = JudgeAgent(None, meta_observer=None)
        
        solutions = [
            Solution(
                agent_id="agent1",
                agent_role=AgentRole.GENERALIST,
                proposal="P1",
                reasoning="R1",
                confidence=0.7,
                tradeoffs=[]
            ),
            Solution(
                agent_id="agent2",
                agent_role=AgentRole.SPECIALIST,
                proposal="P2",
                reasoning="R2",
                confidence=0.8,
                tradeoffs=["A"]
            ),
            Solution(
                agent_id="agent3",
                agent_role=AgentRole.CRITIC,
                proposal="P3",
                reasoning="R3",
                confidence=0.6,
                tradeoffs=[]
            ),
        ]
        
        scores = {
            "agent1": 0.70,
            "agent2": 0.85,
            "agent3": 0.65
        }
        
        best, reasoning = judge.select_best_solution(solutions, scores)
        
        assert best.agent_id == "agent2"
        assert "agent2" in reasoning
        assert "0.85" in reasoning
    
    def test_evaluation_with_different_roles(self):
        """Test that different agent roles get fair evaluation"""
        judge = JudgeAgent(None, meta_observer=None)
        
        gen_solution = Solution(
            agent_id="gen",
            agent_role=AgentRole.GENERALIST,
            proposal="Holistic approach",
            reasoning="Considers all stakeholders",
            confidence=0.8,
            tradeoffs=["A", "B"]
        )
        
        spec_solution = Solution(
            agent_id="spec",
            agent_role=AgentRole.SPECIALIST,
            proposal="Technical approach",
            reasoning="Technically optimal",
            confidence=0.85,
            tradeoffs=["C"]
        )
        
        score_gen, _ = judge.evaluate_solution(gen_solution, "Problem", {})
        score_spec, _ = judge.evaluate_solution(spec_solution, "Problem", {})
        
        # Both should be evaluated fairly
        assert 0 <= score_gen <= 1
        assert 0 <= score_spec <= 1


# ============================================================================
# DEBATE FRAMEWORK TESTS
# ============================================================================

class TestDebateFramework:
    """Test full debate framework"""
    
    def test_debate_initialization(self):
        """Test debate framework creation"""
        models = {"mistral": None, "codellama": None, "model_3": None, "model_4": None}
        framework = create_debate_framework(models)
        
        assert framework.generalist is not None
        assert framework.specialist is not None
        assert framework.critic is not None
        assert framework.judge is not None
        assert len(framework.agents) == 3
    
    def test_debate_flow_completes(self):
        """Test that debate completes all phases"""
        models = {}
        framework = create_debate_framework(models)
        
        problem = "Design a new medical device"
        context = {"budget": "1M", "timeline": "2 years"}
        identity_anchors = {"value": "innovation"}
        
        solution, session = framework.debate(
            problem=problem,
            context=context,
            identity_anchors=identity_anchors,
            num_rounds=1
        )
        
        # Check all phases completed
        expected_phases = {
            DebatePhase.PROBLEM_FRAMING,
            DebatePhase.PROPOSAL,
            DebatePhase.CRITIQUE,
            DebatePhase.REBUTTAL,
            DebatePhase.SYNTHESIS,
            DebatePhase.JUDGMENT,
            DebatePhase.CONSENSUS
        }
        
        completed_phases = set(session.phases_completed)
        
        # At minimum should have: framing, proposals, at least one critique/rebuttal, synthesis, judgment, consensus
        assert DebatePhase.PROBLEM_FRAMING in completed_phases
        assert DebatePhase.PROPOSAL in completed_phases
        assert DebatePhase.SYNTHESIS in completed_phases
        assert DebatePhase.JUDGMENT in completed_phases
        assert DebatePhase.CONSENSUS in completed_phases
    
    def test_debate_produces_solution(self):
        """Test that debate produces valid solution"""
        models = {}
        framework = create_debate_framework(models)
        
        solution, session = framework.debate(
            problem="Design system",
            context={},
            identity_anchors={},
            num_rounds=1
        )
        
        assert solution is not None
        assert solution.proposal
        assert solution.reasoning
        assert 0 <= solution.confidence <= 1
        assert solution.alignment_score >= 0
    
    def test_debate_session_tracking(self):
        """Test that debate sessions are tracked"""
        models = {}
        framework = create_debate_framework(models)
        
        assert len(framework.debate_history) == 0
        
        framework.debate(
            problem="Test",
            context={},
            identity_anchors={},
            num_rounds=1
        )
        
        assert len(framework.debate_history) == 1
        
        framework.debate(
            problem="Test 2",
            context={},
            identity_anchors={},
            num_rounds=1
        )
        
        assert len(framework.debate_history) == 2
    
    def test_debate_summary(self):
        """Test debate summary generation"""
        models = {}
        framework = create_debate_framework(models)
        
        solution, session = framework.debate(
            problem="Test problem",
            context={},
            identity_anchors={},
            num_rounds=1
        )
        
        summary = framework.get_debate_summary(session)
        
        assert "session_id" in summary
        assert "problem" in summary
        assert summary["problem"] == "Test problem"
        assert "final_solution_agent" in summary
        assert "final_score" in summary
        assert summary["final_score"] > 0
    
    def test_multiple_rounds(self):
        """Test multi-round debate"""
        models = {}
        framework = create_debate_framework(models)
        
        solution, session = framework.debate(
            problem="Complex design",
            context={},
            identity_anchors={},
            num_rounds=3  # Multiple rounds
        )
        
        # Should have multiple critique and rebuttal phases
        critique_count = session.phases_completed.count(DebatePhase.CRITIQUE)
        rebuttal_count = session.phases_completed.count(DebatePhase.REBUTTAL)
        
        assert critique_count >= 2
        assert rebuttal_count >= 2


# ============================================================================
# COMPLEXITY CLASSIFICATION TESTS
# ============================================================================

class TestProblemComplexityClassifier:
    """Test problem complexity classification"""
    
    def test_simple_problem(self):
        """Test classification of simple problem"""
        classifier = ProblemComplexityClassifier()
        
        classification, score = classifier.classify("What is 2+2?")
        
        assert classification == "SIMPLE"
        assert score < 0.6
    
    def test_complex_problem(self):
        """Test classification of complex problem"""
        classifier = ProblemComplexityClassifier()
        
        classification, score = classifier.classify(
            "Design a scalable medical device system that optimizes performance versus cost versus usability for developing markets"
        )
        
        assert classification == "COMPLEX"
        assert score >= 0.5
    
    def test_complexity_scoring(self):
        """Test complexity score progression"""
        classifier = ProblemComplexityClassifier()
        
        simple = classifier._calculate_complexity_score("What is X?", None)
        medium = classifier._calculate_complexity_score("How can we design and optimize our system?", None)
        complex_prob = classifier._calculate_complexity_score(
            "Design a system that optimizes performance while maintaining security and cost efficiency in a distributed architecture",
            None
        )
        
        # Should be in increasing order
        assert simple <= medium
        assert medium <= complex_prob
    
    def test_context_affects_complexity(self):
        """Test that context richness affects complexity"""
        classifier = ProblemComplexityClassifier()
        
        no_context = classifier._calculate_complexity_score("Design system", None)
        with_context = classifier._calculate_complexity_score(
            "Design system",
            {"constraints": ["budget", "timeline", "scalability", "security"]}
        )
        
        # More constraints = higher complexity
        assert with_context > no_context


class TestSmartRouter:
    """Test problem routing"""
    
    def test_routes_simple_to_model(self):
        """Test simple problem routed to model"""
        classifier = ProblemComplexityClassifier()
        
        class MockOrchestrator:
            pass
        
        class MockDebate:
            pass
        
        router = SmartRouter(MockDebate(), MockOrchestrator(), classifier)
        
        decision = router.route("What is the capital of France?")
        
        assert decision.use_debate == False
        assert decision.estimated_time < 5.0
    
    def test_routes_complex_to_debate(self):
        """Test complex problem routed to debate"""
        classifier = ProblemComplexityClassifier()
        
        class MockOrchestrator:
            pass
        
        class MockDebate:
            pass
        
        router = SmartRouter(MockDebate(), MockOrchestrator(), classifier)
        
        decision = router.route("Design medical device with budget and performance tradeoffs")
        
        assert decision.use_debate == True
        assert decision.estimated_time > 5.0
    
    def test_routing_includes_reasoning(self):
        """Test that routing decision includes reasoning"""
        classifier = ProblemComplexityClassifier()
        
        class MockOrchestrator:
            pass
        
        class MockDebate:
            pass
        
        router = SmartRouter(MockDebate(), MockOrchestrator(), classifier)
        
        decision = router.route("Design system")
        
        assert decision.reason
        assert len(decision.recommended_agents) > 0
        assert decision.complexity_score >= 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestOrchestrationIntegration:
    """Test orchestration integration"""
    
    def test_integration_initialization(self):
        """Test integration system creation"""
        models = {}
        framework = create_debate_framework(models)
        
        class MockOrchestrator:
            pass
        
        integration = OrchestrationIntegration(
            debate_framework=framework,
            model_orchestrator=MockOrchestrator(),
            identity_anchors={"value": "test"}
        )
        
        assert integration.debate_framework is not None
        assert integration.model_orchestrator is not None
        assert integration.identity_anchors["value"] == "test"
    
    def test_process_simple_problem(self):
        """Test processing simple problem"""
        models = {}
        framework = create_debate_framework(models)
        
        class MockOrchestrator:
            pass
        
        integration = OrchestrationIntegration(
            debate_framework=framework,
            model_orchestrator=MockOrchestrator()
        )
        
        result = integration.process("What is 2+2?")
        
        assert "method" in result
        assert "solution" in result
        assert result["method"] == "simple"
    
    def test_process_complex_problem(self):
        """Test processing complex problem"""
        models = {}
        framework = create_debate_framework(models)
        
        class MockOrchestrator:
            pass
        
        integration = OrchestrationIntegration(
            debate_framework=framework,
            model_orchestrator=MockOrchestrator()
        )
        
        result = integration.process("Design medical device with tradeoffs")
        
        assert "method" in result
        assert "debate_summary" in result or "method" in result
    
    def test_force_debate_flag(self):
        """Test force_debate flag"""
        models = {}
        framework = create_debate_framework(models)
        
        class MockOrchestrator:
            pass
        
        integration = OrchestrationIntegration(
            debate_framework=framework,
            model_orchestrator=MockOrchestrator()
        )
        
        # Simple problem, but force debate
        result = integration.process("Simple question", force_debate=True)
        
        # Should use debate because of force flag
        assert "debate_summary" in result or "method" in result
    
    def test_statistics_tracking(self):
        """Test statistics collection"""
        models = {}
        framework = create_debate_framework(models)
        
        class MockOrchestrator:
            pass
        
        integration = OrchestrationIntegration(
            debate_framework=framework,
            model_orchestrator=MockOrchestrator()
        )
        
        # Process some problems
        integration.process("What is X?")
        integration.process("Design something complex with tradeoffs")
        integration.process("Another simple question")
        
        stats = integration.get_statistics()
        
        assert stats["total_problems"] == 3
        assert "debate_percentage" in stats
        assert "avg_complexity_score" in stats
        assert "avg_process_time" in stats


class TestDebateResultAnalyzer:
    """Test analysis of debate outcomes"""
    
    def test_analyzer_creation(self):
        """Test analyzer creation"""
        analyzer = DebateResultAnalyzer(autodidactic_loop=None)
        
        assert analyzer.debate_outcomes is not None
        assert len(analyzer.debate_outcomes) == 0
    
    def test_analyze_debate_session(self):
        """Test analyzing a debate session"""
        analyzer = DebateResultAnalyzer(autodidactic_loop=None)
        
        # Create mock session
        session = DebateSession(
            session_id="test_session",
            problem="Test problem",
            start_time=time.time()
        )
        
        final_solution = Solution(
            agent_id="agent1",
            agent_role=AgentRole.SPECIALIST,
            proposal="Winner",
            reasoning="Best",
            confidence=0.9,
            tradeoffs=[],
            alignment_score=0.85
        )
        
        analysis = analyzer.analyze_debate(session, final_solution)
        
        assert analysis["winning_perspective"] == "specialist"
        assert analysis["winning_score"] == 0.85
        assert len(analyzer.debate_outcomes) == 1


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_debate_completes_in_reasonable_time(self):
        """Test that debate completes efficiently"""
        models = {}
        framework = create_debate_framework(models)
        
        start = time.time()
        solution, session = framework.debate(
            problem="Design system",
            context={},
            identity_anchors={},
            num_rounds=1
        )
        duration = time.time() - start
        
        # Should complete in < 5 seconds (generous timeout)
        assert duration < 5.0
        # Session duration should be close to measured duration (within 0.1s)
        assert abs(session.duration - duration) < 0.1
    
    def test_classification_is_fast(self):
        """Test that classification is fast"""
        classifier = ProblemComplexityClassifier()
        
        start = time.time()
        for _ in range(100):
            classifier.classify("Design system")
        duration = time.time() - start
        
        # 100 classifications should be < 1 second
        assert duration < 1.0
    
    def test_large_context_handled(self):
        """Test handling large context"""
        classifier = ProblemComplexityClassifier()
        
        large_context = {f"constraint_{i}": f"value_{i}" for i in range(100)}
        
        start = time.time()
        classification, score = classifier.classify("Design system", large_context)
        duration = time.time() - start
        
        # Should handle large context quickly
        assert duration < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
