import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


class FileExplorer(QTreeWidget):

    def __init__(self, root="."):
        super().__init__()

        self.setHeaderLabel("Project Files")
        self.root = root

        self.populate()

    def populate(self):

        self.clear()

        for root_dir, dirs, files in os.walk(self.root):

            parent = self.invisibleRootItem()

            for d in dirs:
                item = QTreeWidgetItem(parent)
                item.setText(0, d)

            for f in files:
                if f.endswith(".py"):
                    item = QTreeWidgetItem(parent)
                    item.setText(0, f)
                    item.setData(0, Qt.UserRole, os.path.join(root_dir, f))
