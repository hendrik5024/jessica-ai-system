import ast


class RefactorAnalyzer:

    def analyze(self, file_path):

        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)

        issues = []

        function_names = []

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):

                start = node.lineno
                end = node.end_lineno if hasattr(node, "end_lineno") else start
                length = end - start

                # shorter threshold for detection
                if length > 25:
                    issues.append(
                        f"Function '{node.name}' is quite long ({length} lines)."
                    )

                # too many parameters
                if len(node.args.args) > 4:
                    issues.append(
                        f"Function '{node.name}' has many parameters ({len(node.args.args)})."
                    )

                function_names.append(node.name)

        # duplicate functions
        duplicates = set([f for f in function_names if function_names.count(f) > 1])

        for dup in duplicates:
            issues.append(f"Duplicate function name detected: '{dup}'.")

        # detect imports
        imports = []
        names = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)

            if isinstance(node, ast.Name):
                names.append(node.id)

        for imp in imports:
            if imp not in names:
                issues.append(f"Import '{imp}' appears unused.")

        return issues
