import logging
from memory.memory_manager import MemoryManager


class Reflection:
    def __init__(self):
        try:
            self.memory = MemoryManager()
        except Exception as e:
            logging.error(f"Memory initialization failed: {e}")
            self.memory = None

    def process(self, context, action, result):
        logging.info(f"INPUT: {context}")
        logging.info(f"ACTION: {action}")
        logging.info(f"RESULT: {result}")

        try:
            if self.memory is not None:
                response = result.get("response") if isinstance(result, dict) else result
                self.memory.save_interaction(
                    context["raw_input"],
                    context["intent"],
                    response,
                )
        except Exception as e:
            logging.error(f"Memory save failed: {e}")
