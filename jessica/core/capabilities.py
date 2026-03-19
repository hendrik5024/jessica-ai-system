"""
Jessica Capability Registry

Defines what Jessica CAN and CANNOT do.
This is the source of truth for reality.
"""


class CapabilityRegistry:

    def __init__(self):
        self.capabilities = {
            "has_web_access": False,
            "has_camera_access": False,
            "has_file_access": False,
            "can_execute_actions": False,
            "uses_llm": True,
            "has_memory": True,
        }

    def has(self, capability: str) -> bool:
        return self.capabilities.get(capability, False)
