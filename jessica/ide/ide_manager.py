from pathlib import Path


class IDEManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.workspace = None
        self.current_file = None
        self._initialized = True

    def open_file(self, file_path):

        file_path = Path(file_path)

        if not file_path.exists():
            return "File not found."

        # Set workspace to parent folder
        self.workspace = file_path.parent

        self.current_file = file_path

        return file_path.read_text()
