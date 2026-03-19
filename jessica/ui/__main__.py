"""Jessica Tkinter UI entrypoint.

Run with:
    python -m jessica.ui
"""

import os
import sys

# Allow running this file directly: `python jessica/ui/__main__.py`
if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from jessica.ui.main_tk import main


if __name__ == "__main__":
    main()
