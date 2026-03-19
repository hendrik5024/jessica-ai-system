import os
import time
from datetime import datetime


def _ensure_offscreen_qt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


_ensure_offscreen_qt()

from PySide6.QtWidgets import QApplication

from jessica.gui.main_window import JessicaMainWindow
import jessica.memory.episodic_memory as episodic_module
import jessica.memory.knowledge_memory as knowledge_module


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


def test_gui_semantic_knowledge_birthplace_and_age_recall(tmp_path, monkeypatch):
    episodic_file = tmp_path / "episodic_memory.json"
    knowledge_file = tmp_path / "knowledge_memory.json"

    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(episodic_file))
    monkeypatch.setattr(knowledge_module, "KNOWLEDGE_FILE", str(knowledge_file))

    app = QApplication.instance() or QApplication([])
    window = JessicaMainWindow()

    try:
        count = window.chat_display.toPlainText().count("Jessica: ")

        prompts = [
            "I was born in South Africa",
            "Where was I born?",
            "I was born in 1990",
            "How old am I?",
        ]

        for prompt in prompts:
            window.input_box.setText(prompt)
            window.send_message()

            ok, count = _wait_for_next_response(app, window, count)
            assert ok, f"Timed out waiting for response to: {prompt}"

        chat = window.chat_display.toPlainText()

        expected_age = datetime.now().year - 1990
        assert "You told me earlier that you were born in South Africa." in chat
        assert f"You were born in 1990, which makes you {expected_age} years old." in chat

    finally:
        window.close()
        app.processEvents()


def test_gui_semantic_birthplace_overwrite_uses_latest_fact(tmp_path, monkeypatch):
    episodic_file = tmp_path / "episodic_memory.json"
    knowledge_file = tmp_path / "knowledge_memory.json"

    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(episodic_file))
    monkeypatch.setattr(knowledge_module, "KNOWLEDGE_FILE", str(knowledge_file))

    app = QApplication.instance() or QApplication([])
    window = JessicaMainWindow()

    try:
        count = window.chat_display.toPlainText().count("Jessica: ")

        prompts = [
            "I was born in South Africa",
            "I was born in Namibia",
            "Where was I born?",
        ]

        for prompt in prompts:
            window.input_box.setText(prompt)
            window.send_message()

            ok, count = _wait_for_next_response(app, window, count)
            assert ok, f"Timed out waiting for response to: {prompt}"

        chat = window.chat_display.toPlainText()

        assert "You told me earlier that you were born in Namibia." in chat

    finally:
        window.close()
        app.processEvents()
