from typing import Any


class GoalManager:

    def __init__(self) -> None:
        self.goals: list[dict[str, Any]] = []

    def add_goal(self, description: str) -> dict[str, Any]:

        goal = {
            "description": description,
            "status": "active",
            "tasks": []
        }

        self.goals.append(goal)

        return goal

    def list_goals(self) -> list[dict[str, Any]]:

        return self.goals

    def get_active_goal(self) -> str | None:

        for goal in self.goals:
            if goal.get("status") == "active":
                return str(goal.get("description", ""))

        return None

    def complete_goal(self, description: str) -> dict[str, Any] | None:

        for goal in self.goals:

            if goal["description"] == description:
                goal["status"] = "completed"
                return goal

        return None
