from jessica.agents.base_agent import BaseAgent
from pathlib import Path


class ProjectAnalyzerAgent(BaseAgent):

    def __init__(self):

        super().__init__(
            name="ProjectAnalyzer",
            description="Analyzes Python projects and summarizes structure."
        )

    def run(self, task, context=None):

        root = Path(context or ".")

        py_files = list(root.rglob("*.py"))

        return {
            "files": len(py_files),
            "modules": list({p.parent.name for p in py_files})
        }
