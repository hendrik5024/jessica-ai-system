import asyncio
import json
from datetime import datetime

from config import load_settings
from jessica.core.jessica_core import JessicaCore
from jessica.memory import episodic_memory as episodic_module
from jessica.memory.episodic_memory import EpisodicMemory
from logger import get_internal_logger


def test_episodic_memory_store_and_search(tmp_path, monkeypatch):
    memory_file = tmp_path / "episodic_memory.json"
    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(memory_file))

    memory = EpisodicMemory()
    memory.store_event("Explain Python", "Python is a high-level language.", "GENERAL")

    results = memory.search("Python")

    assert len(results) == 1
    assert results[0]["user_input"] == "Explain Python"


def test_pipeline_recall_returns_earlier_discussion(tmp_path, monkeypatch):
    memory_file = tmp_path / "episodic_memory.json"
    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(memory_file))

    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    first = asyncio.run(core.handle_input("system status"))
    recall = asyncio.run(core.handle_input("What did we discuss earlier about system status?"))

    assert "System status:" in first
    assert "Earlier discussion:" in recall
    assert "You said: system status" in recall

    with open(memory_file, "r", encoding="utf-8") as handle:
        entries = json.load(handle)

    assert len(entries) >= 2


def test_pipeline_recall_keywords_include_remember_phrase(tmp_path, monkeypatch):
    memory_file = tmp_path / "episodic_memory.json"
    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(memory_file))

    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    asyncio.run(core.handle_input("Explain Python"))
    recall = asyncio.run(core.handle_input("Do you remember what we talked about Python?"))

    assert "Earlier discussion:" in recall
    assert "Explain Python" in recall


def test_age_query_uses_born_year_from_episodic_memory(tmp_path, monkeypatch):
    memory_file = tmp_path / "episodic_memory.json"
    monkeypatch.setattr(episodic_module, "MEMORY_FILE", str(memory_file))

    settings = load_settings()
    logger = get_internal_logger(settings.log_file)
    core = JessicaCore(settings=settings, logger=logger)

    core.episodic_memory.store_event(
        "I was born in 1990",
        "Thanks, I will remember that.",
        "PERSONAL_INFO",
    )

    response = asyncio.run(core.handle_input("how old am i"))

    expected_age = datetime.now().year - 1990
    assert response == f"You were born in 1990, which makes you {expected_age} years old."
