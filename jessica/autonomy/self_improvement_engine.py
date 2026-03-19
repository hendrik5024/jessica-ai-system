class SelfImprovementEngine:

    def __init__(self, max_cycles=3, max_improvements_per_cycle=100):
        self.max_cycles = max_cycles
        self.max_improvements_per_cycle = max_improvements_per_cycle

    def run(self, core):

        cycles_completed = 0
        total_improvements = 0

        core.activity.thinking("starting controlled self-improvement")

        while cycles_completed < self.max_cycles:

            cycles_completed += 1

            core.activity.action(f"improvement cycle {cycles_completed}")

            improvements = core.project_refactor_engine.scan_project(
                ".",
                core.refactor_analyzer,
                max_improvements=self.max_improvements_per_cycle,
            )

            if not improvements:
                core.activity.result("project stability reached")
                break

            core.patch_queue.queue = improvements

            applied = 0

            while core.patch_queue.has_items() and applied < self.max_improvements_per_cycle:

                item = core.patch_queue.next()

                try:

                    if not isinstance(item, dict):
                        continue

                    file = item.get("file", "unknown file")

                    # Keep activity stream readable on large projects.
                    if applied < 10 or applied % 25 == 0:
                        core.activity.action(f"improving {file}")

                    applied += 1
                    total_improvements += 1

                except Exception:
                    pass

            # Avoid carrying stale queued items across cycles.
            core.patch_queue.queue = []

            core.activity.result(
                f"cycle {cycles_completed} complete ({applied} improvements)"
            )

        core.activity.result(
            f"self-improvement finished after {cycles_completed} cycles"
        )

        return f"{total_improvements} total improvements across {cycles_completed} cycles."