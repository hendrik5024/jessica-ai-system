from typing import Any


class ExperimentManager:
    """Runs a scientific hypothesis-test-record cycle.

    Architecture position:
        Goals → Planner → HypothesisAgent
            → ExperimentManager
                → Sandbox (run experiment code)
                → KnowledgeMemory (store result)
            → CriticAgent
        → Planner generates next hypothesis
    """

    def __init__(
        self,
        sandbox: Any,
        knowledge_memory: Any,
        experimental_sandbox: Any | None = None,
    ) -> None:
        self.sandbox = sandbox
        self.knowledge = knowledge_memory
        self.experimental_sandbox = experimental_sandbox
        self._experiment_count = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_experiment(self, hypothesis: str, code: str) -> dict[str, Any]:
        """Deploy and execute *code* in the sandbox, record results.

        Returns a record with:
            hypothesis  — the original hypothesis string
            result      — raw sandbox execution result dict
            success     — True if execution returned returncode 0
            summary     — human-readable one-liner for KnowledgeMemory
        """
        print(f"\nRunning experiment for hypothesis: {hypothesis}")

        if self.experimental_sandbox is not None and hasattr(self.experimental_sandbox, "run_experiment"):
            result = self.experimental_sandbox.run_experiment(code)
        else:
            agent_name = self._hypothesis_to_slug(hypothesis)
            file_path = self.sandbox.deploy_agent(agent_name, code)
            result = self.sandbox.execute_agent(file_path)

        self._experiment_count += 1

        success = bool(
            result.get("status") == "success"
            or (
                result.get("returncode") == 0
                and not result.get("error")
            )
        )

        stdout_preview = (result.get("stdout") or "").strip()[:200]
        summary = (
            f"[PASS] {hypothesis}: {stdout_preview}"
            if success
            else f"[FAIL] {hypothesis}: {result.get('stderr') or result.get('error', 'unknown error')}"
        )

        record: dict[str, Any] = {
            "hypothesis": hypothesis,
            "result": result,
            "success": success,
            "summary": summary,
        }

        return record

    @property
    def experiment_count(self) -> int:
        return self._experiment_count

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hypothesis_to_slug(hypothesis: str) -> str:
        """Convert hypothesis text to a safe filename slug."""
        import re
        slug = re.sub(r"[^a-z0-9]+", "_", hypothesis.strip().lower()).strip("_")
        return f"exp_{slug[:40]}"
