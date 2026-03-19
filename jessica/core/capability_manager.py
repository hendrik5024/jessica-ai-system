from typing import Any


class CapabilityManager:

    def __init__(self) -> None:
        self.capabilities: dict[str, Any] = {}

    def register(self, name: str, agent: Any) -> None:

        self.capabilities[name] = agent

    def get(self, capability: str) -> Any:

        return self.capabilities.get(capability)

    def list_capabilities(self) -> list[str]:

        return list(self.capabilities.keys())
