import ast
import os


class CodeAnalyzer:

    def find_file(self, filename, root="."):

        matches = []

        for root_dir, dirs, files in os.walk(root):

            if filename in files:
                path = os.path.join(root_dir, filename)
                matches.append(path)

        if not matches:
            return None

        # Prefer files inside "jessica" directory
        preferred = [m for m in matches if "jessica" in m.lower()]

        if preferred:
            matches = preferred

        # Choose the largest file (likely the real implementation)
        matches.sort(key=lambda p: os.path.getsize(p), reverse=True)

        return matches[0]


    def analyze_file(self, filename):

        path = self.find_file(filename)

        if not path:
            raise Exception(f"{filename} not found in project")

        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)

        functions = []
        classes = []

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

            if isinstance(node, ast.ClassDef):
                classes.append(node.name)

        line_count = len(source.splitlines())

        return {
            "file_path": path,
            "lines": line_count,
            "functions": functions,
            "classes": classes
        }
