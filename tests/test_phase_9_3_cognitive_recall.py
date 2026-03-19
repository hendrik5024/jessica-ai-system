from pathlib import Path

from jessica.memory.knowledge_memory import KnowledgeMemory
from jessica.memory.cognitive_recall_bridge import CognitiveRecallBridge


def test_exact_recall_used_in_response(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("Question A", "Answer A", confidence=0.9)

    bridge = CognitiveRecallBridge(memory)
    response = bridge.augment_response("Question A", "Base response")

    assert response.startswith("From what I have learned: Answer A.")


def test_search_recall_used_when_exact_not_found(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("What is the capital of France", "Paris", confidence=0.9)

    bridge = CognitiveRecallBridge(memory)
    response = bridge.augment_response("capital of france", "Base response")

    assert response.startswith("From what I have learned: Paris.")


def test_base_response_unchanged_if_nothing_found(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    bridge = CognitiveRecallBridge(memory)

    response = bridge.augment_response("Unknown question", "Base response")

    assert response == "Base response"


def test_memory_persists_after_reload(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("Question B", "Answer B", confidence=0.8)

    reloaded = KnowledgeMemory(storage_path=str(storage))
    bridge = CognitiveRecallBridge(reloaded)
    response = bridge.augment_response("Question B", "Base response")

    assert response.startswith("From what I have learned: Answer B.")


def test_deterministic_behavior(tmp_path: Path):
    storage = tmp_path / "knowledge.json"
    memory = KnowledgeMemory(storage_path=str(storage))
    memory.learn("Question C", "Answer C", confidence=0.8)

    bridge = CognitiveRecallBridge(memory)
    response1 = bridge.augment_response("Question C", "Base response")
    response2 = bridge.augment_response("Question C", "Base response")

    assert response1 == response2
