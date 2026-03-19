import os
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import QApplication
from jessica.gui.main_window import JessicaMainWindow


def main():
    app = QApplication(sys.argv)

    window = JessicaMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
