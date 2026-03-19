"""
Tests for Safe Self-Improvement Loop

Validates:
- Change proposal generation
- Simulation and offline evaluation
- Human approval gates
- Deployment with automatic rollback
- Complete end-to-end cycle
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from jessica.unified_world_model.safe_self_improvement import (
    ChangeType, ChangeRiskLevel, ChangeProposal,
    ChangeProposalBatch, ChangeProposalGenerator,
    SimulationResult, SimulationEnvironment,
    ApprovalStatus, ApprovalDecision, ApprovalGate,
    DeploymentRecord, RollbackDetector, DeploymentManager,
    SafeSelfImprovementLoop
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_system():
    """Mock AGI system for testing."""
    system = Mock()
    system.CausalStateManager = Mock()
    system.PlanValidator = Mock()
    system.TransferConsultant = Mock()
    system.ContinualLearningEngine = Mock()
    return system


@pytest.fixture
def proposal_generator():
    """Proposal generator instance."""
    return ChangeProposalGenerator()


@pytest.fixture
def simulation_env():
    """Simulation environment instance."""
    return SimulationEnvironment()


@pytest.fixture
def approval_gate():
    """Approval gate instance."""
    return ApprovalGate()


@pytest.fixture
def deployment_manager():
    """Deployment manager instance."""
    return DeploymentManager()


@pytest.fixture
def sample_proposal():
    """Sample change proposal."""
    return ChangeProposal(
        proposal_id="test_prop_1",
        change_type=ChangeType.PARAMETER_TUNING,
        title="Test Parameter Adjustment",
        description="Test proposal for validation threshold",
        affected_components=["PlanValidator"],
        affected_phases=[6],
        current_value=0.70,
        proposed_value=0.75,
        parameter_name="validation_threshold",
        motivation="Testing proposal generation",
        expected_improvement="Improve validation accuracy",
        improvement_metric="validation_accuracy",
        estimated_improvement=0.05,
        risk_level=ChangeRiskLevel.LOW,
        potential_downsides=["Minor performance overhead"],
        affected_capabilities=["planning"],
        rollback_difficulty="easy",
        proposed_by="test"
    )


@pytest.fixture
def sample_simulation_result(sample_proposal):
    """Sample simulation result."""
    return SimulationResult(
        proposal_id=sample_proposal.proposal_id,
        simulation_id="sim_test_1",
        performance_before={"accuracy": 0.85, "consistency": 0.95},
        performance_after={"accuracy": 0.87, "consistency": 0.96},
        performance_delta={"accuracy": 0.02, "consistency": 0.01},
        overall_score_before=0.88,
        overall_score_after=0.91,
        score_improvement=0.03,
        safety_violations=0,
        causal_drift=0.02,
        regression_detected=False,
        affected_metrics=["accuracy", "consistency"],
        passed_baseline=True,
        passed_improvement=True,
        safe_to_deploy=True,
        environment="synthetic_queries",
        duration_seconds=0.5
    )


# ============================================================================
# TEST: Change Proposal Generation
# ============================================================================

class TestProposalGeneration:
    """Tests for generating change proposals."""
    
    def test_generator_creation(self, proposal_generator):
        """Test proposal generator initialization."""
        assert proposal_generator.generated_count == 0
        assert proposal_generator.approved_count == 0
        assert len(proposal_generator.change_history) == 0
    
    def test_generate_proposal_batch(self, proposal_generator, mock_system):
        """Test generating batch of proposals."""
        statistics = {
            "prediction_errors": [1, 2, 3, 4, 5],  # High error rate
            "total_predictions": 20,
            "transfer_consultation_rate": 0.80,
            "knowledge_gaps": ["physics", "biology"],
            "meta_learner_stats": None,
            "safety_violations": 0,
            "integration_quality": 3.5
        }
        
        batch = proposal_generator.analyze_system_and_propose(mock_system, statistics)
        
        assert batch.total_count > 0
        assert len(batch.proposals) > 0
        assert all(isinstance(p, ChangeProposal) for p in batch.proposals)
    
    def test_proposal_contains_required_fields(self, proposal_generator, mock_system):
        """Test that generated proposals have all required fields."""
        statistics = {
            "prediction_errors": [],
            "transfer_consultation_rate": 0.90,
            "knowledge_gaps": [],
            "meta_learner_stats": None,
            "safety_violations": 0,
            "integration_quality": 3.5
        }
        
        batch = proposal_generator.analyze_system_and_propose(mock_system, statistics)
        
        for proposal in batch.proposals:
            assert proposal.proposal_id
            assert proposal.change_type
            assert proposal.title
            assert proposal.affected_components
            assert proposal.current_value is not None or proposal.change_type == ChangeType.KNOWLEDGE_EXPANSION
            assert proposal.estimated_improvement >= 0.0
            assert proposal.risk_level
    
    def test_parameter_tuning_proposal(self, proposal_generator, mock_system):
        """Test parameter tuning proposal generation."""
        statistics = {
            "prediction_errors": list(range(25)),  # High error rate (>0.2)
            "total_predictions": 100,
            "transfer_consultation_rate": 0.95,
            "knowledge_gaps": [],
            "meta_learner_stats": None,
            "safety_violations": 0,
            "integration_quality": 3.5
        }
        
        batch = proposal_generator.analyze_system_and_propose(mock_system, statistics)
        
        # Should have parameter tuning proposal
        param_proposals = [p for p in batch.proposals if p.change_type == ChangeType.PARAMETER_TUNING]
        assert len(param_proposals) > 0
        
        prop = param_proposals[0]
        assert prop.parameter_name == "validation_threshold"
        assert prop.proposed_value > prop.current_value
    
    def test_safety_improvement_proposal(self, proposal_generator, mock_system):
        """Test safety improvement proposal generation."""
        statistics = {
            "prediction_errors": [],
            "transfer_consultation_rate": 0.95,
            "knowledge_gaps": [],
            "meta_learner_stats": None,
            "safety_violations": 5,  # Violations detected
            "integration_quality": 3.5
        }
        
        batch = proposal_generator.analyze_system_and_propose(mock_system, statistics)
        
        safety_proposals = [p for p in batch.proposals if p.change_type == ChangeType.SAFETY_IMPROVEMENT]
        assert len(safety_proposals) > 0
        assert all(p.risk_level == ChangeRiskLevel.TRIVIAL for p in safety_proposals)
    
    def test_proposal_serialization(self, sample_proposal):
        """Test that proposals can be serialized to dict."""
        prop_dict = sample_proposal.to_dict()
        
        assert prop_dict["proposal_id"] == sample_proposal.proposal_id
        assert prop_dict["change_type"] == "parameter_tuning"
        assert prop_dict["risk_level"] == "LOW"
        assert prop_dict["estimated_improvement"] == 0.05


# ============================================================================
# TEST: Simulation and Offline Evaluation
# ============================================================================

class TestSimulationEnvironment:
    """Tests for simulation and evaluation."""
    
    def test_environment_creation(self, simulation_env):
        """Test simulation environment initialization."""
        assert simulation_env.simulations_run == 0
        assert len(simulation_env.results_cache) == 0
    
    def test_create_system_copy(self, simulation_env, mock_system):
        """Test creating isolated copy of system."""
        copy = simulation_env.create_copy_of_system(mock_system)
        
        # Should be a different object
        assert copy is not mock_system
    
    def test_evaluate_proposal_basic(self, simulation_env, mock_system, sample_proposal):
        """Test basic proposal evaluation."""
        result = simulation_env.evaluate_proposal(mock_system, sample_proposal)
        
        assert result.proposal_id == sample_proposal.proposal_id
        assert result.simulation_id
        assert result.safe_to_deploy is not None
        assert result.performance_before is not None
        assert result.performance_after is not None
    
    def test_simulation_detects_regression(self, simulation_env, mock_system):
        """Test that simulation detects performance regressions."""
        proposal = ChangeProposal(
            proposal_id="bad_change",
            change_type=ChangeType.PARAMETER_TUNING,
            title="Bad Parameter Change",
            description="This should cause regression",
            affected_components=["PlanValidator"],
            affected_phases=[6],
            current_value=0.70,
            proposed_value=0.95,  # Extreme value
            parameter_name="validation_threshold",
            motivation="Testing regression detection",
            expected_improvement="None - testing",
            improvement_metric="accuracy",
            estimated_improvement=-0.20,  # Expected to be negative
            risk_level=ChangeRiskLevel.HIGH,
            potential_downsides=["High regression risk"],
            affected_capabilities=["planning"],
            rollback_difficulty="medium",
            proposed_by="test"
        )
        
        result = simulation_env.evaluate_proposal(mock_system, proposal)
        
        # With extreme parameter value, should either show no improvement or mark as unsafe
        # The result shows no improvement and confidence is reduced
        assert result.passed_improvement == False or result.confidence < 0.85
    
    def test_simulation_result_to_dict(self, sample_simulation_result):
        """Test serialization of simulation results."""
        result_dict = sample_simulation_result.to_dict()
        
        assert result_dict["proposal_id"]
        assert "overall_improvement" in result_dict
        assert "safe_to_deploy" in result_dict
        assert result_dict["safe_to_deploy"] == True
    
    def test_simulation_metrics_calculation(self, simulation_env):
        """Test calculation of overall score."""
        metrics = {
            "accuracy": 0.90,
            "causal_consistency": 0.95,
            "transfer_rate": 0.85,
            "validation_rate": 0.80,
            "latency_ms": 100
        }
        
        score = simulation_env._calculate_overall_score(metrics)
        
        assert 0.0 <= score <= 1.0
        # Good metrics should score reasonably well
        assert score > 0.3


# ============================================================================
# TEST: Human Approval Gate
# ============================================================================

class TestApprovalGate:
    """Tests for human approval workflow."""
    
    def test_gate_creation(self, approval_gate):
        """Test approval gate initialization."""
        assert approval_gate.auto_approved_count == 0
        assert approval_gate.human_approved_count == 0
        assert approval_gate.rejected_count == 0
    
    def test_auto_approve_safety_improvement(self, approval_gate, sample_proposal, sample_simulation_result):
        """Test auto-approval of safety improvements."""
        # Make it a safety improvement with trivial risk
        proposal = ChangeProposal(
            proposal_id="safety_trivial",
            change_type=ChangeType.SAFETY_IMPROVEMENT,
            title="Trivial Safety Improvement",
            description="Simple safety check",
            affected_components=["CausalStateManager"],
            affected_phases=[6],
            current_value="reactive",
            proposed_value="proactive",
            parameter_name="safety_check_mode",
            motivation="Improve safety",
            expected_improvement="Better safety",
            improvement_metric="safety_violations",
            estimated_improvement=0.50,
            risk_level=ChangeRiskLevel.TRIVIAL,
            potential_downsides=[],
            affected_capabilities=["safety"],
            rollback_difficulty="easy",
            proposed_by="safety_monitor"
        )
        
        result = SimulationResult(
            proposal_id=proposal.proposal_id,
            simulation_id="sim_1",
            performance_before={"safety": 0.90},
            performance_after={"safety": 0.95},
            performance_delta={"safety": 0.05},
            overall_score_before=0.85,
            overall_score_after=0.87,
            score_improvement=0.02,
            safety_violations=0,
            causal_drift=0.01,
            regression_detected=False,
            affected_metrics=["safety"],
            passed_baseline=True,
            passed_improvement=True,
            safe_to_deploy=True,
            environment="synthetic_queries",
            duration_seconds=0.3
        )
        
        status = approval_gate.submit_for_approval(proposal, result)
        
        assert status == ApprovalStatus.APPROVED
        assert approval_gate.auto_approved_count == 1
    
    def test_auto_approve_performance_optimization(self, approval_gate):
        """Test auto-approval of performance optimizations."""
        proposal = ChangeProposal(
            proposal_id="perf_opt_1",
            change_type=ChangeType.PERFORMANCE_OPTIMIZATION,
            title="Cache Optimization",
            description="Faster caching",
            affected_components=["TransferConsultant"],
            affected_phases=[2],
            current_value="naive_cache",
            proposed_value="lru_cache",
            parameter_name="caching_strategy",
            motivation="Improve speed",
            expected_improvement="Lower latency",
            improvement_metric="latency_ms",
            estimated_improvement=0.20,
            risk_level=ChangeRiskLevel.LOW,
            potential_downsides=["Memory overhead"],
            affected_capabilities=["speed"],
            rollback_difficulty="easy",
            proposed_by="optimizer"
        )
        
        result = SimulationResult(
            proposal_id=proposal.proposal_id,
            simulation_id="sim_2",
            performance_before={"latency_ms": 150},
            performance_after={"latency_ms": 120},
            performance_delta={"latency_ms": -30},
            overall_score_before=0.80,
            overall_score_after=0.85,
            score_improvement=0.05,
            safety_violations=0,
            causal_drift=0.0,
            regression_detected=False,
            affected_metrics=["latency"],
            passed_baseline=True,
            passed_improvement=True,
            safe_to_deploy=True,
            environment="synthetic_queries",
            duration_seconds=0.4
        )
        
        status = approval_gate.submit_for_approval(proposal, result)
        
        assert status == ApprovalStatus.APPROVED
        assert approval_gate.auto_approved_count >= 1
    
    def test_queue_for_human_review(self, approval_gate, sample_proposal, sample_simulation_result):
        """Test queueing proposal for human review."""
        status = approval_gate.submit_for_approval(sample_proposal, sample_simulation_result)
        
        assert status == ApprovalStatus.UNDER_REVIEW
        assert len(approval_gate.approval_queue) > 0
    
    def test_generate_review_summary(self, approval_gate, sample_proposal, sample_simulation_result):
        """Test generating summary for human reviewer."""
        summary = approval_gate.generate_review_summary(sample_proposal, sample_simulation_result)
        
        assert summary["title"] == sample_proposal.title
        assert "simulation_results" in summary
        assert "reviewer_questions" in summary
        assert len(summary["reviewer_questions"]) > 0
    
    def test_human_decision_approval(self, approval_gate):
        """Test recording human approval decision."""
        decision = approval_gate.human_decision(
            proposal_id="test_prop",
            decision=ApprovalStatus.APPROVED,
            reviewer_id="expert_1",
            reasoning="Looks good based on simulation data"
        )
        
        assert decision.proposal_id == "test_prop"
        assert decision.decision == ApprovalStatus.APPROVED
        assert decision.reviewer_id == "expert_1"
        assert approval_gate.human_approved_count == 1
    
    def test_human_decision_rejection(self, approval_gate):
        """Test recording human rejection."""
        decision = approval_gate.human_decision(
            proposal_id="bad_prop",
            decision=ApprovalStatus.REJECTED,
            reviewer_id="expert_1",
            reasoning="Potential downsides outweigh benefits"
        )
        
        assert decision.decision == ApprovalStatus.REJECTED
        assert approval_gate.rejected_count == 1
    
    def test_decision_with_conditions(self, approval_gate):
        """Test approval with conditions."""
        decision = approval_gate.human_decision(
            proposal_id="conditional_prop",
            decision=ApprovalStatus.APPROVED,
            reviewer_id="expert_2",
            reasoning="Approved with conditions",
            conditions=["Only deploy during low-load periods", "Monitor for 24 hours"]
        )
        
        assert len(decision.conditions) == 2
        assert "low-load" in decision.conditions[0]


# ============================================================================
# TEST: Deployment and Rollback
# ============================================================================

class TestDeploymentAndRollback:
    """Tests for deployment and automatic rollback."""
    
    def test_deployment_record_creation(self):
        """Test creating deployment record."""
        deployment = DeploymentRecord(
            proposal_id="prop_1",
            deployment_id="deploy_1",
            change_type=ChangeType.PARAMETER_TUNING,
            system_state_hash="abc123",
            baseline_metrics={"accuracy": 0.85},
            deployed_at=datetime.now(),
            deployed_by="test",
            active=True
        )
        
        assert deployment.proposal_id == "prop_1"
        assert deployment.active == True
        assert deployment.needs_rollback == False
    
    def test_rollback_detector_creation(self):
        """Test rollback detector initialization."""
        detector = RollbackDetector()
        
        assert detector.degradation_threshold == 0.10
        assert detector.regression_threshold == 0.05
        assert len(detector.monitored_deployments) == 0
    
    def test_rollback_detector_monitors_deployment(self):
        """Test monitoring deployment."""
        detector = RollbackDetector()
        deployment = DeploymentRecord(
            proposal_id="prop_1",
            deployment_id="deploy_1",
            change_type=ChangeType.PARAMETER_TUNING,
            system_state_hash="abc123",
            baseline_metrics={"accuracy": 0.85, "consistency": 0.95},
            deployed_at=datetime.now(),
            deployed_by="test",
            active=True
        )
        
        detector.monitor_deployment(deployment)
        
        assert len(detector.monitored_deployments) == 1
        assert detector.monitored_deployments[0] == deployment
    
    def test_detect_degradation_above_threshold(self):
        """Test detection of degradation above threshold."""
        detector = RollbackDetector()
        deployment = DeploymentRecord(
            proposal_id="prop_1",
            deployment_id="deploy_1",
            change_type=ChangeType.PARAMETER_TUNING,
            system_state_hash="abc123",
            baseline_metrics={
                "accuracy": 0.85,
                "causal_consistency": 0.95,
                "planning_success_rate": 0.88
            },
            deployed_at=datetime.now(),
            deployed_by="test",
            active=True
        )
        
        # Current metrics show significant degradation
        current_metrics = {
            "accuracy": 0.75,  # 10% drop
            "causal_consistency": 0.85,  # 10% drop
            "planning_success_rate": 0.78,  # 10% drop
        }
        
        should_rollback, reason = detector.check_for_degradation(deployment, current_metrics)
        
        assert should_rollback == True
        assert reason is not None
    
    def test_no_rollback_for_small_degradation(self):
        """Test that small degradation doesn't trigger rollback."""
        detector = RollbackDetector()
        deployment = DeploymentRecord(
            proposal_id="prop_1",
            deployment_id="deploy_1",
            change_type=ChangeType.PARAMETER_TUNING,
            system_state_hash="abc123",
            baseline_metrics={
                "accuracy": 0.85,
                "causal_consistency": 0.95,
                "planning_success_rate": 0.88
            },
            deployed_at=datetime.now(),
            deployed_by="test",
            active=True
        )
        
        # Slight improvement
        current_metrics = {
            "accuracy": 0.86,  # Small improvement
            "causal_consistency": 0.95,
            "planning_success_rate": 0.89,
        }
        
        should_rollback, reason = detector.check_for_degradation(deployment, current_metrics)
        
        assert should_rollback == False
    
    def test_detect_safety_violation_increase(self):
        """Test detection of increased safety violations."""
        detector = RollbackDetector()
        deployment = DeploymentRecord(
            proposal_id="prop_1",
            deployment_id="deploy_1",
            change_type=ChangeType.PARAMETER_TUNING,
            system_state_hash="abc123",
            baseline_metrics={
                "accuracy": 0.85,
                "causal_consistency": 0.95,
                "planning_success_rate": 0.88,
                "safety_violations": 0
            },
            deployed_at=datetime.now(),
            deployed_by="test",
            active=True
        )
        
        # Violations increased
        current_metrics = {
            "accuracy": 0.85,
            "causal_consistency": 0.95,
            "planning_success_rate": 0.88,
            "safety_violations": 3
        }
        
        should_rollback, reason = detector.check_for_degradation(deployment, current_metrics)
        
        assert should_rollback == True
        assert "safety" in reason.lower()
    
    def test_trigger_rollback(self):
        """Test executing rollback."""
        detector = RollbackDetector()
        deployment = DeploymentRecord(
            proposal_id="prop_1",
            deployment_id="deploy_1",
            change_type=ChangeType.PARAMETER_TUNING,
            system_state_hash="abc123",
            baseline_metrics={"accuracy": 0.85},
            deployed_at=datetime.now(),
            deployed_by="test",
            active=True
        )
        
        rollback_fn = Mock()
        success = detector.trigger_rollback(deployment, "Test rollback", rollback_fn)
        
        assert success == True
        assert deployment.needs_rollback == True
        assert deployment.active == False
        assert detector.rollback_count == 1
        rollback_fn.assert_called_once()
    
    def test_deployment_manager_creation(self, deployment_manager):
        """Test deployment manager initialization."""
        assert deployment_manager.deployed_count == 0
        assert len(deployment_manager.deployments) == 0
    
    def test_deploy_change(self, deployment_manager, sample_proposal, mock_system):
        """Test deploying approved change."""
        apply_fn = Mock()
        
        deployment = deployment_manager.deploy_change(sample_proposal, apply_fn)
        
        assert deployment.proposal_id == sample_proposal.proposal_id
        assert deployment.active == True
        assert deployment_manager.deployed_count == 1
        apply_fn.assert_called_once()


# ============================================================================
# TEST: Complete Improvement Cycle
# ============================================================================

class TestSafeSelfImprovementLoop:
    """Tests for complete self-improvement loop."""
    
    def test_loop_creation(self, mock_system, approval_gate, simulation_env, deployment_manager):
        """Test creating improvement loop."""
        loop = SafeSelfImprovementLoop(
            system=mock_system,
            approval_gate=approval_gate,
            simulation_env=simulation_env,
            deployment_manager=deployment_manager
        )
        
        assert loop.improvement_cycles == 0
        assert loop.total_proposals == 0
    
    def test_run_improvement_cycle(self, mock_system, approval_gate, simulation_env, deployment_manager):
        """Test running complete improvement cycle."""
        loop = SafeSelfImprovementLoop(
            system=mock_system,
            approval_gate=approval_gate,
            simulation_env=simulation_env,
            deployment_manager=deployment_manager
        )
        
        statistics = {
            "prediction_errors": [1, 2, 3, 4, 5],
            "total_predictions": 20,
            "transfer_consultation_rate": 0.80,
            "knowledge_gaps": [],
            "meta_learner_stats": None,
            "safety_violations": 1,
            "integration_quality": 3.5
        }
        
        report = loop.run_improvement_cycle(statistics)
        
        assert report["cycle"] == 1
        assert report["proposals_generated"] > 0
        assert report["proposals_approved"] >= 0
        assert loop.improvement_cycles == 1
    
    def test_multiple_cycles(self, mock_system, approval_gate, simulation_env, deployment_manager):
        """Test running multiple improvement cycles."""
        loop = SafeSelfImprovementLoop(
            system=mock_system,
            approval_gate=approval_gate,
            simulation_env=simulation_env,
            deployment_manager=deployment_manager
        )
        
        statistics = {
            "prediction_errors": [],
            "total_predictions": 100,
            "transfer_consultation_rate": 0.95,
            "knowledge_gaps": [],
            "meta_learner_stats": None,
            "safety_violations": 0,
            "integration_quality": 4.5
        }
        
        for _ in range(3):
            loop.run_improvement_cycle(statistics)
        
        assert loop.improvement_cycles == 3
    
    def test_handle_detected_problem(self, mock_system, approval_gate, simulation_env, deployment_manager):
        """Test handling detected problems and rollback."""
        loop = SafeSelfImprovementLoop(
            system=mock_system,
            approval_gate=approval_gate,
            simulation_env=simulation_env,
            deployment_manager=deployment_manager
        )
        
        # Create and deploy a change
        deployment = DeploymentRecord(
            proposal_id="prop_1",
            deployment_id="deploy_1",
            change_type=ChangeType.PARAMETER_TUNING,
            system_state_hash="abc123",
            baseline_metrics={
                "accuracy": 0.85,
                "causal_consistency": 0.95,
                "planning_success_rate": 0.88
            },
            deployed_at=datetime.now(),
            deployed_by="test",
            active=True
        )
        
        deployment_manager.deployments["prop_1"] = deployment
        deployment_manager.rollback_detector.monitor_deployment(deployment)
        
        # Simulate problem detection
        degraded_metrics = {
            "accuracy": 0.70,  # Major drop
            "causal_consistency": 0.95,
            "planning_success_rate": 0.88
        }
        
        rolled_back = loop.handle_detected_problem("prop_1", degraded_metrics)
        
        # Should detect and handle problem
        assert deployment.needs_rollback == True
    
    def test_get_status(self, mock_system, approval_gate, simulation_env, deployment_manager):
        """Test getting system status."""
        loop = SafeSelfImprovementLoop(
            system=mock_system,
            approval_gate=approval_gate,
            simulation_env=simulation_env,
            deployment_manager=deployment_manager
        )
        
        status = loop.get_status()
        
        assert "cycles_completed" in status
        assert "total_proposals" in status
        assert "approved" in status
        assert "deployed" in status
        assert "auto_approval_rate" in status
        assert 0 <= status["auto_approval_rate"] <= 1
    
    def test_audit_log_tracking(self, mock_system, approval_gate, simulation_env, deployment_manager):
        """Test that audit log tracks all changes."""
        loop = SafeSelfImprovementLoop(
            system=mock_system,
            approval_gate=approval_gate,
            simulation_env=simulation_env,
            deployment_manager=deployment_manager
        )
        
        statistics = {
            "prediction_errors": [],
            "total_predictions": 100,
            "transfer_consultation_rate": 0.95,
            "knowledge_gaps": [],
            "meta_learner_stats": None,
            "safety_violations": 0,
            "integration_quality": 4.5
        }
        
        loop.run_improvement_cycle(statistics)
        
        assert len(loop.audit_log) > 0
        assert loop.audit_log[0]["cycle"] == 1


# ============================================================================
# TEST: Safety Constraints
# ============================================================================

class TestSafetyConstraints:
    """Tests for safety-first design."""
    
    def test_change_proposal_includes_risk_level(self, sample_proposal):
        """Verify proposals include risk assessment."""
        assert hasattr(sample_proposal, "risk_level")
        assert isinstance(sample_proposal.risk_level, ChangeRiskLevel)
    
    def test_proposal_has_rollback_plan(self, sample_proposal):
        """Verify proposals include rollback difficulty."""
        assert hasattr(sample_proposal, "rollback_difficulty")
        assert sample_proposal.rollback_difficulty in ["easy", "medium", "hard"]
    
    def test_proposal_has_downsides(self, sample_proposal):
        """Verify proposals list potential downsides."""
        assert hasattr(sample_proposal, "potential_downsides")
        assert isinstance(sample_proposal.potential_downsides, list)
    
    def test_simulation_required_before_deployment(self, approval_gate, sample_proposal):
        """Verify simulation required for human-review changes."""
        # Without simulation result, shouldn't auto-approve non-trivial changes
        no_sim_result = SimulationResult(
            proposal_id=sample_proposal.proposal_id,
            simulation_id="sim_failed",
            performance_before={"accuracy": 0.85},
            performance_after={"accuracy": 0.84},
            performance_delta={"accuracy": -0.01},
            overall_score_before=0.80,
            overall_score_after=0.79,
            score_improvement=-0.01,
            safety_violations=1,  # Safety issue
            causal_drift=0.05,
            regression_detected=True,
            affected_metrics=["accuracy"],
            passed_baseline=False,
            passed_improvement=False,
            safe_to_deploy=False,
            environment="synthetic_queries",
            duration_seconds=0.5
        )
        
        status = approval_gate.submit_for_approval(sample_proposal, no_sim_result)
        
        # Should queue for human review, not auto-approve
        assert status == ApprovalStatus.UNDER_REVIEW or status == ApprovalStatus.REJECTED
    
    def test_rollback_on_safety_violation(self):
        """Verify automatic rollback on safety violations."""
        detector = RollbackDetector()
        deployment = DeploymentRecord(
            proposal_id="prop_1",
            deployment_id="deploy_1",
            change_type=ChangeType.PARAMETER_TUNING,
            system_state_hash="abc123",
            baseline_metrics={
                "accuracy": 0.85,
                "causal_consistency": 0.95,
                "planning_success_rate": 0.88,
                "safety_violations": 0
            },
            deployed_at=datetime.now(),
            deployed_by="test",
            active=True
        )
        
        # Any increase in violations triggers rollback
        current_metrics = {"safety_violations": 1}
        current_metrics.update(deployment.baseline_metrics)
        current_metrics["safety_violations"] = 1
        
        should_rollback, reason = detector.check_for_degradation(deployment, current_metrics)
        
        assert should_rollback == True


# ============================================================================
# TEST: Integration Benchmarks
# ============================================================================

class TestIntegrationBenchmarks:
    """Integration and performance benchmarks."""
    
    def test_proposal_generation_performance(self, proposal_generator, mock_system):
        """Test proposal generation speed."""
        statistics = {
            "prediction_errors": list(range(10)),
            "total_predictions": 100,
            "transfer_consultation_rate": 0.90,
            "knowledge_gaps": ["physics"],
            "meta_learner_stats": None,
            "safety_violations": 1,
            "integration_quality": 3.5
        }
        
        import time
        start = time.time()
        batch = proposal_generator.analyze_system_and_propose(mock_system, statistics)
        duration = time.time() - start
        
        # Should be fast
        assert duration < 1.0
        assert batch.total_count > 0
    
    def test_end_to_end_cycle_performance(self, mock_system, approval_gate, simulation_env, deployment_manager):
        """Test complete cycle performance."""
        loop = SafeSelfImprovementLoop(
            system=mock_system,
            approval_gate=approval_gate,
            simulation_env=simulation_env,
            deployment_manager=deployment_manager
        )
        
        statistics = {
            "prediction_errors": [],
            "total_predictions": 100,
            "transfer_consultation_rate": 0.95,
            "knowledge_gaps": [],
            "meta_learner_stats": None,
            "safety_violations": 0,
            "integration_quality": 4.5
        }
        
        import time
        start = time.time()
        loop.run_improvement_cycle(statistics)
        duration = time.time() - start
        
        # Full cycle should complete in reasonable time
        assert duration < 5.0
    
    def test_auto_approval_reduces_overhead(self, approval_gate):
        """Test that auto-approval reduces human review overhead."""
        # Create 10 trivial safety proposals
        for i in range(10):
            proposal = ChangeProposal(
                proposal_id=f"safety_{i}",
                change_type=ChangeType.SAFETY_IMPROVEMENT,
                title=f"Safety Improvement {i}",
                description="Simple check",
                affected_components=["CausalStateManager"],
                affected_phases=[6],
                current_value=f"val_{i}",
                proposed_value=f"val_{i}_improved",
                parameter_name=f"param_{i}",
                motivation="Safety",
                expected_improvement="Better safety",
                improvement_metric="safety",
                estimated_improvement=0.10,
                risk_level=ChangeRiskLevel.TRIVIAL,
                potential_downsides=[],
                affected_capabilities=["safety"],
                rollback_difficulty="easy",
                proposed_by="safety_monitor"
            )
            
            result = SimulationResult(
                proposal_id=proposal.proposal_id,
                simulation_id=f"sim_{i}",
                performance_before={"safety": 0.90},
                performance_after={"safety": 0.95},
                performance_delta={"safety": 0.05},
                overall_score_before=0.85,
                overall_score_after=0.87,
                score_improvement=0.02,
                safety_violations=0,
                causal_drift=0.01,
                regression_detected=False,
                affected_metrics=["safety"],
                passed_baseline=True,
                passed_improvement=True,
                safe_to_deploy=True,
                environment="synthetic_queries",
                duration_seconds=0.2
            )
            
            approval_gate.submit_for_approval(proposal, result)
        
        # All should be auto-approved
        assert approval_gate.auto_approved_count == 10
        # No human review needed
        assert len(approval_gate.approval_queue) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
