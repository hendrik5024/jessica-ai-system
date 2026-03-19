from datetime import datetime

from jessica.governance import (
    ImprovementProposal,
    ImprovementGovernor,
    CapabilityInstaller,
)


def test_capability_installation_flow():
    governor = ImprovementGovernor()

    proposal = ImprovementProposal(
        proposal_id="p2",
        capability_name="language_module",
        description="Add multilingual support",
        expected_benefit="Better global interaction",
        potential_risk="Translation errors",
        created_at=datetime.utcnow(),
    )

    governor.review_proposal(
        proposal,
        approve=True,
        reviewer="human",
        reason="Approved",
    )

    installer = CapabilityInstaller(governor)

    record = installer.install_capability(
        proposal_id="p2",
        capability_name="language_module",
        installer="human",
    )

    assert record.success is True
