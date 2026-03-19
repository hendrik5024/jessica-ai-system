class ConsoleManager:

    console_widget = None

    @classmethod
    def attach_console(cls, widget):
        """
        Attach the GUI console widget.
        """
        cls.console_widget = widget

    @classmethod
    def log(cls, message):
        text = str(message)

        if not cls.console_widget:
            print(text)
            return

        try:
            # Lazy import so core modules don't require PySide6
            from PySide6.QtCore import QThread
            
            # Qt widgets must only be touched from their owning thread.
            if QThread.currentThread() == cls.console_widget.thread():
                cls.console_widget.append(text)
            else:
                # Fallback to stdout when called from worker threads.
                print(text)
        except Exception:
            print(text)
