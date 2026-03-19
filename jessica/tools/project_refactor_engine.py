import os


class ProjectRefactorEngine:

    EXCLUDED_DIRS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        "node_modules",
        "build",
        "dist",
    }

    def scan_project(self, root_path, analyzer, max_improvements=200):

        improvements = []

        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]

            for file in files:

                if file.endswith(".py"):

                    path = os.path.join(root, file)

                    try:
                        issues = analyzer.analyze(path)

                        if issues:
                            improvements.append({
                                "file": path,
                                "issues": issues
                            })

                            if len(improvements) >= max_improvements:
                                return improvements

                    except Exception:
                        pass

        return improvements
