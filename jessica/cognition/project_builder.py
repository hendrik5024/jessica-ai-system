from pathlib import Path


class ProjectBuilder:

    def __init__(self, projects_path="projects"):

        self.projects_path = Path(projects_path)
        self.projects_path.mkdir(parents=True, exist_ok=True)

    def create_python_project(self, name="python_project"):

        project_path = self.projects_path / name

        if project_path.exists():
            return f"Project '{name}' already exists."

        project_path.mkdir()

        (project_path / "main.py").write_text(
            'print("Hello from your new project!")'
        )

        (project_path / "config.json").write_text(
            '{\n  "project": "python_project",\n  "version": "0.1"\n}'
        )

        return f"Project created at {project_path}"
