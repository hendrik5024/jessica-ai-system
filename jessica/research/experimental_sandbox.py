import os
import subprocess
import sys
import tempfile
import time
import uuid
from typing import Any


class ExperimentalSandbox:
    """Runs experiment code safely in an isolated subprocess."""

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def run_experiment(self, code: str) -> dict[str, Any]:
        """Execute Python code safely and capture results."""

        experiment_id = f"experiment_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        temp_script_path = ""

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as temp_script:
                temp_script.write(code)
                temp_script_path = temp_script.name

            result = subprocess.run(
                [sys.executable, temp_script_path],
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout,
            )

            duration = time.time() - start_time
            status = "success" if result.returncode == 0 else "failed"

            return {
                "experiment_id": experiment_id,
                "status": status,
                "stdout": (result.stdout or "").strip(),
                "stderr": (result.stderr or "").strip(),
                "duration": duration,
                "returncode": result.returncode,
                "code": code,
            }

        except subprocess.TimeoutExpired:
            return {
                "experiment_id": experiment_id,
                "status": "timeout",
                "stdout": "",
                "stderr": "Execution exceeded sandbox timeout",
                "duration": float(self.timeout),
                "returncode": None,
                "code": code,
            }

        except (OSError, RuntimeError, ValueError, TypeError) as exc:
            return {
                "experiment_id": experiment_id,
                "status": "error",
                "stdout": "",
                "stderr": str(exc),
                "duration": 0.0,
                "returncode": None,
                "code": code,
            }

        finally:
            if temp_script_path and os.path.exists(temp_script_path):
                try:
                    os.remove(temp_script_path)
                except OSError:
                    pass
