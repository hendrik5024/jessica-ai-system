from config import load_settings
from jessica.core.jessica_core import JessicaCore
from logger import get_internal_logger


def main() -> None:
    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    print("Jessica CSI (Phase 103) is running. Type 'exit' to quit.")

    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Jessica: Goodbye.")
            break

        response = core.handle_input(user_input)
        print(f"Jessica: {response}")


if __name__ == "__main__":
    main()