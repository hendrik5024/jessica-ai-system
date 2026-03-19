from jessica.knowledge import KnowledgeRegistry


def test_knowledge_module_registration():
    registry = KnowledgeRegistry()

    record = registry.register_module(
        module_name="math_knowledge",
        proposal_id="proposal_42",
    )

    assert record.module_name == "math_knowledge"
    assert registry.get_module("math_knowledge") is not None
