from jessica.llm.llm_interface import LLMInterface
from jessica.llm.llm_router import LLMRouter


def test_llm_responds_to_questions():
    router = LLMRouter(LLMInterface())
    assert router.should_use_llm("What is 2 + 2?") is True
    assert router.generate("What is 2 + 2?") == "[LLM RESPONSE] What is 2 + 2?"


def test_non_questions_do_not_trigger_llm():
    router = LLMRouter(LLMInterface())
    assert router.should_use_llm("hello there") is False


def test_deterministic_output():
    llm = LLMInterface()
    first = llm.generate("test")
    second = llm.generate("test")
    assert first == second
    assert first == "[LLM RESPONSE] test"
