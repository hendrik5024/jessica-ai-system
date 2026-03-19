import json
import os

WORKFLOW_FILE = "jessica/memory/workflow_memory.json"


class WorkflowMemory:

    def __init__(self):

        if not os.path.exists(WORKFLOW_FILE):
            with open(WORKFLOW_FILE, "w") as f:
                json.dump({}, f)

        with open(WORKFLOW_FILE, "r") as f:
            self.workflows = json.load(f)

    def store_workflow(self, intent, steps):

        # Prevent overwriting good workflows accidentally
        if intent not in self.workflows:

            self.workflows[intent] = {
                "steps": steps,
                "success_count": 1
            }

        else:

            self.workflows[intent]["success_count"] += 1

        self._save()

    def get_workflow(self, intent):

        workflow = self.workflows.get(intent)

        if workflow:
            return workflow["steps"]

        return None

    def _save(self):

        with open(WORKFLOW_FILE, "w") as f:
            json.dump(self.workflows, f, indent=2)
