"""Smoke tests — MockLLM offline (Fase 0)."""

from langchain_core.messages import HumanMessage

from app.llm import ValidatingChatModel, get_llm
from app.mock_llm import MockChatModel, MockEmbeddings, MockLLM


def test_mock_llm_returns_simulation_prefix():
    llm = MockLLM()
    out = llm.invoke("What is RAG chunking?")
    assert "[SIMULATION MODE]" in out
    assert "chunk" in out.lower() or "RAG" in out


def test_mock_embeddings_dimension_stable():
    emb = MockEmbeddings()
    v1 = emb.embed_query("same text")
    v2 = emb.embed_query("same text")
    assert len(v1) == MockEmbeddings.DIMENSION
    assert v1 == v2


def test_get_llm_defaults_to_mock_without_keys(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("LLM_FALLBACK_CHAIN", "openrouter,groq,mock")
    llm = get_llm("mock")
    assert isinstance(llm, ValidatingChatModel)
    assert isinstance(llm.delegate, MockChatModel)
    out = llm.invoke([HumanMessage(content="RAG")])
    assert "[SIMULATION MODE]" in str(out.content)
