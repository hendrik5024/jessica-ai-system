from pathlib import Path

from jessica.identity.identity_model import IdentityModel
from jessica.memory.knowledge_memory import KnowledgeMemory


def test_user_name_recall(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("fact:user_name", "Hendrik")

    model = IdentityModel(memory)
    assert model.get_user_name() == "Hendrik"


def test_assistant_name_default(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    model = IdentityModel(memory)

    assert model.get_assistant_name() == "Jessica"


def test_identity_responses_deterministic(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("fact:assistant_name", "Jessica")

    model = IdentityModel(memory)
    response1 = model.describe_self()
    response2 = model.describe_self()

    assert response1 == response2


def test_no_learning_inside_identity_model(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    model = IdentityModel(memory)

    _ = model.describe_self()
    assert memory.count() == 0


def test_memory_single_source_of_truth(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("fact:user_name", "Hendrik")

    model = IdentityModel(memory)
    assert model.describe_user() == "Your name is Hendrik."
