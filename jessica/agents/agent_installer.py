import json
import shutil
from pathlib import Path


class AgentInstaller:

    @staticmethod
    def _update_state(agent_dir, state):

        config_path = Path(agent_dir) / "config.json"
        if not config_path.exists():
            return

        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["state"] = state
            config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        except Exception:
            # Keep install/reject flow resilient even if config metadata is malformed.
            return

    def install(self, sandbox_path):

        sandbox = Path(sandbox_path)
        if sandbox.is_file():
            sandbox = sandbox.parent

        target_root = Path("jessica/agents")
        target_root.mkdir(parents=True, exist_ok=True)
        target = target_root / sandbox.name

        if target.exists():
            shutil.rmtree(target)

        shutil.move(str(sandbox), str(target))
        self._update_state(target, "active")

        return str(target)

    def reject(self, sandbox_path):

        sandbox = Path(sandbox_path)
        if sandbox.is_file():
            sandbox = sandbox.parent

        rejected_root = Path("jessica/sandbox_agents/rejected")
        rejected_root.mkdir(parents=True, exist_ok=True)
        target = rejected_root / sandbox.name

        if target.exists():
            shutil.rmtree(target)

        shutil.move(str(sandbox), str(target))
        self._update_state(target, "rejected")

        return str(target)
