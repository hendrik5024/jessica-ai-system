import keyword
import re

from PySide6.QtGui import (
    QColor,
    QFont,
    QKeySequence,
    QShortcut,
    QSyntaxHighlighter,
    QTextCharFormat,
)
from PySide6.QtWidgets import QPlainTextEdit


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#005cc5"))
        keyword_format.setFontWeight(QFont.Bold)
        for kw in keyword.kwlist:
            self.rules.append((rf"\\b{kw}\\b", keyword_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#22863a"))
        self.rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', string_format))
        self.rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", string_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a737d"))
        self.rules.append((r"#.*$", comment_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b31d28"))
        self.rules.append((r"\\b\\d+\\b", number_format))

    def highlightBlock(self, text):
        for pattern, text_format in self.rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, text_format)


class CodeEditor(QPlainTextEdit):

    def __init__(self):
        super().__init__()

        font = QFont("Consolas", 11)
        self.setFont(font)

        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.current_file = None

        self.highlighter = PythonHighlighter(self.document())
        self.save_shortcut = QShortcut(QKeySequence.Save, self)
        self.save_shortcut.activated.connect(self.save_file)

    def load_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.setPlainText(f.read())

        self.current_file = path

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.toPlainText())
