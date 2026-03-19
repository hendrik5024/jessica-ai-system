"""
Phase 92: Autonomous Action Proposals - Test Suite

Tests the proposal-based autonomy system.
"""

import pytest
from jessica.autonomy.action_proposal import ActionProposal
from jessica.autonomy.proposal_memory import ProposalMemory
from jessica.autonomy.autonomy_engine import AutonomyEngine
from jessica.autonomy.autonomy_orchestrator import AutonomyOrchestrator
from jessica.core.cognitive_kernel import CognitiveKernel


class TestActionProposal:
    """Test ActionProposal data class"""

    def test_create_proposal(self):
        proposal = ActionProposal(
            proposal_id="test-123",
            description="Test action",
            reasoning="Testing",
            actions=["action1"],
            risk_level="low",
        )
        assert proposal.proposal_id == "test-123"
        assert proposal.description == "Test action"
        assert proposal.risk_level == "low"

    def test_high_risk_check(self):
        proposal = ActionProposal(
            proposal_id="test-456",
            description="Dangerous action",
            reasoning="Testing",
            actions=["risky_action"],
            risk_level="high",
        )
        assert proposal.is_high_risk()

    def test_low_risk_check(self):
        proposal = ActionProposal(
            proposal_id="test-789",
            description="Safe action",
            reasoning="Testing",
            actions=["safe_action"],
            risk_level="low",
        )
        assert not proposal.is_high_risk()

    def test_default_status(self):
        proposal = ActionProposal(
            proposal_id="test-000",
            description="Test",
            reasoning="Test",
            actions=["test"],
            risk_level="low",
        )
        assert proposal.status == "pending"

    def test_requires_permission_default(self):
        proposal = ActionProposal(
            proposal_id="test-111",
            description="Test",
            reasoning="Test",
            actions=["test"],
            risk_level="low",
        )
        assert proposal.requires_permission


class TestProposalMemory:
    """Test ProposalMemory storage"""

    def test_add_proposal(self):
        memory = ProposalMemory()
        proposal = ActionProposal(
            proposal_id="test-1",
            description="Test",
            reasoning="Test",
            actions=["test"],
            risk_level="low",
        )
        memory.add(proposal)
        assert memory.get("test-1") == proposal

    def test_get_missing_proposal(self):
        memory = ProposalMemory()
        assert memory.get("nonexistent") is None

    def test_list_all_empty(self):
        memory = ProposalMemory()
        assert memory.list_all() == []

    def test_list_all(self):
        memory = ProposalMemory()
        p1 = ActionProposal(
            proposal_id="1", description="A", reasoning="R", actions=["a"], risk_level="low"
        )
        p2 = ActionProposal(
            proposal_id="2", description="B", reasoning="R", actions=["b"], risk_level="medium"
        )
        memory.add(p1)
        memory.add(p2)
        all_proposals = memory.list_all()
        assert len(all_proposals) == 2
        assert p1 in all_proposals
        assert p2 in all_proposals


class TestAutonomyEngine:
    """Test AutonomyEngine proposal generation"""

    def test_engine_enabled_by_default(self):
        engine = AutonomyEngine()
        assert engine.enabled

    def test_propose_file_operation(self):
        engine = AutonomyEngine()
        proposal = engine.propose("open file config.txt")
        assert proposal is not None
        assert "file" in proposal.description.lower()
        assert proposal.risk_level == "medium"

    def test_propose_internet_search(self):
        engine = AutonomyEngine()
        proposal = engine.propose("search the internet for Python tutorials")
        assert proposal is not None
        assert "internet" in proposal.description.lower()
        assert proposal.risk_level == "high"

    def test_propose_calculation(self):
        engine = AutonomyEngine()
        proposal = engine.propose("calculate 2 + 2")
        assert proposal is not None
        assert "calculation" in proposal.description.lower()
        assert proposal.risk_level == "low"

    def test_no_proposal_for_chat(self):
        engine = AutonomyEngine()
        proposal = engine.propose("hello, how are you?")
        assert proposal is None

    def test_empty_input(self):
        engine = AutonomyEngine()
        proposal = engine.propose("")
        assert proposal is None

    def test_proposal_has_valid_id(self):
        engine = AutonomyEngine()
        proposal = engine.propose("calculate something")
        assert proposal.proposal_id
        assert len(proposal.proposal_id) > 0


class TestAutonomyOrchestrator:
    """Test AutonomyOrchestrator coordination"""

    def test_orchestrator_initialization(self):
        orchestrator = AutonomyOrchestrator()
        assert orchestrator.engine is not None
        assert orchestrator.memory is not None

    def test_process_creates_proposal(self):
        orchestrator = AutonomyOrchestrator()
        proposal = orchestrator.process("search internet for weather")
        assert proposal is not None
        assert proposal.risk_level == "high"

    def test_process_stores_proposal(self):
        orchestrator = AutonomyOrchestrator()
        proposal = orchestrator.process("calculate 10 * 5")
        stored = orchestrator.memory.get(proposal.proposal_id)
        assert stored == proposal

    def test_process_no_proposal(self):
        orchestrator = AutonomyOrchestrator()
        proposal = orchestrator.process("hello there")
        assert proposal is None

    def test_approve_existing_proposal(self):
        orchestrator = AutonomyOrchestrator()
        proposal = orchestrator.process("open file data.txt")
        result = orchestrator.approve(proposal.proposal_id)
        assert result == "approved"

    def test_approve_missing_proposal(self):
        orchestrator = AutonomyOrchestrator()
        result = orchestrator.approve("nonexistent-id")
        assert result == "not_found"


class TestCognitiveKernelAutonomy:
    """Test autonomy integration with CognitiveKernel"""

    def test_kernel_has_autonomy(self):
        kernel = CognitiveKernel()
        assert kernel.autonomy is not None
        assert isinstance(kernel.autonomy, AutonomyOrchestrator)

    def test_kernel_returns_proposal_dict(self):
        kernel = CognitiveKernel()
        result = kernel.process("search internet for news")
        assert isinstance(result, dict)
        assert result["type"] == "proposal"
        assert "description" in result
        assert "reasoning" in result
        assert "actions" in result
        assert "risk" in result
        assert "proposal_id" in result

    def test_kernel_returns_string_for_normal_chat(self):
        kernel = CognitiveKernel()
        result = kernel.process("hello")
        assert isinstance(result, str)

    def test_proposal_has_high_risk_marked(self):
        kernel = CognitiveKernel()
        result = kernel.process("search the internet")
        assert result["risk"] == "high"

    def test_proposal_has_low_risk_marked(self):
        kernel = CognitiveKernel()
        result = kernel.process("calculate 5 * 5")
        assert result["risk"] == "low"

    def test_proposal_stored_in_memory(self):
        kernel = CognitiveKernel()
        result = kernel.process("open file test.txt")
        proposal_id = result["proposal_id"]
        stored = kernel.autonomy.memory.get(proposal_id)
        assert stored is not None
        assert stored.proposal_id == proposal_id


class TestProposalWorkflows:
    """Test complete proposal workflows"""

    def test_file_open_workflow(self):
        kernel = CognitiveKernel()
        result = kernel.process("open file config.yaml")
        assert result["type"] == "proposal"
        assert result["risk"] == "medium"
        assert "open_file" in result["actions"]

    def test_internet_search_workflow(self):
        kernel = CognitiveKernel()
        result = kernel.process("search for AGI research")
        assert result["type"] == "proposal"
        assert result["risk"] == "high"
        assert "internet_search" in result["actions"]

    def test_calculation_workflow(self):
        kernel = CognitiveKernel()
        result = kernel.process("calculate the square root")
        assert result["type"] == "proposal"
        assert result["risk"] == "low"
        assert "calculate" in result["actions"]

    def test_orchestrator_tracks_multiple_proposals(self):
        orchestrator = AutonomyOrchestrator()
        p1 = orchestrator.process("calculate 10 + 5")
        p2 = orchestrator.process("search internet")
        p3 = orchestrator.process("open file data.txt")

        all_proposals = orchestrator.memory.list_all()
        assert len(all_proposals) == 3
        assert p1 in all_proposals
        assert p2 in all_proposals
        assert p3 in all_proposals


class TestProposalSafety:
    """Test safety constraints of proposal system"""

    def test_proposal_does_not_execute(self):
        """Proposals should never execute actions automatically"""
        engine = AutonomyEngine()
        proposal = engine.propose("open file /etc/passwd")
        # Proposal created but nothing executed
        assert proposal.status == "pending"

    def test_high_risk_requires_permission(self):
        proposal = ActionProposal(
            proposal_id="test",
            description="Dangerous",
            reasoning="Test",
            actions=["dangerous"],
            risk_level="high",
        )
        assert proposal.requires_permission

    def test_proposal_immutable(self):
        proposal = ActionProposal(
            proposal_id="test",
            description="Test",
            reasoning="Test",
            actions=["test"],
            risk_level="low",
        )
        with pytest.raises(Exception):  # Frozen dataclass raises error on modification
            proposal.status = "approved"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
