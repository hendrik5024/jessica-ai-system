from pathlib import Path

from jessica.memory.knowledge_memory import KnowledgeMemory
from jessica.memory.knowledge_structurer import KnowledgeStructurer


def test_fact_extraction_patterns():
    memory = KnowledgeMemory(storage_path="memory/knowledge.json")
    structurer = KnowledgeStructurer(memory)

    assert structurer.extract_fact("my name is Hendrik") == ("user_name", "hendrik")
    assert structurer.extract_fact("your name is Jessica") == ("assistant_name", "jessica")
    assert structurer.extract_fact("I live in Lisbon") == ("user_location", "lisbon")
    assert structurer.extract_fact("I work as Engineer") == ("user_profession", "engineer")


def test_store_and_retrieve_fact(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    structurer = KnowledgeStructurer(memory)

    structurer.process_input("my name is Hendrik")
    assert memory.recall("fact:user_name") == "hendrik"


def test_answering_uses_structured_fact(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    structurer = KnowledgeStructurer(memory)

    structurer.process_input("my name is Hendrik")
    user_name = memory.recall("fact:user_name")

    assert user_name == "hendrik"
    response = f"Your name is {user_name}."
    assert response == "Your name is hendrik."


def test_deterministic_behavior(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    structurer = KnowledgeStructurer(memory)

    structurer.process_input("my name is Hendrik")
    first = memory.recall("fact:user_name")
    structurer.process_input("my name is Hendrik")
    second = memory.recall("fact:user_name")

    assert first == second
