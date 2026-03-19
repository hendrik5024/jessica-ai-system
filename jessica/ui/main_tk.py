import tkinter as tk
from typing import Any


class JessicaUI:
    def __init__(self, manager):
        self.manager = manager
        self.root = tk.Tk()
        self.root.title("Jessica")

        self.text = tk.Text(self.root, height=24, width=80)
        self.text.pack()

        self.entry = tk.Entry(self.root, width=80)
        self.entry.pack()
        self.entry.bind("<Return>", self.on_enter)

    def _format_result(self, resp: Any) -> str:
        if isinstance(resp, dict):
            out = resp.get("result") or resp.get("output") or resp
            if isinstance(out, dict):
                return str(out.get("reply") or out)
            return str(out)
        return str(resp)

    def on_enter(self, event):
        user_text = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if not user_text:
            return

        resp = self.manager.handle_input(user_text)
        answer = self._format_result(resp)
        self.text.insert(tk.END, f"You: {user_text}\nJessica: {answer}\n\n")
        self.text.see(tk.END)

    def run(self):
        self.root.mainloop()


def main():
    from jessica.jessica_core import CognitiveManager

    ui = JessicaUI(CognitiveManager())
    ui.run()


if __name__ == "__main__":
    main()
