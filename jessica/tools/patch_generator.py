import difflib


class PatchGenerator:

    def generate_patch(self, old_code, new_code):

        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm=""
        )

        return "\n".join(diff)
