import json
import os


SKILL_FILE = "jessica/memory/skills.json"


class SkillMemory:

    def __init__(self):
        os.makedirs(os.path.dirname(SKILL_FILE), exist_ok=True)

        if not os.path.exists(SKILL_FILE):
            with open(SKILL_FILE, "w", encoding="utf-8") as handle:
                json.dump({}, handle)

        with open(SKILL_FILE, "r", encoding="utf-8") as handle:
            self.skills = json.load(handle)

    def record_skill(self, task, tool):
        self.skills[task] = tool

        with open(SKILL_FILE, "w", encoding="utf-8") as handle:
            json.dump(self.skills, handle, indent=4)

    def find_tool(self, task):
        return self.skills.get(task, None)