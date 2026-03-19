from jessica.goals import GoalEngine, GoalProposalEngine


def test_goal_proposal_generation():
    goal_engine = GoalEngine()
    proposal_engine = GoalProposalEngine()

    goal = goal_engine.create_goal("Improve reasoning")

    proposals = proposal_engine.generate_proposals(goal)

    assert len(proposals) > 0
    assert proposals[0].goal_id == goal.goal_id
