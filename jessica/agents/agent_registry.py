import importlib


class AgentRegistry:

    def __init__(self):

        self.agents = {}

    def register(self, agent):

        self.agents[agent.name] = agent

    def get(self, name):

        return self.agents.get(name)

    def list_agents(self):

        return list(self.agents.keys())

    def register_generated_agent(self, module_path, class_name):

        importlib.invalidate_caches()
        module = importlib.import_module(module_path)

        agent_class = getattr(module, class_name)

        agent = agent_class()

        self.register(agent)
