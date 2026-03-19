import io
import os
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from jessica.intelligence.debug_engine import DebugEngine
from logger import log_event


class SandboxRunner:

    def run_python_project(self, project_path):

        project_path = Path(project_path).resolve()
        main_file = project_path / "main.py"

        if not main_file.exists():
            return "Error: main.py not found in project."

        debugger = DebugEngine()
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        previous_cwd = Path.cwd()
        previous_sys_path = list(sys.path)

        try:
            # Run the project script in-process so we can capture exact traceback details.
            code = main_file.read_text(encoding="utf-8")
            compiled = compile(code, str(main_file), "exec")
            exec_globals = {
                "__name__": "__main__",
                "__file__": str(main_file),
            }

            os.chdir(project_path)
            sys.path.insert(0, str(project_path.resolve()))

            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(compiled, exec_globals)

            output = stdout_buffer.getvalue().strip()
            errors = stderr_buffer.getvalue().strip()

            response = []
            response.append("Execution finished.\n")

            if output:
                response.append(f"Output:\n{output}\n")

            if errors:
                response.append(f"Errors:\n{errors}\n")

            return "\n".join(response)

        except Exception:
            info = debugger.record_exception(sys.exc_info())
            trace = traceback.format_exc()

            # Restore runtime context before logging so root-level config import resolves correctly.
            os.chdir(previous_cwd)
            sys.path = previous_sys_path

            log_event(
                "execution_error | "
                f"file={info['file']} | "
                f"function={info['function']} | "
                f"line={info['line']} | "
                f"error={info['error']}\n{trace}"
            )

            return f"""
Execution error detected.

File: {info['file']}
Function: {info['function']}
Line: {info['line']}

Error:
{info['error']}
"""

        finally:
            os.chdir(previous_cwd)
            sys.path = previous_sys_path
