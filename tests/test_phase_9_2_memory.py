from datetime import datetime
from pathlib import Path

from jessica.memory.knowledge_memory import KnowledgeMemory


def test_learning_persists_to_disk(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("Question A", "Answer A", confidence=0.8)

    assert storage.exists()
    loaded = KnowledgeMemory(storage_path=str(storage))
    assert loaded.recall("Question A") == "Answer A"


def test_reload_loads_stored_knowledge(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("Question B", "Answer B", confidence=0.7)

    reloaded = KnowledgeMemory(storage_path=str(storage))
    assert reloaded.count() == 1
    assert reloaded.recall("Question B") == "Answer B"


def test_overwrite_only_with_higher_confidence(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("Question C", "Answer C1", confidence=0.6)
    memory.learn("Question C", "Answer C2", confidence=0.5)

    assert memory.recall("Question C") == "Answer C1"

    memory.learn("Question C", "Answer C3", confidence=0.9)
    assert memory.recall("Question C") == "Answer C3"


def test_recall_returns_stored_answer(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("Question D", "Answer D")

    assert memory.recall("Question D") == "Answer D"


def test_search_returns_approximate_matches(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("What is the capital of France", "Paris")
    memory.learn("How many days in a week", "Seven")

    assert memory.search("capital of france") == "Paris"
    assert memory.search("days in a week") == "Seven"
