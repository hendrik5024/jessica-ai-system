from typing import Dict
from datetime import datetime

from .improvement_proposal import ImprovementProposal
from .improvement_decision import ImprovementDecision


class ImprovementGovernor:
    def __init__(self):
        self._decisions: Dict[str, ImprovementDecision] = {}

    def review_proposal(
        self,
        proposal: ImprovementProposal,
        approve: bool,
        reviewer: str,
        reason: str,
    ) -> ImprovementDecision:
        decision = ImprovementDecision(
            proposal_id=proposal.proposal_id,
            approved=approve,
            reviewer=reviewer,
            decision_reason=reason,
            decided_at=datetime.utcnow(),
        )

        self._decisions[proposal.proposal_id] = decision
        return decision

    def get_decision(self, proposal_id: str):
        return self._decisions.get(proposal_id)
