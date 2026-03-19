from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QGroupBox,
    QTextEdit,
)


class SettingsTab(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        # Title
        title = QLabel("Jessica Control Center")
        title_font = title.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Execution behavior
        exec_group = QGroupBox("Execution Behavior")
        exec_layout = QVBoxLayout()
        exec_layout.addWidget(QLabel("Execution Mode:"))
        
        mode_combo = QComboBox()
        mode_combo.addItems(["manual", "assisted", "autonomous"])
        exec_layout.addWidget(mode_combo)
        
        exec_group.setLayout(exec_layout)
        layout.addWidget(exec_group)

        # Self-improvement
        improve_group = QGroupBox("Self-Improvement")
        improve_layout = QVBoxLayout()
        improve_layout.addWidget(QLabel("Self-Improvement:"))
        
        improve_combo = QComboBox()
        improve_combo.addItems(["disabled", "approval", "enabled"])
        improve_layout.addWidget(improve_combo)
        
        improve_group.setLayout(improve_layout)
        layout.addWidget(improve_group)

        # Model configuration
        model_group = QGroupBox("Model Configuration")
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("Reasoning Model:"))
        reasoning_combo = QComboBox()
        reasoning_combo.addItems(["phi-3-mini", "llama-2", "mistral"])
        model_layout.addWidget(reasoning_combo)
        
        model_layout.addWidget(QLabel("Coding Model:"))
        coding_combo = QComboBox()
        coding_combo.addItems(["codellama-13b", "starcoder", "deepseek-coder"])
        model_layout.addWidget(coding_combo)
        
        model_layout.addWidget(QLabel("Chat Model:"))
        chat_combo = QComboBox()
        chat_combo.addItems(["capybara-hermes", "zephyr", "neural-chat"])
        model_layout.addWidget(chat_combo)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Workspace behavior
        workspace_group = QGroupBox("Workspace Behavior")
        workspace_layout = QVBoxLayout()
        workspace_layout.addWidget(QLabel("Workspace Behavior:"))
        
        workspace_combo = QComboBox()
        workspace_combo.addItems(["manual", "auto_open", "auto_open_and_build"])
        workspace_layout.addWidget(workspace_combo)
        
        workspace_group.setLayout(workspace_layout)
        layout.addWidget(workspace_group)

        # Info panel
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText(
            "Jessica Control Center\n"
            "========================\n\n"
            "Configure Jessica's behavior, trust levels, and model selection.\n\n"
            "Execution Modes:\n"
            "  • manual: Approval required for all actions\n"
            "  • assisted: Jessica suggests, you decide\n"
            "  • autonomous: Jessica acts independently\n\n"
            "Self-Improvement:\n"
            "  • disabled: No learning\n"
            "  • approval: Learn with your approval\n"
            "  • enabled: Learn automatically\n"
        )
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Stretch to fill remaining space
        layout.addStretch()

        self.setLayout(layout)
