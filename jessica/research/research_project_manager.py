from typing import Any


class ResearchProjectManager:
    """Manages long-running research projects.

    A project groups hypotheses, experiments, and results under a single goal.
    """

    def __init__(self, knowledge_memory: Any) -> None:
        self.knowledge_memory = knowledge_memory
        self.projects: dict[str, dict[str, Any]] = {}

    def create_project(self, goal: str) -> str:
        project_id = f"project_{len(self.projects) + 1}"

        self.projects[project_id] = {
            "goal": goal,
            "hypotheses": [],
            "experiments": [],
            "results": [],
        }

        return project_id

    def add_hypothesis(self, project_id: str, hypothesis: str) -> None:

        if project_id not in self.projects:
            return

        self.projects[project_id]["hypotheses"].append(hypothesis)

    def add_experiment(self, project_id: str, experiment_record: dict[str, Any]) -> None:

        if project_id not in self.projects:
            return

        self.projects[project_id]["experiments"].append(experiment_record)

    def add_result(self, project_id: str, result_summary: str) -> None:

        if project_id not in self.projects:
            return

        self.projects[project_id]["results"].append(result_summary)

        # Also persist to long-term knowledge memory when available.
        if self.knowledge_memory is None:
            return

        if hasattr(self.knowledge_memory, "store"):
            try:
                self.knowledge_memory.store(result_summary)
                return
            except (OSError, RuntimeError, TypeError, ValueError):
                pass

        if hasattr(self.knowledge_memory, "remember"):
            try:
                self.knowledge_memory.remember(result_summary)
            except (OSError, RuntimeError, TypeError, ValueError):
                pass

    def get_project(self, project_id: str) -> dict[str, Any] | None:

        return self.projects.get(project_id)

    def find_project_id_by_goal(self, goal: str) -> str | None:

        for project_id, project in self.projects.items():
            if project.get("goal") == goal:
                return project_id

        return None
