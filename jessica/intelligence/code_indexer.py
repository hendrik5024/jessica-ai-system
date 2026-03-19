from pathlib import Path
import ast


class CodeIndexer:

    def __init__(self, root="."):

        self.root = Path(root)
        self.index = {}

    def build_index(self):

        self.index = {}

        for file in self.root.rglob("*.py"):

            try:

                tree = ast.parse(file.read_text())

                functions = []
                classes = []

                for node in ast.walk(tree):

                    if isinstance(node, ast.FunctionDef):
                        functions.append(node.name)

                    if isinstance(node, ast.ClassDef):
                        classes.append(node.name)

                self.index[str(file)] = {
                    "functions": functions,
                    "classes": classes
                }

            except Exception:
                pass

        return f"Indexed {len(self.index)} Python files."

    def find_symbol(self, name):

        results = []

        for file, data in self.index.items():

            if name in data["functions"] or name in data["classes"]:
                results.append(file)

        return results

    def get_functions(self, file_name):

        for file, data in self.index.items():

            if file_name in file:
                return data["functions"]

        return []

    def get_classes(self, file_name):

        for file, data in self.index.items():

            if file_name in file:
                return data["classes"]

        return []
