import os
import time


def _ensure_offscreen_qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


_ensure_offscreen_qt()

from PySide6.QtWidgets import QApplication

from jessica.gui.main_window import JessicaMainWindow


def _wait_for_next_response(app, window, previous_count, timeout=25):
    deadline = time.time() + timeout

    while time.time() < deadline:
        app.processEvents()
        chat = window.chat_display.toPlainText()
        current_count = chat.count("Jessica: ")

        if current_count > previous_count:
            return True, current_count

        time.sleep(0.05)

    return False, previous_count


def test_gui_time_queries_use_internal_time_path():
    app = QApplication.instance() or QApplication([])
    window = JessicaMainWindow()

    try:
        prompts = [
            "What is the time?",
            "Can you check system time?",
        ]

        count = window.chat_display.toPlainText().count("Jessica: ")

        for prompt in prompts:
            window.input_box.setText(prompt)
            window.send_message()

            ok, count = _wait_for_next_response(app, window, count)
            assert ok, f"Timed out waiting for response to: {prompt}"

        chat = window.chat_display.toPlainText()

        assert chat.count("The current system time is") >= 2
        assert "According to my knowledge" not in chat

    finally:
        window.close()
        app.processEvents()
