import uuid
from typing import List

from .goal_record import GoalRecord
from .goal_proposal import GoalProposal


class GoalProposalEngine:
    def generate_proposals(self, goal: GoalRecord) -> List[GoalProposal]:
        proposal = GoalProposal(
            proposal_id=str(uuid.uuid4()),
            goal_id=goal.goal_id,
            proposal_text=f"Suggested improvement aligned to goal: {goal.description}",
        )

        return [proposal]
