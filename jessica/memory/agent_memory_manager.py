import json
from pathlib import Path


class AgentMemoryManager:

    def __init__(self):

        self.memory_dir = Path("jessica/agent_memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def load(self, agent_name):

        path = self.memory_dir / f"{agent_name}.json"

        if not path.exists():
            return []

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def store(self, agent_name, record):

        path = self.memory_dir / f"{agent_name}.json"

        data = []

        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

        data.append(record)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
