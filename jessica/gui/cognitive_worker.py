# PySide6 imports moved inside __init__ to make GUI optional
try:
    from PySide6.QtCore import QObject, Signal, Slot
except ImportError:
    # Fallback stubs when PySide6 not available
    class QObject:
        pass
    class Signal:
        def __init__(self, *args):
            pass
        def emit(self, *args):
            pass
    def Slot(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
import asyncio
import os
import sys
import threading
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import load_settings
from jessica.cognition.background_engine import background_thinking
from jessica.cognition.telemetry import pop_next_insight
from jessica.core.jessica_core import JessicaCore
from jessica.memory.memory_manager import init_memory
from logger import get_internal_logger


class CognitiveWorker(QObject):

    response_ready = Signal(str)
    insight_generated = Signal(str)

    def __init__(self):
        super().__init__()

        init_memory()
        settings = load_settings()
        logger = get_internal_logger(settings.log_file)
        self.jessica = JessicaCore(settings=settings, logger=logger)

        threading.Thread(
            target=self.background_loop,
            daemon=True
        ).start()

    @Slot(str)
    def process_message(self, message):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            try:
                response = loop.run_until_complete(
                    self.jessica.handle_input(message)
                )
            except Exception as e:
                response = f"Jessica encountered an internal error: {str(e)}"
                print("WORKER ERROR:", e)
            self.response_ready.emit(response)
            self._emit_pending_insights()
        except Exception as exc:
            self.response_ready.emit(f"Error: {exc}")
        finally:
            loop.close()

    def _emit_pending_insights(self):
        while True:
            insight = pop_next_insight()

            if not insight:
                break

            self.insight_generated.emit(insight)

    def background_loop(self):
        while True:
            insight = background_thinking()

            if insight:
                self.insight_generated.emit(insight)

            time.sleep(10)
