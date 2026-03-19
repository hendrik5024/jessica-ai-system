import ast
from pathlib import Path


class DependencyGraph:

    def __init__(self, root="."):
        self.root = Path(root)
        self.calls = {}

    def build(self):

        self.calls = {}
        
        skip_dirs = {'.venv', 'node_modules', '.git', '__pycache__', 'venv', 'env'}

        for file in self.root.rglob("*.py"):
            
            # Skip files in ignored directories
            if any(part in skip_dirs for part in file.parts):
                continue

            try:

                tree = ast.parse(file.read_text())

                functions = {}

                for node in ast.walk(tree):

                    if isinstance(node, ast.FunctionDef):

                        called = []

                        for sub in ast.walk(node):

                            if isinstance(sub, ast.Call):

                                if isinstance(sub.func, ast.Name):
                                    called.append(sub.func.id)

                                elif isinstance(sub.func, ast.Attribute):
                                    called.append(sub.func.attr)

                        functions[node.name] = called

                if functions:
                    self.calls[str(file)] = functions

            except Exception:
                pass

    def find_function_usage(self, name):

        results = []

        for file, funcs in self.calls.items():

            for func, calls in funcs.items():

                if name in calls:
                    results.append(f"{func} → {file}")

        return results
