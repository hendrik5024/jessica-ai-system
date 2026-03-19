import os
import time


def _ensure_offscreen_qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


_ensure_offscreen_qt()

from PySide6.QtWidgets import QApplication

from jessica.gui.main_window import JessicaMainWindow
import jessica.memory.episodic_memory as episodic_module


def _wait_for_next_response(app, window, previous_count, timeout=30):
    deadline = time.time() + timeout

    while time.time() < deadline:
        app.processEvents()
        chat = window.chat_display.toPlainText()
        current_count = chat.count("Jessica: ")

        if current_count > previous_count:
            return True, current_count

        time.sleep(0.05)

    return False, previous_count


def test_gui_episodic_recall_for_system_status(tmp_path, monkeypatch):
    memory_file = tmp_path / "episodic_memory.json"
    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(memory_file))

    app = QApplication.instance() or QApplication([])
    window = JessicaMainWindow()

    try:
        count = window.chat_display.toPlainText().count("Jessica: ")

        window.input_box.setText("system status")
        window.send_message()
        ok1, count = _wait_for_next_response(app, window, count)
        assert ok1

        window.input_box.setText("What did we discuss earlier about system status?")
        window.send_message()
        ok2, count = _wait_for_next_response(app, window, count)
        assert ok2

        chat = window.chat_display.toPlainText()

        assert "Earlier discussion:" in chat
        assert "You said: system status" in chat
        assert "I responded: System status:" in chat

    finally:
        window.close()
        app.processEvents()
