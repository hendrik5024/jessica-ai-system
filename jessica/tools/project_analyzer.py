import os


class ProjectAnalyzer:

    EXCLUDED_FOLDERS = {
        ".venv",
        "__pycache__",
        "site-packages",
        ".git",
        "node_modules"
    }

    def scan_project(self, root_path):

        summary = {
            "python_files": 0,
            "folders": 0,
            "modules": [],
            "lines_of_code": 0
        }

        for root, dirs, files in os.walk(root_path):

            # Remove excluded folders from scan
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_FOLDERS]

            summary["folders"] += len(dirs)

            for file in files:

                if file.endswith(".py"):

                    summary["python_files"] += 1

                    module_name = file.replace(".py", "")
                    summary["modules"].append(module_name)

                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            summary["lines_of_code"] += sum(1 for _ in f)
                    except:
                        pass

        return summary

    def detect_main_modules(self, root_path):
        """
        Detect main module directories (cognition, gui, tools, etc).
        """
        main_modules = []
        
        try:
            for item in os.listdir(root_path):
                item_path = os.path.join(root_path, item)
                if os.path.isdir(item_path) and item not in self.EXCLUDED_FOLDERS:
                    if not item.startswith('.') and not item.startswith('__'):
                        init_file = os.path.join(item_path, '__init__.py')
                        if os.path.exists(init_file):
                            main_modules.append(item)
        except Exception as e:
            pass

        return main_modules
