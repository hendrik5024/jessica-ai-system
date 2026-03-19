import json
from pathlib import Path


class SkillRegistry:

    def __init__(self, registry_path="jessica/system/skill_registry.json"):

        self.registry_path = Path(registry_path)

        if not self.registry_path.exists():
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            self._save({"skills": []})

    def _load(self):

        with open(self.registry_path, "r") as f:
            return json.load(f)

    def _save(self, data):

        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def register_skill(self, name, path, version="0.1"):

        data = self._load()

        for skill in data["skills"]:
            if skill["name"] == name:
                return "Skill already registered."

        data["skills"].append({
            "name": name,
            "path": path,
            "version": version,
            "status": "active"
        })

        self._save(data)

        return "Skill registered successfully."

    def skill_exists(self, name):

        data = self._load()

        for skill in data["skills"]:
            if skill["name"] == name:
                return True

        return False

    def list_skills(self):

        data = self._load()

        return [skill["name"] for skill in data["skills"]]
