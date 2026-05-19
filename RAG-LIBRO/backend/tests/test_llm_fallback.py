"""Tests — cadena de fallback LLM."""

from langchain_core.messages import AIMessage, HumanMessage

from app.llm import (
    EmptyResponseError,
    ValidatingChatModel,
    _build_fallback_chain,
    _is_empty_message,
    _parse_fallback_chain,
    get_llm,
)
from app.mock_llm import MockChatModel, MockLLM


def test_parse_fallback_chain_default(monkeypatch):
    monkeypatch.delenv("LLM_FALLBACK_CHAIN", raising=False)
    assert _parse_fallback_chain() == ["openrouter", "groq", "mock"]


def test_parse_fallback_chain_from_env(monkeypatch):
    monkeypatch.setenv("LLM_FALLBACK_CHAIN", "groq,mock,openrouter")
    assert _parse_fallback_chain() == ["groq", "mock", "openrouter"]


def test_is_empty_message():
    assert _is_empty_message(AIMessage(content=""))
    assert _is_empty_message(AIMessage(content="   "))
    assert not _is_empty_message(AIMessage(content="hola"))


def test_get_llm_mock_provider():
    llm = get_llm("mock")
    assert isinstance(llm, ValidatingChatModel)
    out = llm.invoke([HumanMessage(content="What is RAG chunking?")])
    assert "[SIMULATION MODE]" in str(out.content)


def test_get_llm_without_keys_uses_mock(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("LLM_FALLBACK_CHAIN", "openrouter,groq,mock")
    llm = get_llm()
    out = llm.invoke([HumanMessage(content="Explain RAG retrieval")])
    assert "[SIMULATION MODE]" in str(out.content)


def test_fallback_chain_skips_missing_keys(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    chain = _build_fallback_chain(["openrouter", "groq", "mock"])
    out = chain.invoke([HumanMessage(content="agents and tools")])
    assert "[SIMULATION MODE]" in str(out.content)


def test_validating_raises_on_empty():
    from langchain_core.outputs import ChatGeneration, ChatResult

    class AlwaysEmpty(MockChatModel):
        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content=""))]
            )

    validated = ValidatingChatModel(delegate=AlwaysEmpty())
    try:
        validated.invoke([HumanMessage(content="hi")])
        raised = False
    except EmptyResponseError:
        raised = True
    assert raised


def test_mock_llm_still_works():
    llm = MockLLM()
    out = llm.invoke("RAG and FAISS")
    assert "[SIMULATION MODE]" in out
