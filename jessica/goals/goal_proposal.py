from dataclasses import dataclass


@dataclass(frozen=True)
class GoalProposal:
    proposal_id: str
    goal_id: str
    proposal_text: str
