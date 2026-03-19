import shutil
from pathlib import Path


class SkillInstaller:

    def __init__(self,
                 generated_path="jessica/generated_skills",
                 skills_path="jessica/skills"):

        self.generated_path = Path(generated_path)
        self.skills_path = Path(skills_path)

        self.skills_path.mkdir(parents=True, exist_ok=True)

    def install_skill(self, skill_name):

        source = self.generated_path / skill_name
        destination = self.skills_path / skill_name

        if not source.exists():
            return f"Skill '{skill_name}' not found."

        if destination.exists():
            return f"Skill '{skill_name}' already installed."

        shutil.move(str(source), str(destination))

        return f"Skill '{skill_name}' installed successfully."
