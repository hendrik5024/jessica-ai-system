class ProposalMemory:
    """
    Stores proposals created by Jessica.
    """

    def __init__(self):
        self._proposals = {}

    def add(self, proposal):
        self._proposals[proposal.proposal_id] = proposal

    def get(self, proposal_id):
        return self._proposals.get(proposal_id)

    def list_all(self):
        return list(self._proposals.values())
