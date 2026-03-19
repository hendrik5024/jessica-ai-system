from pathlib import Path


class ProjectAnalyzer:

    def analyze(self, path):

        root = Path(path)

        python_files = list(root.rglob("*.py"))
        folders = [p for p in root.rglob("*") if p.is_dir()]

        line_count = 0

        for file in python_files:

            try:
                line_count += len(file.read_text().splitlines())
            except:
                pass

        return (
            f"Project Analysis:\n\n"
            f"Python files: {len(python_files)}\n"
            f"Folders: {len(folders)}\n"
            f"Lines of code: {line_count}"
        )
