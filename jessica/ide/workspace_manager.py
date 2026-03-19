from pathlib import Path


class WorkspaceManager:

    def __init__(self):

        self.current_project = None

    def open_project(self, project_path):

        path = Path(project_path)

        if not path.exists():
            return "Project not found."

        self.current_project = path

        return f"Workspace opened: {path}"
