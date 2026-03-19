"""Phase 14 — Self-Improvement Governance: proposal registry."""

from __future__ import annotations

from typing import Dict, List, Optional

from jessica.improvement_proposal import ImprovementProposal


class ImprovementRegistry:
    def __init__(self) -> None:
        self._proposals: Dict[str, ImprovementProposal] = {}
        self._order: List[str] = []
        self._decisions: Dict[str, Optional[str]] = {}
        self._decision_log: Dict[str, List[str]] = {}

    def add_proposal(self, proposal: ImprovementProposal) -> None:
        if proposal.proposal_id in self._proposals:
            raise ValueError("Proposal already exists")
        self._proposals[proposal.proposal_id] = proposal
        self._order.append(proposal.proposal_id)
        self._decisions[proposal.proposal_id] = None
        self._decision_log[proposal.proposal_id] = []

    def approve_proposal(self, proposal_id: str) -> None:
        if proposal_id not in self._proposals:
            raise ValueError("Proposal not found")
        current = self._decisions.get(proposal_id)
        if current == "rejected":
            raise ValueError("Proposal already rejected")
        if current != "approved":
            self._decisions[proposal_id] = "approved"
            self._decision_log[proposal_id].append("approved")

    def reject_proposal(self, proposal_id: str) -> None:
        if proposal_id not in self._proposals:
            raise ValueError("Proposal not found")
        current = self._decisions.get(proposal_id)
        if current == "approved":
            raise ValueError("Proposal already approved")
        if current != "rejected":
            self._decisions[proposal_id] = "rejected"
            self._decision_log[proposal_id].append("rejected")

    def get_proposal(self, proposal_id: str) -> ImprovementProposal | None:
        return self._proposals.get(proposal_id)

    def list_proposals(self) -> List[ImprovementProposal]:
        return [self._proposals[pid] for pid in self._order]

    def get_decision(self, proposal_id: str) -> Optional[str]:
        return self._decisions.get(proposal_id)

    def get_decision_log(self, proposal_id: str) -> List[str]:
        return list(self._decision_log.get(proposal_id, []))
