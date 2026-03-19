"""Jessica package entrypoint.

Run:
    python -m jessica         # CLI
    python -m jessica --ui    # Tkinter window (legacy)
    python -m jessica --desktop  # CustomTkinter desktop UI (recommended)
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Sequence

# Allow running this file directly: `python jessica/__main__.py`
if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _run_cli() -> None:
    from jessica.jessica_core import CognitiveManager

    # Lazy import so GUI usage doesn't require TTS deps.
    try:
        from jessica.tts.tts_adapter import speak  # type: ignore
    except Exception:
        speak = None  # type: ignore[assignment]

    brain = CognitiveManager()
    print("Jessica (offline) ready. Type 'exit' to quit.")
    while True:
        try:
            text = input("You: ")
        except EOFError:
            print("EOF received, exiting.")
            break
        if not text:
            continue
        if text.lower() in ("exit", "quit"):
            print("Bye.")
            break

        res = brain.handle_input(text)
        if isinstance(res, dict):
            out = res.get("result") or res.get("output") or res
        else:
            out = res
        if isinstance(out, dict):
            say = out.get("reply") or str(out)
        else:
            say = str(out)

        print("Jessica:", say)
        if speak is not None:
            try:
                speak(str(say))
            except Exception:
                pass


def _run_ui() -> None:
    from jessica.ui.main_tk import main as ui_main

    ui_main()


def _run_desktop() -> None:
    from jessica.ui.desktop_ui import main as desktop_main

    desktop_main()


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m jessica")
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch the legacy Tkinter UI",
    )
    parser.add_argument(
        "--desktop",
        action="store_true",
        help="Launch the CustomTkinter desktop UI (recommended)",
    )
    parser.add_argument(
        "--demo",
        choices=["programming-e2e", "model-e2e", "office-e2e", "browser-e2e", "all"],
        help="Run end-to-end demos: programming-e2e, model-e2e, office-e2e, browser-e2e, or all",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.demo:
        from jessica.demos import run_programming_e2e, run_model_e2e, run_office_e2e, run_browser_e2e

        if args.demo in ("programming-e2e", "all"):
            run_programming_e2e()
        if args.demo in ("model-e2e", "all"):
            run_model_e2e()
        if args.demo in ("office-e2e", "all"):
            run_office_e2e()
        if args.demo in ("browser-e2e", "all"):
            run_browser_e2e()
        return

    if args.desktop:
        _run_desktop()
        return
    if args.ui:
        _run_ui()
        return
    _run_cli()


if __name__ == "__main__":
    main()
