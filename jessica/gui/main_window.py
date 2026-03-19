import os

from config import load_settings
from jessica.gui.console_manager import ConsoleManager
from jessica.gui.settings_tab import SettingsTab
from jessica.ide.ide_manager import IDEManager
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QLabel,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
)
from PySide6.QtCore import QThread, Signal, QTimer, Qt
from jessica.cognition.telemetry import get_telemetry
from jessica.gui.cognitive_worker import CognitiveWorker
from jessica.tools.system.system_monitor import get_system_status

class JessicaMainWindow(QMainWindow):
    message_submitted = Signal(str)

    def __init__(self):
        super().__init__()
        self.ide_manager = IDEManager()

        self.setWindowTitle("Jessica Cognitive Interface")
        self.setGeometry(100, 100, 900, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tab widgets
        self.chat_tab = QWidget()
        self.monitor_tab = QWidget()
        self.insight_tab = QWidget()
        self.log_tab = QWidget()
        self.console_tab = QWidget()
        self.ide_tab = self.create_ide_tab()

        # Add tabs
        self.tabs.addTab(self.chat_tab, "Chat")
        self.tabs.addTab(self.monitor_tab, "Monitor")
        self.tabs.addTab(self.insight_tab, "Insights")
        self.tabs.addTab(self.log_tab, "Logs")
        self.tabs.addTab(self.console_tab, "Console")
        self.tabs.addTab(self.ide_tab, "IDE")
        self.tabs.addTab(SettingsTab(), "Settings")

        chat_layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type message to Jessica...")
        self.input_box.returnPressed.connect(self.send_message)

        self.status_label = QLabel("Jessica: Idle")

        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(self.input_box)
        chat_layout.addWidget(self.status_label)

        self.chat_tab.setLayout(chat_layout)

        monitor_layout = QVBoxLayout()

        self.status_panel = QTextEdit()
        self.status_panel.setReadOnly(True)

        monitor_layout.addWidget(self.status_panel)

        self.monitor_tab.setLayout(monitor_layout)

        insight_layout = QVBoxLayout()

        self.insight_display = QTextEdit()
        self.insight_display.setReadOnly(True)

        insight_layout.addWidget(self.insight_display)

        self.insight_tab.setLayout(insight_layout)

        log_layout = QVBoxLayout()

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)

        log_layout.addWidget(self.log_display)

        self.log_tab.setLayout(log_layout)

        console_layout = QVBoxLayout()

        self.console_display = QTextEdit()
        self.console_display.setReadOnly(True)

        console_layout.addWidget(self.console_display)

        self.console_tab.setLayout(console_layout)

        # Attach console to ConsoleManager
        ConsoleManager.attach_console(self.console_display)

        settings = load_settings()
        self.log_file_path = os.path.abspath(settings.log_file)
        self.log_file_position = 0
        self.max_log_lines = 200
        self.log_keywords = (
            "state_change",
            "intent_detected",
            "observer",
            "cognitive_friction",
            "inquiry_engine",
            "csi_pipeline",
            "persona_selected",
            "response_sent",
            "error",
        )
        self.log_display.setPlaceholderText(f"Watching {self.log_file_path}")

        # Create cognitive worker thread
        self.thread = QThread()
        self.worker = CognitiveWorker()

        self.worker.moveToThread(self.thread)

        self.message_submitted.connect(self.worker.process_message)
        self.thread.start()

        self.worker.response_ready.connect(self.display_response)
        self.worker.insight_generated.connect(self.display_insight)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status_panel)
        self.timer.start(1000)
        self.update_status_panel()

    def create_ide_tab(self):

        ide_tab = QWidget()

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # Explorer (left)
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("Project Files")

        # Code editor (center)
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("Code editor")

        # Jessica chat panel (right) - with input
        chat_panel = QWidget()
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        self.ide_chat = QTextEdit()
        self.ide_chat.setReadOnly(True)
        self.ide_chat.setPlaceholderText("Ask Jessica about your code...")
        
        self.ide_input_box = QLineEdit()
        self.ide_input_box.setPlaceholderText("Type message to Jessica...")
        self.ide_input_box.returnPressed.connect(self.send_ide_message)
        
        chat_layout.addWidget(self.ide_chat)
        chat_layout.addWidget(self.ide_input_box)
        chat_panel.setLayout(chat_layout)

        # Bottom split: terminal sessions (left) + execution console (right)
        bottom_layout = QHBoxLayout()

        terminal_panel = QWidget()
        terminal_panel_layout = QVBoxLayout()
        terminal_panel_layout.setContentsMargins(0, 0, 0, 0)

        terminal_label = QLabel("Terminal Sessions")
        self.terminal_tabs = QTabWidget()

        self.terminal_powershell = QTextEdit()
        self.terminal_powershell.setReadOnly(True)
        self.terminal_powershell.setPlaceholderText("PowerShell output...")

        self.terminal_python = QTextEdit()
        self.terminal_python.setReadOnly(True)
        self.terminal_python.setPlaceholderText("Python output...")

        self.terminal_general = QTextEdit()
        self.terminal_general.setReadOnly(True)
        self.terminal_general.setPlaceholderText("General terminal output...")

        self.terminal_tabs.addTab(self.terminal_powershell, "PowerShell")
        self.terminal_tabs.addTab(self.terminal_python, "Python")
        self.terminal_tabs.addTab(self.terminal_general, "Terminal")

        terminal_panel_layout.addWidget(terminal_label)
        terminal_panel_layout.addWidget(self.terminal_tabs)
        terminal_panel.setLayout(terminal_panel_layout)

        self.ide_terminal = QTextEdit()
        self.ide_terminal.setReadOnly(True)
        self.ide_terminal.setPlaceholderText("Execution / console output...")

        top_layout.addWidget(self.project_tree, 1)
        top_layout.addWidget(self.code_editor, 3)
        top_layout.addWidget(chat_panel, 1)

        bottom_layout.addWidget(terminal_panel, 2)
        bottom_layout.addWidget(self.ide_terminal, 1)

        main_layout.addLayout(top_layout, 3)
        main_layout.addLayout(bottom_layout, 2)

        ide_tab.setLayout(main_layout)

        self._populate_project_tree("projects")
        self.project_tree.itemDoubleClicked.connect(
            lambda item, _column: self.open_file_in_editor(item.data(0, Qt.UserRole) or item.text(0))
        )

        return ide_tab

    def _populate_project_tree(self, root_path):
        self.project_tree.clear()
        root_path = os.path.abspath(root_path)

        if not os.path.exists(root_path):
            return

        root_name = os.path.basename(root_path) or root_path
        root_item = QTreeWidgetItem([root_name])
        root_item.setData(0, Qt.UserRole, root_path)
        self.project_tree.addTopLevelItem(root_item)

        self._add_tree_children(root_item, root_path)
        self.project_tree.expandItem(root_item)

    def _add_tree_children(self, parent_item, parent_path):
        try:
            children = sorted(os.listdir(parent_path))
        except OSError:
            return

        for child in children:
            child_path = os.path.join(parent_path, child)
            child_item = QTreeWidgetItem([child])
            child_item.setData(0, Qt.UserRole, child_path)
            parent_item.addChild(child_item)

            if os.path.isdir(child_path):
                self._add_tree_children(child_item, child_path)

    def send_message(self):
        message = self.input_box.text().strip()
        if not message:
            return

        self.chat_display.append(f"You: {message}")

        self.status_label.setText("Jessica: Thinking...")

        self.message_submitted.emit(message)

        self.input_box.clear()

    def send_ide_message(self):
        message = self.ide_input_box.text().strip()
        if not message:
            return

        self.ide_chat.append(f"You: {message}")
        self._append_terminal_text("general", f"> {message}")

        self.message_submitted.emit(message)

        self.ide_input_box.clear()

    def display_response(self, response):
        self.chat_display.append(f"Jessica: {response}")
        self.status_label.setText("Jessica: Idle")

        # Keep IDE chat and execution panes in sync with responses.
        self.ide_chat.append(f"Jessica: {response}")
        self.ide_terminal.append(str(response))

        terminal_channel = self._detect_terminal_channel(str(response))
        self._append_terminal_text(terminal_channel, str(response))

    def _detect_terminal_channel(self, text):
        lowered = text.lower()

        if "powershell" in lowered or "pwsh" in lowered:
            return "powershell"

        if "traceback" in lowered or "python" in lowered or ".py" in lowered:
            return "python"

        return "general"

    def _append_terminal_text(self, channel, text):
        if channel == "powershell":
            self.terminal_powershell.append(text)
            return

        if channel == "python":
            self.terminal_python.append(text)
            return

        self.terminal_general.append(text)

    def display_insight(self, insight):
        self.insight_display.append(f"Jessica Insight: {insight}")

    def update_status_panel(self):
        data = get_telemetry()

        try:
            status = get_system_status()
            cpu_usage = status["cpu"]
            memory_usage = status["memory"]
        except Exception:
            cpu_usage = "N/A"
            memory_usage = "N/A"

        text = (
            "Jessica Cognitive Monitor\n"
            "-------------------------\n"
            f"State: {data['state']}\n"
            f"Intent: {data['intent']}\n"
            f"Persona: {data['persona']}\n"
            f"Risk Level: {data['risk']}\n"
            f"CPU: {cpu_usage}%\n"
            f"Memory: {memory_usage}%\n"
        )

        self.status_panel.setText(text)
        self.update_log_panel()

    def _is_relevant_log(self, line):
        return any(keyword in line for keyword in self.log_keywords)

    def update_log_panel(self):
        if not os.path.exists(self.log_file_path):
            return

        try:
            current_size = os.path.getsize(self.log_file_path)

            if current_size < self.log_file_position:
                self.log_file_position = 0
                self.log_display.clear()

            with open(self.log_file_path, "r", encoding="utf-8", errors="ignore") as handle:
                handle.seek(self.log_file_position)
                new_lines = handle.readlines()
                self.log_file_position = handle.tell()

            filtered_lines = [line.strip() for line in new_lines if self._is_relevant_log(line)]

            if not filtered_lines:
                return

            existing_lines = self.log_display.toPlainText().splitlines()
            combined_lines = (existing_lines + filtered_lines)[-self.max_log_lines:]
            self.log_display.setPlainText("\n".join(combined_lines))

        except Exception:
            return

    def open_file_in_editor(self, filename):
        if not filename or not os.path.isfile(filename):
            return

        try:
            content = self.ide_manager.open_file(filename)
            if content == "File not found.":
                return
            self.code_editor.setPlainText(content)
            self.ide_chat.append(f"Opening {os.path.basename(filename)} in editor")
        except OSError:
            return

    def closeEvent(self, event):
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)
