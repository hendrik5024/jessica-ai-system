from jessica.memory.agent_memory_manager import AgentMemoryManager


class BaseAgent:

    def __init__(self, name, description):

        self.name = name
        self.description = description
        self.memory = AgentMemoryManager()

    def run(self, task, context=None):

        raise NotImplementedError("Agent must implement run()")
