from typing import Any


class Supervisor:

    def __init__(self) -> None:

        self.max_retries = 3
        self.task_history: dict[str, int] = {}

    def approve(self, task: dict[str, Any]) -> tuple[bool, str]:

        agent = task.get("agent")

        if not agent:
            return False, "No agent defined"

        # Track task repetition
        key = f"{agent}:{task.get('task')}"

        count = self.task_history.get(key, 0)

        if count >= self.max_retries:
            return False, "Task repeated too many times"

        self.task_history[key] = count + 1

        return True, "approved"


    __all__ = ["Supervisor"]
