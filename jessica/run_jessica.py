import asyncio
import os
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import load_settings
from jessica.core.jessica_core import JessicaCore
from jessica.memory.memory_manager import init_memory
from logger import get_internal_logger


def run_terminal():
    init_memory()
    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    jessica = JessicaCore(settings=settings, logger=logger)

    print("\nJessica Phase 103 - Terminal Mode")
    print("Type 'exit' to quit\n")

    while True:
        try:
            user_input = input("You: ")

            if user_input.lower() == "exit":
                print("Jessica shutting down.")
                break

            response = asyncio.run(jessica.handle_input(user_input))
            print(response)

        except KeyboardInterrupt:
            print("\nInterrupted. Returning to IDLE.")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    run_terminal()
