from typing import Any


class TaskQueue:

    def __init__(self) -> None:
        self.queue: list[dict[str, Any]] = []

    def add_task(self, task: dict[str, Any]) -> None:

        self.queue.append(task)

    def next_task(self) -> dict[str, Any] | None:

        if not self.queue:
            return None

        return self.queue.pop(0)

    def list_tasks(self) -> list[dict[str, Any]]:

        return self.queue
