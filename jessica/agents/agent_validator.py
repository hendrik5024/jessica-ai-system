import importlib
import traceback


class AgentValidator:

    def validate(self, module_path, class_name):

        try:

            importlib.invalidate_caches()
            module = importlib.import_module(module_path)

            agent_class = getattr(module, class_name)

            agent = agent_class()

            result = agent.run("test")

            return True, result

        except Exception:

            return False, traceback.format_exc()
