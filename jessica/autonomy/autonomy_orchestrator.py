from jessica.autonomy.autonomy_engine import AutonomyEngine
from jessica.autonomy.proposal_memory import ProposalMemory


class AutonomyOrchestrator:
    """
    Coordinates proposals and approval flow.
    """

    def __init__(self):
        self.engine = AutonomyEngine()
        self.memory = ProposalMemory()

    def process(self, user_input: str):
        """
        Generate proposal (if needed)
        """

        proposal = self.engine.propose(user_input)

        if not proposal:
            return None

        self.memory.add(proposal)
        return proposal

    def approve(self, proposal_id: str):
        proposal = self.memory.get(proposal_id)

        if proposal:
            return "approved"

        return "not_found"
