"""Thin wrapper to run Jessica.

Preferred usages:
    python run_jessica.py
    python -m jessica
Both call the same CLI loop in `jessica.__main__.main`.
"""

from jessica.__main__ import main

if __name__ == "__main__":
    main()
