from pathlib import Path


class ProjectArchitect:

    def __init__(self, projects_path="projects"):

        self.projects_path = Path(projects_path)
        self.projects_path.mkdir(parents=True, exist_ok=True)

    def build_project(self, name, modules):

        project_path = self.projects_path / name

        if project_path.exists():
            name = name + "_v2"
            project_path = self.projects_path / name

        project_path.mkdir()

        for module in modules:

            file_path = project_path / f"{module}.py"

            file_path.write_text(
                f"# {module} module\n\n"
                f"def run():\n"
                f"    print('Module {module} running')\n"
            )

        (project_path / "main.py").write_text(
            "print('Project started')"
        )

        return project_path
