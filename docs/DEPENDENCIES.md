# Dependency Inventory

This file documents Python dependencies detected from imports across the workspace and how they map to install files.

## Core Runtime (`requirements.txt`)

These are used by the main Jessica runtime, routing, memory, automation, and web API:

- numpy
- pyttsx3
- torch
- transformers
- sentence-transformers
- faiss-cpu
- python-dotenv
- psutil
- pynput
- pywin32 (Windows only)
- PySide6
- PyYAML
- scikit-learn
- scipy
- huggingface-hub
- safetensors
- typing-extensions
- tqdm
- typer
- jinja2
- llama-cpp-python
- requests
- flask
- flask-cors

## Development (`requirements-dev.txt`)

- pytest
- pytest-cov

## Optional/Feature-Specific (`requirements-optional.txt`)

These are imported by optional modules (voice, vision, CAD, research tooling, etc.) and are not required for baseline runtime:

- vosk, pyaudio, pocketsphinx, sounddevice, soundfile, whisper, piper, TTS
- opencv-python, face-recognition, pytesseract, Pillow
- pandas, openpyxl, PyPDF2, python-docx
- pyautogui, keyboard, mouse, bs4
- chromadb, diffusers, evaluate, peft, sentencepiece
- cadquery, trimesh
- openai, instructor, docstring-parser, tabulate, matplotlib, seaborn, wget, github3.py, GitPython, chess

## Detection Notes

Dependency identification was based on static import discovery across project Python files. Some imports are optional paths used only when specific capabilities are enabled.
