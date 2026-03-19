import uuid

from jessica.autonomy.action_proposal import ActionProposal


class AutonomyEngine:
    """
    Generates possible actions based on input.
    DOES NOT execute anything.
    """

    def __init__(self):
        self.enabled = True

    def propose(self, user_input: str) -> ActionProposal | None:
        """
        Decide if an action should be proposed.
        """

        if not user_input:
            return None

        text = user_input.lower()

        # Example triggers (expand later)
        if "open" in text and "file" in text:
            return self._create(
                "Open a file",
                "User requested file access",
                ["open_file"],
                "medium"
            )

        if "search" in text or "internet" in text:
            return self._create(
                "Search internet",
                "User requested external information",
                ["internet_search"],
                "high"
            )

        if "calculate" in text:
            return self._create(
                "Perform calculation",
                "User requested calculation",
                ["calculate"],
                "low"
            )

        return None

    def _create(self, description, reasoning, actions, risk):
        return ActionProposal(
            proposal_id=str(uuid.uuid4()),
            description=description,
            reasoning=reasoning,
            actions=actions,
            risk_level=risk,
        )
