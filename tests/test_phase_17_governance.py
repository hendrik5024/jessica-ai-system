from datetime import datetime

from jessica.governance import (
    ImprovementProposal,
    ImprovementGovernor,
)


def test_improvement_governance_flow():
    governor = ImprovementGovernor()

    proposal = ImprovementProposal(
        proposal_id="p1",
        capability_name="math_reasoning",
        description="Add symbolic reasoning module",
        expected_benefit="Better calculation ability",
        potential_risk="Incorrect reasoning output",
        created_at=datetime.utcnow(),
    )

    decision = governor.review_proposal(
        proposal,
        approve=True,
        reviewer="human",
        reason="Safe and useful",
    )

    assert decision.approved is True
    assert governor.get_decision("p1") is not None
