from concurrent.futures import ThreadPoolExecutor


class AgentOrchestrator:

    def __init__(self, registry):

        self.registry = registry

    def run_parallel(self, agent_names, task, context=None):

        results = {}

        agents = [self.registry.get(name) for name in agent_names if self.registry.get(name) is not None]

        with ThreadPoolExecutor(max_workers=len(agents)) as executor:

            futures = {
                executor.submit(agent.run, task, context): agent.name
                for agent in agents
            }

            for future in futures:

                name = futures[future]

                try:
                    results[name] = future.result()
                except Exception as e:
                    results[name] = f"Error: {e}"

        return results
