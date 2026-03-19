from typing import Any


class Planner:

    def goal_to_tasks(self, goal: dict[str, Any]) -> list[dict[str, str]]:

        description = goal["description"].lower()

        if "research" in description:

            return [
                {"agent": "research_agent", "task": goal["description"]},
                {"agent": "critic_agent", "task": "review research results"}
            ]

        if "create agent" in description:

            return [
                {"agent": "agent_generator", "task": goal["description"]}
            ]

        return [
            {"agent": "critic_agent", "task": goal["description"]}
        ]
