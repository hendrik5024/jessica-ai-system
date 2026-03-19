class WorkflowOptimizer:

    def optimize(self, steps):

        optimized = []

        seen = set()

        for step in steps:

            # Remove duplicate steps
            if step in seen:
                continue

            seen.add(step)

            optimized.append(step)

        return optimized
