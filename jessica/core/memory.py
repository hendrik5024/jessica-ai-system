import json
import os
from typing import Any


class Memory:

    def __init__(self, file_path: str = "jessica/memory.json") -> None:

        self.file_path = file_path

        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def load(self) -> dict[str, Any]:

        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict[str, Any]) -> None:

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def remember(self, key: str, value: Any) -> None:

        data = self.load()
        data[key] = value
        self.save(data)

    def recall(self, key: str) -> Any:

        data = self.load()
        return data.get(key)
