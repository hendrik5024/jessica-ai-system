import json
from pathlib import Path


class AgentGenerator:

    def __init__(self, agents_root="jessica/sandbox_agents"):
        self.agents_root = Path(agents_root)

    def create_agent(self, name, description):

        agent_dir = self.agents_root / name.lower()
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Ensure importable package structure for dynamic validation imports.
        root_init = self.agents_root / "__init__.py"
        if not root_init.exists():
            root_init.write_text("", encoding="utf-8")

        agent_init = agent_dir / "__init__.py"
        if not agent_init.exists():
            agent_init.write_text("", encoding="utf-8")

        agent_file = agent_dir / "agent.py"

        template = f'''from jessica.agents.base_agent import BaseAgent


class {name}(BaseAgent):

    def __init__(self):
        super().__init__(
            name="{name}",
            description="{description}"
        )

    def run(self, task, context=None):

        return "Agent {name} executed task successfully."
'''

        agent_file.write_text(template, encoding="utf-8")

        config_file = agent_dir / "config.json"
        config_file.write_text(
            json.dumps(
                {
                    "name": name,
                    "description": description,
                    "state": "sandbox",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        return str(agent_dir)
