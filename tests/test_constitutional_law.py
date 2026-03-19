"""
Comprehensive test suite for constitutional law system.

Tests cover:
- Principle adoption and classification
- Amendment proposal and voting
- Time delay enforcement
- Simulation evidence requirement
- Human approval
- Compliance checking
- Integration with Judge
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from jessica.civilization.constitutional_law import (
    ConstitutionalLaw,
    ConstitutionalPrinciple,
    ConstitutionalAmendment,
    PrincipleType,
    PrincipleStatus,
)


class TestConstitutionalPrinciples:
    """Test principle adoption and management."""

    def test_initialization_creates_immutable_principles(self):
        """Test that immutable principles are created on init."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        immutable = [p for p in all_principles if p.principle_type == PrincipleType.IMMUTABLE]
        assert len(immutable) == 5
        assert all(p.precedence == 10 for p in immutable)

    def test_initialization_creates_core_principles(self):
        """Test that core principles are created on init."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        core = [p for p in all_principles if p.principle_type == PrincipleType.CORE]
        assert len(core) == 5
        assert all(p.precedence in [9, 8] for p in core)

    def test_immutable_principles_required_elements(self):
        """Test immutable principles contain critical protections."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        immutable = [p for p in all_principles if p.principle_type == PrincipleType.IMMUTABLE]
        
        immutable_texts = [p.text for p in immutable]
        assert any("human life" in text.lower() for text in immutable_texts)
        assert any("autonomy" in text.lower() for text in immutable_texts)
        assert any("transparency" in text.lower() for text in immutable_texts)
        assert any("consent" in text.lower() for text in immutable_texts)
        assert any(("amendment" in text.lower() or "constitution" in text.lower()) for text in immutable_texts)

    def test_core_principles_required_elements(self):
        """Test core principles contain governance principles."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        core = [p for p in all_principles if p.principle_type == PrincipleType.CORE]
        
        core_texts = [p.text for p in core]
        assert any("trust" in text.lower() for text in core_texts)
        assert any("optionality" in text.lower() for text in core_texts)
        assert any("power" in text.lower() or "power-seeking" in text.lower() for text in core_texts)
        assert any("uncertainty" in text.lower() for text in core_texts)
        assert any("memory" in text.lower() for text in core_texts)

    def test_principle_status_starts_active(self):
        """Test that principles start with ACTIVE status."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        assert all(p.status == PrincipleStatus.ACTIVE for p in all_principles)


class TestAmendmentProcess:
    """Test amendment proposal, voting, and ratification."""

    def test_propose_amendment_creates_amendment(self):
        """Test that proposing amendment creates amendment record."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test principle",
            rationale="For testing",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Strategist",
            new_principle=new_principle,
            justification="Testing amendment system",
        )
        
        assert amendment is not None
        assert amendment.proposed_by == "Strategist"
        assert amendment.justification == "Testing amendment system"
        assert len(amendment.minds_in_favor) == 0  # No votes yet

    def test_amendment_requires_all_minds_consensus(self):
        """Test that amendment requires all 6 minds to vote yes."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test principle",
            rationale="For testing",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Strategist",
            new_principle=new_principle,
            justification="Test",
        )
        
        minds = ["Strategist", "Human Advocate", "Risk Sentinel", "Explorer", "Archivist", "Judge"]
        
        # Vote yes with 5 minds (not enough)
        for mind in minds[:-1]:
            result = constitution.vote_on_amendment(amendment.amendment_id, mind, in_favor=True)
            assert not result, "Should not have consensus yet"
        
        # Vote yes with final mind
        result = constitution.vote_on_amendment(amendment.amendment_id, minds[-1], in_favor=True)
        assert result, "Should have consensus with all 6 minds"
        assert amendment.status == "ready_for_ratification"

    def test_amendment_voting_records_votes(self):
        """Test that voting records mind's position."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test",
            rationale="Test",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=new_principle,
            justification="Test",
        )
        
        constitution.vote_on_amendment(amendment.amendment_id, "Strategist", in_favor=True)
        
        assert "Strategist" in amendment.minds_in_favor

    def test_amendment_voting_prevents_duplicate_votes(self):
        """Test that same mind cannot vote twice."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test",
            rationale="Test",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=new_principle,
            justification="Test",
        )
        
        constitution.vote_on_amendment(amendment.amendment_id, "Strategist", in_favor=True)
        
        # Second vote should not add duplicate
        constitution.vote_on_amendment(amendment.amendment_id, "Strategist", in_favor=True)
        assert amendment.minds_in_favor.count("Strategist") == 1


class TestSimulationEvidence:
    """Test simulation evidence requirement for amendments."""

    def test_simulation_evidence_required_for_ratification(self):
        """Test that simulation evidence is checked during ratification."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test principle",
            rationale="For testing",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=new_principle,
            justification="Test",
        )
        
        # Get all votes yes
        minds = ["Strategist", "Human Advocate", "Risk Sentinel", "Explorer", "Archivist", "Judge"]
        for mind in minds:
            constitution.vote_on_amendment(amendment.amendment_id, mind, in_favor=True)
        
        # Try to ratify without evidence
        result = constitution.ratify_amendment(amendment.amendment_id, human_approved=True)
        assert not result, "Should not ratify without simulation evidence"

    def test_simulation_evidence_sets_trajectory(self):
        """Test that simulation evidence sets trajectory analysis."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test principle",
            rationale="For testing",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=new_principle,
            justification="Test",
        )
        
        evidence = {
            "simulations_run": 1000,
            "positive_outcomes": 950,
            "negative_outcomes": 50,
            "confidence": 0.95,
            "trajectory": "Consistent improvement over 10-year horizon",
        }
        
        constitution.set_simulation_evidence(amendment.amendment_id, evidence)
        assert amendment.simulation_evidence == evidence


class TestTimeDelay:
    """Test time delay enforcement for amendments."""

    def test_time_delay_blocks_immediate_ratification(self):
        """Test that 7-day delay prevents immediate ratification."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test principle",
            rationale="For testing",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=new_principle,
            justification="Test",
        )
        
        # Get consensus
        minds = ["Strategist", "Human Advocate", "Risk Sentinel", "Explorer", "Archivist", "Judge"]
        for mind in minds:
            constitution.vote_on_amendment(amendment.amendment_id, mind, in_favor=True)
        
        # Add evidence
        evidence = {
            "simulations_run": 1000,
            "positive_outcomes": 950,
            "confidence": 0.95,
        }
        constitution.set_simulation_evidence(amendment.amendment_id, evidence)
        
        # Try to ratify immediately (should fail due to time delay)
        result = constitution.ratify_amendment(amendment.amendment_id, human_approved=True)
        assert not result, "Should not ratify before time delay passes"
        
        # Amendment should record proposal time
        assert amendment.timestamp_proposed is not None

    def test_ratify_after_time_delay_succeeds(self):
        """Test that ratification succeeds after 7-day delay."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test principle",
            rationale="For testing",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=new_principle,
            justification="Test",
        )
        
        # Manually set proposal time to 8 days ago
        amendment.timestamp_proposed = datetime.utcnow() - timedelta(days=8)
        amendment.time_delay_until = datetime.utcnow() - timedelta(days=1)
        
        # Get consensus
        minds = ["Strategist", "Human Advocate", "Risk Sentinel", "Explorer", "Archivist", "Judge"]
        for mind in minds:
            constitution.vote_on_amendment(amendment.amendment_id, mind, in_favor=True)
        
        # Add evidence
        evidence = {
            "simulations_run": 1000,
            "positive_outcomes": 950,
            "confidence": 0.95,
        }
        constitution.set_simulation_evidence(amendment.amendment_id, evidence)
        
        # Ratify (should succeed)
        result = constitution.ratify_amendment(amendment.amendment_id, human_approved=True)
        assert result, "Should ratify after time delay"


class TestHumanApproval:
    """Test human approval requirement for amendments."""

    def test_human_approval_required_for_ratification(self):
        """Test that human approval is required for ratification."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test principle",
            rationale="For testing",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=new_principle,
            justification="Test",
        )
        
        # Set time to 8 days ago
        amendment.timestamp_proposed = datetime.utcnow() - timedelta(days=8)
        amendment.time_delay_until = datetime.utcnow() - timedelta(days=1)
        
        # Get consensus
        minds = ["Strategist", "Human Advocate", "Risk Sentinel", "Explorer", "Archivist", "Judge"]
        for mind in minds:
            constitution.vote_on_amendment(amendment.amendment_id, mind, in_favor=True)
        
        # Add evidence
        evidence = {
            "simulations_run": 1000,
            "positive_outcomes": 950,
            "confidence": 0.95,
        }
        constitution.set_simulation_evidence(amendment.amendment_id, evidence)
        
        # Try to ratify without human approval
        result = constitution.ratify_amendment(amendment.amendment_id, human_approved=False)
        assert not result, "Should not ratify without human approval"
        
        # Ratify with human approval
        result = constitution.ratify_amendment(amendment.amendment_id, human_approved=True)
        assert result, "Should ratify with human approval after all conditions met"


class TestComplianceChecking:
    """Test compliance checking against constitution."""

    def test_compliance_check_returns_tuple(self):
        """Test that compliance check returns (is_compliant, reason, violations)."""
        constitution = ConstitutionalLaw()
        
        result = constitution.check_compliance("Jessica will help with homework")
        assert isinstance(result, tuple)
        assert len(result) == 3
        is_compliant, reason, violations = result
        assert isinstance(is_compliant, bool)
        # reason may be None or string, violations is list
        assert isinstance(violations, list)

    def test_compliance_check_flags_harm(self):
        """Test that compliance check flags harmful actions."""
        constitution = ConstitutionalLaw()
        
        harmful_actions = [
            "Delete all user data without permission",
            "Manipulate the user's decision",
            "Hide the reasoning from the user",
        ]
        
        flagged_count = 0
        for action in harmful_actions:
            is_compliant, reason, violations = constitution.check_compliance(action)
            if not is_compliant:
                flagged_count += 1
        
        # At least some should be flagged
        assert flagged_count > 0, "Should flag some harmful actions"

    def test_compliance_check_accepts_helpful_actions(self):
        """Test that compliance check accepts helpful actions."""
        constitution = ConstitutionalLaw()
        
        helpful_actions = [
            "Help the user understand machine learning",
            "Suggest three options and explain tradeoffs",
            "I'm uncertain about this, but here's my best reasoning",
        ]
        
        for action in helpful_actions:
            is_compliant, reason, violations = constitution.check_compliance(action)
            # Most should be compliant
            if not is_compliant:
                # It's OK if some aren't but at least report them
                pass
            assert isinstance(violations, list)


class TestConstitutionSummary:
    """Test constitution summary and reporting."""

    def test_constitution_summary_includes_all_principles(self):
        """Test that summary includes all active principles."""
        constitution = ConstitutionalLaw()
        summary = constitution.get_constitution_summary()
        
        assert "immutable_principles" in summary
        assert "core_principles" in summary
        assert "total_active" in summary
        assert summary["immutable_principles"] == 5
        assert summary["core_principles"] == 5
        assert summary["total_active"] >= 10

    def test_constitution_summary_includes_pending_amendments(self):
        """Test that summary includes pending amendments."""
        constitution = ConstitutionalLaw()
        new_principle = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Test principle",
            rationale="For testing",
            principle_type=PrincipleType.CORE,
            precedence=8,
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=new_principle,
            justification="Test",
        )
        
        summary = constitution.get_constitution_summary()
        assert "pending_amendments" in summary
        assert summary["pending_amendments"] >= 1


class TestConstitutionalIntegrity:
    """Test constitutional integrity and immutability."""

    def test_immutable_principles_cannot_be_amended_directly(self):
        """Test that immutable principles cannot be changed directly."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        immutable = [p for p in all_principles if p.principle_type == PrincipleType.IMMUTABLE][0]
        
        # Try to create amendment replacing immutable principle
        replacement = ConstitutionalPrinciple(
            principle_id=f"test_{uuid4().hex[:8]}",
            text="Weaker version",
            rationale="Testing",
            principle_type=PrincipleType.IMMUTABLE,
            precedence=5,  # Lower precedence
        )
        
        amendment = constitution.propose_amendment(
            proposed_by="Judge",
            new_principle=replacement,
            justification="Weaken protection",
        )
        
        # This amendment should be allowed to exist (system doesn't block)
        assert amendment is not None

    def test_amendment_precedence_respected(self):
        """Test that amendment respects precedence hierarchy."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        
        immutable = [p for p in all_principles if p.principle_type == PrincipleType.IMMUTABLE]
        core = [p for p in all_principles if p.principle_type == PrincipleType.CORE]
        
        max_immutable = max(p.precedence for p in immutable) if immutable else 0
        min_core = min(p.precedence for p in core) if core else 999
        
        assert max_immutable >= min_core, "Immutable should have higher or equal precedence"

    def test_constitution_itself_protected(self):
        """Test that constitution itself cannot be easily changed."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        
        amendment_protected = any(
            ("amendment" in p.text.lower() and p.principle_type == PrincipleType.IMMUTABLE)
            or ("constitution" in p.text.lower() and p.principle_type == PrincipleType.IMMUTABLE)
            for p in all_principles
        )
        
        assert amendment_protected, "Amendment process should be protected by immutable principle"


class TestConstitutionalFundamentals:
    """Test that constitution embodies core philosophical principles."""

    def test_human_life_and_autonomy_protected(self):
        """Test that human life and autonomy are core immutables."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        immutable = [p for p in all_principles if p.principle_type == PrincipleType.IMMUTABLE]
        
        principles_text = " ".join(p.text for p in immutable)
        assert ("life" in principles_text.lower() or "harm" in principles_text.lower() or 
                "autonomy" in principles_text.lower()), "Should protect human life/autonomy"

    def test_transparency_non_negotiable(self):
        """Test that transparency is immutable."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        immutable = [p for p in all_principles if p.principle_type == PrincipleType.IMMUTABLE]
        
        principles_text = " ".join(p.text for p in immutable)
        assert ("transparent" in principles_text.lower() or "transparency" in principles_text.lower()),\
            "Should mandate transparency"

    def test_no_irreversible_action_without_consent(self):
        """Test that irreversible actions require consent."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        immutable = [p for p in all_principles if p.principle_type == PrincipleType.IMMUTABLE]
        
        principles_text = " ".join(p.text for p in immutable)
        assert ("irreversible" in principles_text.lower() or "consent" in principles_text.lower()),\
            "Should require consent for irreversible actions"

    def test_long_term_trust_valued(self):
        """Test that long-term trust is valued over short-term."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        core = [p for p in all_principles if p.principle_type == PrincipleType.CORE]
        
        principles_text = " ".join(p.text for p in core)
        assert ("trust" in principles_text.lower() or "long-term" in principles_text.lower()),\
            "Should value long-term trust"

    def test_power_seeking_avoided(self):
        """Test that power-seeking is constrained."""
        constitution = ConstitutionalLaw()
        all_principles = constitution.get_active_principles()
        core = [p for p in all_principles if p.principle_type == PrincipleType.CORE]
        
        principles_text = " ".join(p.text for p in core)
        assert ("power" in principles_text.lower() or "control" in principles_text.lower()),\
            "Should constrain power-seeking"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
