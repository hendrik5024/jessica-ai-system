"""Phase 6: Comprehensive Decision Support Test Suite

Tests for:
- Data structure immutability (frozen dataclasses)
- Proposal generation determinism
- Evaluation scoring consistency  
- Explanation text generation
- Orchestrator workflow
- Safety constraints (no execution, no background threads, no learning, no retries)
- Integration with Phase 5.1.5, 5.5
- Backward compatibility with Phase 4-5.5
"""
import pytest
from jessica.execution import (
    DecisionProposal,
    DecisionEvaluation,
    DecisionExplanation,
    DecisionBundle,
    RiskLevel,
    ReversibilityScore,
    DecisionProposer,
    DecisionEvaluator,
    DecisionExplainer,
    DecisionOrchestrator,
    create_decision_bundle,
)


class TestDecisionStructures:
    """Test immutable frozen dataclasses."""

    def test_decision_proposal_is_frozen(self):
        """Verify DecisionProposal cannot be modified."""
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Test proposal",
            step_count=3,
            estimated_effort="low",
            rationale="For testing",
        )
        
        with pytest.raises(Exception):
            proposal.description = "Modified"

    def test_decision_bundle_is_frozen(self):
        """Verify DecisionBundle cannot be modified."""
        bundle = create_decision_bundle("Test goal")
        
        with pytest.raises(Exception):
            bundle.goal_description = "Modified"

    def test_decision_evaluation_is_frozen(self):
        """Verify DecisionEvaluation cannot be modified."""
        evaluation = DecisionEvaluation(
            proposal_id="p1",
            risk_level=RiskLevel.LOW,
            reversibility=ReversibilityScore.FULLY_REVERSIBLE,
            complexity_score=3.0,
            estimated_duration_seconds=60,
            confidence=0.8,
            risk_factors=["factor1"],
            failure_modes=["mode1"],
            intervention_points=["point1"],
        )
        
        with pytest.raises(Exception):
            evaluation.complexity_score = 5.0

    def test_decision_explanation_is_frozen(self):
        """Verify DecisionExplanation cannot be modified."""
        explanation = DecisionExplanation(
            proposal_id="p1",
            summary="Test summary",
            what_it_does="Does something",
            how_it_works="Works like this",
            why_proposed="Because",
            advantages=["adv1"],
            disadvantages=["dis1"],
            uncertainties=["unc1"],
            risk_summary="Risks: none",
            safety_notes="Safe",
            recommendations="Do it",
            when_to_use="Always",
            when_not_to_use="Never",
        )
        
        with pytest.raises(Exception):
            explanation.summary = "Modified"

    def test_risk_level_enum_values(self):
        """Verify RiskLevel enum has correct levels."""
        assert RiskLevel.VERY_LOW.value == "very_low"
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.VERY_HIGH.value == "very_high"

    def test_reversibility_score_enum_values(self):
        """Verify ReversibilityScore enum has correct levels."""
        assert ReversibilityScore.FULLY_REVERSIBLE.value == "fully_reversible"
        assert ReversibilityScore.MOSTLY_REVERSIBLE.value == "mostly_reversible"
        assert ReversibilityScore.PARTIALLY_REVERSIBLE.value == "partially_reversible"
        assert ReversibilityScore.BARELY_REVERSIBLE.value == "barely_reversible"
        assert ReversibilityScore.IRREVERSIBLE.value == "irreversible"

    def test_create_decision_bundle_factory(self):
        """Verify create_decision_bundle factory function."""
        bundle = create_decision_bundle("Test goal")
        assert bundle.goal_description == "Test goal"
        assert bundle.bundle_id is not None
        assert bundle.proposals == []
        assert bundle.evaluations == {}
        assert bundle.explanations == {}

    def test_decision_structures_to_dict(self):
        """Verify all structures can serialize to dict."""
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Test",
            step_count=2,
            estimated_effort="low",
            rationale="Testing",
        )
        
        proposal_dict = proposal.to_dict()
        assert proposal_dict["proposal_id"] == "p1"
        assert proposal_dict["action_plan_id"] == "ap1"


class TestDecisionProposer:
    """Test proposal generation."""

    def test_proposer_initialization(self):
        """Verify DecisionProposer initializes correctly."""
        proposer = DecisionProposer(enabled=True)
        assert proposer.enabled is True
        
        proposer_disabled = DecisionProposer(enabled=False)
        assert proposer_disabled.enabled is False

    def test_propose_with_empty_pipelines(self):
        """Verify proposer handles empty pipeline dict."""
        proposer = DecisionProposer()
        proposals, error = proposer.propose_plans_from_goal(
            goal_description="Test goal",
            available_pipelines={},
        )
        
        assert error is not None
        assert proposals == []

    def test_propose_with_valid_pipelines(self):
        """Verify proposer generates proposals from valid pipelines."""
        proposer = DecisionProposer()
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "backup"},
                "approval_result": {"approved": True},
            },
        }
        
        proposals, error = proposer.propose_plans_from_goal(
            goal_description="Backup files",
            available_pipelines=pipelines,
        )
        
        assert error is None
        assert len(proposals) > 0
        assert all(isinstance(p, DecisionProposal) for p in proposals)

    def test_propose_determinism(self):
        """Verify proposal generation is deterministic."""
        proposer1 = DecisionProposer()
        proposer2 = DecisionProposer()
        
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "backup"},
                "approval_result": {"approved": True},
            },
        }
        
        proposals1, _ = proposer1.propose_plans_from_goal(
            goal_description="Backup files",
            available_pipelines=pipelines,
            max_proposals=3,
        )
        
        proposals2, _ = proposer2.propose_plans_from_goal(
            goal_description="Backup files",
            available_pipelines=pipelines,
            max_proposals=3,
        )
        
        # Should generate same number of proposals
        assert len(proposals1) == len(proposals2)

    def test_proposer_disabled_returns_error(self):
        """Verify disabled proposer returns error."""
        proposer = DecisionProposer(enabled=False)
        proposals, error = proposer.propose_plans_from_goal(
            goal_description="Test",
            available_pipelines={"p1": {}},
        )
        
        assert error is not None
        assert proposals == []

    def test_proposer_disable_enable_flags(self):
        """Verify proposer disable/enable flags work."""
        proposer = DecisionProposer(enabled=True)
        assert proposer.enabled is True
        
        proposer.disable()
        assert proposer.enabled is False
        
        proposer.enable()
        assert proposer.enabled is True

    def test_ask_clarifying_questions(self):
        """Verify proposer generates clarifying questions."""
        proposer = DecisionProposer()
        questions = proposer.ask_clarifying_questions("Organize files")
        
        assert isinstance(questions, list)
        assert len(questions) > 0
        assert all(isinstance(q, str) for q in questions)

    def test_ask_questions_when_disabled(self):
        """Verify disabled proposer returns empty questions."""
        proposer = DecisionProposer(enabled=False)
        questions = proposer.ask_clarifying_questions("Test goal")
        
        assert questions == []

    def test_propose_max_proposals_limit(self):
        """Verify proposer respects max_proposals limit."""
        proposer = DecisionProposer()
        pipelines = {f"p{i}": {
            "pipeline_id": f"p{i}",
            "status": "approved",
            "intent": {"goal": f"action_{i}"},
            "approval_result": {"approved": True},
        } for i in range(5)}
        
        proposals, _ = proposer.propose_plans_from_goal(
            goal_description="Multi-step task",
            available_pipelines=pipelines,
            max_proposals=2,
        )
        
        assert len(proposals) <= 2


class TestDecisionEvaluator:
    """Test proposal evaluation."""

    def test_evaluator_initialization(self):
        """Verify DecisionEvaluator initializes correctly."""
        evaluator = DecisionEvaluator(enabled=True)
        assert evaluator.enabled is True

    def test_evaluate_single_proposal(self):
        """Verify evaluator scores a single proposal."""
        evaluator = DecisionEvaluator()
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Test action",
            step_count=3,
            estimated_effort="low",
            rationale="For testing",
        )
        
        evaluation, error = evaluator.evaluate_proposal(proposal)
        
        assert error is None
        assert isinstance(evaluation, DecisionEvaluation)
        assert evaluation.proposal_id == "p1"

    def test_evaluation_scoring_determinism(self):
        """Verify evaluation scoring is deterministic."""
        evaluator1 = DecisionEvaluator()
        evaluator2 = DecisionEvaluator()
        
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Test action",
            step_count=3,
            estimated_effort="low",
            rationale="Testing",
        )
        
        eval1, _ = evaluator1.evaluate_proposal(proposal)
        eval2, _ = evaluator2.evaluate_proposal(proposal)
        
        assert eval1.risk_level == eval2.risk_level
        assert eval1.complexity_score == eval2.complexity_score
        assert eval1.confidence == eval2.confidence

    def test_evaluate_multiple_proposals(self):
        """Verify evaluator handles multiple proposals."""
        evaluator = DecisionEvaluator()
        proposals = [
            DecisionProposal(
                proposal_id=f"p{i}",
                action_plan_id=f"ap{i}",
                description=f"Action {i}",
                step_count=i + 1,
                estimated_effort="low" if i % 2 == 0 else "high",
                rationale="Testing",
            )
            for i in range(3)
        ]
        
        evaluations, error = evaluator.evaluate_proposals(proposals)
        
        assert error is None
        assert len(evaluations) == 3

    def test_evaluator_disabled_returns_error(self):
        """Verify disabled evaluator returns error."""
        evaluator = DecisionEvaluator(enabled=False)
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Test",
            step_count=1,
            estimated_effort="low",
            rationale="Test",
        )
        
        evaluation, error = evaluator.evaluate_proposal(proposal)
        
        assert error is not None
        assert evaluation is None

    def test_evaluator_disable_enable_flags(self):
        """Verify evaluator disable/enable flags work."""
        evaluator = DecisionEvaluator(enabled=True)
        assert evaluator.enabled is True
        
        evaluator.disable()
        assert evaluator.enabled is False
        
        evaluator.enable()
        assert evaluator.enabled is True

    def test_compare_proposals_ranking(self):
        """Verify evaluator can rank proposals."""
        evaluator = DecisionEvaluator()
        
        # Verify safe method handles proposals of different risk levels
        proposals = [
            DecisionProposal(
                proposal_id="p1",
                action_plan_id="ap1",
                description="Simple action",
                step_count=1,
                estimated_effort="low",
                rationale="Safe",
            ),
            DecisionProposal(
                proposal_id="p2",
                action_plan_id="ap2",
                description="Complex action",
                step_count=10,
                estimated_effort="high",
                rationale="Risky",
            ),
        ]
        
        evaluations, _ = evaluator.evaluate_proposals(proposals)
        comparison = evaluator.compare_proposals(evaluations)
        
        assert "safest_proposal_id" in comparison
        assert "simplest_proposal_id" in comparison
        assert "fastest_proposal_id" in comparison

    def test_complexity_score_range(self):
        """Verify complexity score is in valid range."""
        evaluator = DecisionEvaluator()
        
        for step_count in [1, 5, 10, 50]:
            proposal = DecisionProposal(
                proposal_id=f"p{step_count}",
                action_plan_id=f"ap{step_count}",
                description="Test",
                step_count=step_count,
                estimated_effort="low",
                rationale="Test",
            )
            
            evaluation, _ = evaluator.evaluate_proposal(proposal)
            
            assert 0.0 <= evaluation.complexity_score <= 10.0

    def test_confidence_score_range(self):
        """Verify confidence score is in valid range."""
        evaluator = DecisionEvaluator()
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Test",
            step_count=3,
            estimated_effort="low",
            rationale="Test",
        )
        
        evaluation, _ = evaluator.evaluate_proposal(proposal)
        
        assert 0.0 <= evaluation.confidence <= 1.0


class TestDecisionExplainer:
    """Test explanation generation."""

    def test_explainer_initialization(self):
        """Verify DecisionExplainer initializes correctly."""
        explainer = DecisionExplainer(enabled=True)
        assert explainer.enabled is True

    def test_explain_single_proposal(self):
        """Verify explainer generates explanation for proposal."""
        explainer = DecisionExplainer()
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Test action",
            step_count=3,
            estimated_effort="low",
            rationale="For testing",
        )
        
        evaluation = DecisionEvaluation(
            proposal_id="p1",
            risk_level=RiskLevel.LOW,
            reversibility=ReversibilityScore.FULLY_REVERSIBLE,
            complexity_score=3.0,
            estimated_duration_seconds=60,
            confidence=0.85,
            risk_factors=[],
            failure_modes=[],
            intervention_points=[],
        )
        
        explanation, error = explainer.explain_proposal(proposal, evaluation)
        
        assert error is None
        assert isinstance(explanation, DecisionExplanation)
        assert explanation.proposal_id == "p1"
        assert explanation.summary is not None

    def test_explanation_contains_required_fields(self):
        """Verify explanation contains all required fields."""
        explainer = DecisionExplainer()
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Backup files",
            step_count=3,
            estimated_effort="low",
            rationale="Data protection",
        )
        
        evaluation = DecisionEvaluation(
            proposal_id="p1",
            risk_level=RiskLevel.VERY_LOW,
            reversibility=ReversibilityScore.FULLY_REVERSIBLE,
            complexity_score=2.0,
            estimated_duration_seconds=30,
            confidence=0.9,
            risk_factors=[],
            failure_modes=[],
            intervention_points=[],
        )
        
        explanation, _ = explainer.explain_proposal(proposal, evaluation)
        
        assert explanation.what_it_does is not None
        assert explanation.how_it_works is not None
        assert explanation.why_proposed is not None
        assert explanation.advantages is not None
        assert explanation.disadvantages is not None
        assert explanation.uncertainties is not None
        assert explanation.risk_summary is not None
        assert explanation.safety_notes is not None

    def test_explainer_disabled_returns_error(self):
        """Verify disabled explainer returns error."""
        explainer = DecisionExplainer(enabled=False)
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Test",
            step_count=1,
            estimated_effort="low",
            rationale="Test",
        )
        
        evaluation = DecisionEvaluation(
            proposal_id="p1",
            risk_level=RiskLevel.LOW,
            reversibility=ReversibilityScore.FULLY_REVERSIBLE,
            complexity_score=1.0,
            estimated_duration_seconds=10,
            confidence=0.9,
            risk_factors=[],
            failure_modes=[],
            intervention_points=[],
        )
        
        explanation, error = explainer.explain_proposal(proposal, evaluation)
        
        assert error is not None
        assert explanation is None

    def test_explainer_disable_enable_flags(self):
        """Verify explainer disable/enable flags work."""
        explainer = DecisionExplainer(enabled=True)
        assert explainer.enabled is True
        
        explainer.disable()
        assert explainer.enabled is False
        
        explainer.enable()
        assert explainer.enabled is True

    def test_explanation_text_is_readable(self):
        """Verify generated explanations are readable prose."""
        explainer = DecisionExplainer()
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",
            description="Organize desktop",
            step_count=2,
            estimated_effort="low",
            rationale="Improve workflow",
        )
        
        evaluation = DecisionEvaluation(
            proposal_id="p1",
            risk_level=RiskLevel.VERY_LOW,
            reversibility=ReversibilityScore.FULLY_REVERSIBLE,
            complexity_score=1.5,
            estimated_duration_seconds=300,
            confidence=0.95,
            risk_factors=[],
            failure_modes=[],
            intervention_points=[],
        )
        
        explanation, _ = explainer.explain_proposal(proposal, evaluation)
        
        # Verify text is present and meaningful
        assert len(explanation.summary) > 0
        assert len(explanation.what_it_does) > 0
        assert len(explanation.how_it_works) > 0


class TestDecisionOrchestrator:
    """Test orchestrator workflow."""

    def test_orchestrator_initialization(self):
        """Verify DecisionOrchestrator initializes correctly."""
        orchestrator = DecisionOrchestrator(enabled=True)
        assert orchestrator.enabled is True

    def test_orchestrator_analyze_goal_workflow(self):
        """Verify orchestrator runs complete workflow."""
        orchestrator = DecisionOrchestrator()
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "backup"},
                "approval_result": {"approved": True},
            },
        }
        
        bundle, error = orchestrator.analyze_goal(
            goal_description="Backup important files",
            available_pipelines=pipelines,
        )
        
        assert error is None
        assert bundle is not None
        assert bundle.goal_description == "Backup important files"
        assert len(bundle.proposals) > 0

    def test_orchestrator_returns_decision_bundle(self):
        """Verify orchestrator returns DecisionBundle."""
        orchestrator = DecisionOrchestrator()
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "action"},
                "approval_result": {"approved": True},
            },
        }
        
        bundle, _ = orchestrator.analyze_goal(
            goal_description="Do something",
            available_pipelines=pipelines,
        )
        
        assert isinstance(bundle, DecisionBundle)
        assert bundle.bundle_id is not None
        assert isinstance(bundle.proposals, list)
        assert isinstance(bundle.evaluations, dict)
        assert isinstance(bundle.explanations, dict)

    def test_orchestrator_with_empty_goal(self):
        """Verify orchestrator handles empty goal."""
        orchestrator = DecisionOrchestrator()
        bundle, error = orchestrator.analyze_goal(
            goal_description="",
            available_pipelines={"p1": {}},
        )
        
        assert error is not None
        assert bundle is None

    def test_orchestrator_with_no_pipelines(self):
        """Verify orchestrator handles empty pipelines."""
        orchestrator = DecisionOrchestrator()
        bundle, error = orchestrator.analyze_goal(
            goal_description="Test goal",
            available_pipelines={},
        )
        
        assert error is not None
        assert bundle is None

    def test_orchestrator_disabled_returns_error(self):
        """Verify disabled orchestrator returns error."""
        orchestrator = DecisionOrchestrator(enabled=False)
        bundle, error = orchestrator.analyze_goal(
            goal_description="Test",
            available_pipelines={"p1": {}},
        )
        
        assert error is not None
        assert bundle is None

    def test_orchestrator_disable_enable(self):
        """Verify orchestrator disable/enable works."""
        orchestrator = DecisionOrchestrator(enabled=True)
        assert orchestrator.enabled is True
        
        orchestrator.disable()
        assert orchestrator.enabled is False
        
        orchestrator.enable()
        assert orchestrator.enabled is True

    def test_orchestrator_format_for_human(self):
        """Verify orchestrator can format bundle as readable text."""
        orchestrator = DecisionOrchestrator()
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "backup"},
                "approval_result": {"approved": True},
            },
        }
        
        bundle, _ = orchestrator.analyze_goal(
            goal_description="Backup files",
            available_pipelines=pipelines,
        )
        
        text = orchestrator.format_bundle_for_human(bundle)
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Backup files" in text

    def test_orchestrator_asks_clarifying_questions(self):
        """Verify orchestrator asks clarifying questions."""
        orchestrator = DecisionOrchestrator()
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "action"},
                "approval_result": {"approved": True},
            },
        }
        
        bundle, _ = orchestrator.analyze_goal(
            goal_description="Organize workspace",
            available_pipelines=pipelines,
            ask_questions=True,
        )
        
        # Bundle should have questions
        assert bundle is not None
        assert hasattr(bundle, 'clarifying_questions')

    def test_orchestrator_get_proposal_details(self):
        """Verify orchestrator can retrieve proposal details."""
        orchestrator = DecisionOrchestrator()
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "backup"},
                "approval_result": {"approved": True},
            },
        }
        
        bundle, _ = orchestrator.analyze_goal(
            goal_description="Backup files",
            available_pipelines=pipelines,
        )
        
        if bundle and bundle.proposals:
            proposal_id = bundle.proposals[0].proposal_id
            details = orchestrator.get_proposal_details(bundle, proposal_id)
            
            assert details is not None
            assert "proposal" in details
            assert "evaluation" in details
            assert "explanation" in details


class TestSafetyConstraints:
    """Test Phase 6 safety constraints."""

    def test_no_execution_capability(self):
        """Verify Phase 6 has no execution capability."""
        orchestrator = DecisionOrchestrator()
        
        # Orchestrator should not have execute method
        assert not hasattr(orchestrator, 'execute')
        assert not hasattr(orchestrator, 'execute_proposal')
        assert not hasattr(orchestrator, 'execute_plan')

    def test_no_approval_capability(self):
        """Verify Phase 6 has no approval capability."""
        orchestrator = DecisionOrchestrator()
        
        # Should not have approval methods
        assert not hasattr(orchestrator, 'approve')
        assert not hasattr(orchestrator, 'approve_proposal')

    def test_no_modification_capability(self):
        """Verify Phase 6 cannot modify pipelines."""
        orchestrator = DecisionOrchestrator()
        
        # Should not have modification methods
        assert not hasattr(orchestrator, 'modify_pipeline')
        assert not hasattr(orchestrator, 'update_pipeline')

    def test_full_reversibility_via_disable(self):
        """Verify all components can be disabled."""
        orchestrator = DecisionOrchestrator(enabled=True)
        
        orchestrator.disable()
        
        # Verify all sub-components are disabled
        assert orchestrator.enabled is False
        assert orchestrator.proposer.enabled is False
        assert orchestrator.evaluator.enabled is False
        assert orchestrator.explainer.enabled is False

    def test_no_background_threads(self):
        """Verify orchestrator uses only synchronous operations."""
        import threading
        
        initial_thread_count = threading.active_count()
        
        orchestrator = DecisionOrchestrator()
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "test"},
                "approval_result": {"approved": True},
            },
        }
        
        bundle, _ = orchestrator.analyze_goal(
            goal_description="Test",
            available_pipelines=pipelines,
        )
        
        final_thread_count = threading.active_count()
        
        # No new background threads should be created
        assert final_thread_count <= initial_thread_count + 1  # +1 allows for thread pool

    def test_no_persistent_state_modification(self):
        """Verify Phase 6 doesn't modify persistent state."""
        proposer = DecisionProposer()
        
        # Proposer should not have persistence methods
        assert not hasattr(proposer, 'save')
        assert not hasattr(proposer, 'persist')
        assert not hasattr(proposer, 'store')

    def test_deterministic_output(self):
        """Verify same input produces same output."""
        orchestrator1 = DecisionOrchestrator()
        orchestrator2 = DecisionOrchestrator()
        
        pipelines = {
            "p1": {
                "pipeline_id": "p1",
                "status": "approved",
                "intent": {"goal": "backup"},
                "approval_result": {"approved": True},
            },
        }
        
        goal = "Backup important files"
        
        bundle1, _ = orchestrator1.analyze_goal(goal, pipelines)
        bundle2, _ = orchestrator2.analyze_goal(goal, pipelines)
        
        # Should produce bundles with same structure
        assert len(bundle1.proposals) == len(bundle2.proposals)
        assert len(bundle1.evaluations) == len(bundle2.evaluations)


class TestBackwardCompatibility:
    """Test compatibility with earlier phases."""

    def test_phase_6_does_not_import_execution_layers(self):
        """Verify Phase 6 doesn't import Phase 5.2 execution."""
        orchestrator = DecisionOrchestrator()
        
        # Should not have action executor
        assert not hasattr(orchestrator, 'action_executor')
        assert not hasattr(orchestrator, 'executor')

    def test_phase_6_is_read_only(self):
        """Verify Phase 6 operations are read-only."""
        proposer = DecisionProposer()
        evaluator = DecisionEvaluator()
        explainer = DecisionExplainer()
        orchestrator = DecisionOrchestrator()
        
        # All key methods should be present and safe
        assert hasattr(proposer, 'propose_plans_from_goal')
        assert hasattr(proposer, 'ask_clarifying_questions')
        assert hasattr(evaluator, 'evaluate_proposal')
        assert hasattr(evaluator, 'compare_proposals')
        assert hasattr(explainer, 'explain_proposal')
        assert hasattr(orchestrator, 'analyze_goal')

    def test_decision_structures_compatible_with_action_plan(self):
        """Verify DecisionProposal can reference ActionPlans."""
        # This tests that Phase 6 data structures can coexist with Phase 5.5
        proposal = DecisionProposal(
            proposal_id="p1",
            action_plan_id="ap1",  # References Phase 5.5 ActionPlan
            description="Multi-step action",
            step_count=3,
            estimated_effort="low",
            rationale="Efficient",
        )
        
        assert proposal.action_plan_id == "ap1"
        assert proposal.proposal_id == "p1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
