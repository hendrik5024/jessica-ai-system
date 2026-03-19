class CodeEditorEngine:

    def replace_function(self, source_code, function_name, new_code):

        lines = source_code.splitlines()

        start = None
        indent = None

        for i, line in enumerate(lines):

            if f"def {function_name}" in line:
                start = i
                indent = len(line) - len(line.lstrip())
                break

        if start is None:
            return source_code

        end = start + 1

        for i in range(start + 1, len(lines)):

            current_indent = len(lines[i]) - len(lines[i].lstrip())

            if current_indent <= indent and lines[i].strip():
                break

            end = i

        new_lines = lines[:start] + new_code.splitlines() + lines[end + 1:]

        return "\n".join(new_lines)
