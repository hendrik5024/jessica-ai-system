from pathlib import Path


class ArchitectureMapper:

    def __init__(self, root="."):
        self.root = Path(root)
        self.architecture = {}

    def build_architecture(self):

        self.architecture = {}

        for folder in self.root.iterdir():

            if folder.is_dir():

                modules = []

                for file in folder.glob("*.py"):
                    modules.append(file.stem)

                if modules:
                    self.architecture[folder.name] = modules

        # Include top-level modules in the selected root.
        root_modules = [file.stem for file in self.root.glob("*.py")]
        if root_modules:
            self.architecture["root"] = root_modules

        # Convenience grouping for workflow-related modules.
        workflow_modules = [name for name in root_modules if name.startswith("workflow")]
        if workflow_modules:
            self.architecture["workflow_engine"] = workflow_modules

        return self.architecture

    def describe_module(self, module_name):

        for subsystem, modules in self.architecture.items():

            if module_name in modules:
                return f"{module_name} belongs to subsystem '{subsystem}'"

        return "Module not found."
