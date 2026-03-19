import sys
from typing import Any


class CognitiveDashboard:

    def refresh(self, state: dict[str, Any]) -> None:
        """Single-line in-place HUD — rewrites the same terminal line each cycle."""
        goal = str(state.get("goal", "None"))[:40]
        line = (
            f"Goal: {goal} | "
            f"Cycle: {state.get('cycle', 0)} | "
            f"Agent: {state.get('agent', 'None')} | "
            f"Model: {state.get('model', 'Unavailable')} | "
            f"Knowledge: {state.get('knowledge_count', 0)} | "
            f"Status: {state.get('status', 'Unknown')}"
        )
        sys.stdout.write("\r" + line.ljust(120))
        sys.stdout.flush()

    def display(self, state: dict[str, Any]) -> None:

        print("\n===============================")
        print("JESSICA COGNITIVE DASHBOARD")
        print("===============================")

        print(f"Active Goal: {state.get('goal', 'None')}")
        print(f"Current Cycle: {state.get('cycle', 0)}")
        print(f"Current Task: {state.get('task', 'None')}")
        print(f"Agent Running: {state.get('agent', 'None')}")
        print(f"Model Used: {state.get('model', 'Unavailable')}")

        print(f"Sandbox Experiments: {state.get('sandbox_experiments', 0)} running")
        print(f"KnowledgeMemory Entries: {state.get('knowledge_count', 0)}")

        print("Agents Installed:")
        agents = state.get('agents', [])
        if agents:
            for agent in agents:
                print(f"- {agent}")
        else:
            print("- none")

        print(f"System Status: {state.get('status', 'Unknown')}")
        print("===============================\n")
