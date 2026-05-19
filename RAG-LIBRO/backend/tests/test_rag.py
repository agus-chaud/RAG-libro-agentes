"""Tests — módulo app.rag (Fase 1d)."""

from pathlib import Path

import pytest
from langchain_core.documents import Document

from app.rag import (
    RETRIEVER_K_DEFAULT,
    answer_with_sources,
    build_or_load_vectorstore,
    clear_vectorstore_cache,
    format_docs,
    get_retriever,
    set_vectorstore,
)
from app.vectorstore import build_faiss_index, create_embeddings


@pytest.fixture(autouse=True)
def _clear_rag_cache():
    clear_vectorstore_cache()
    yield
    clear_vectorstore_cache()


def _sample_chunks() -> list[Document]:
    return [
        Document(
            page_content="RAG retrieves chunks and answers with context.",
            metadata={"page": 0, "page_pdf": 1},
        ),
        Document(
            page_content="FAISS is a vector index for similarity search.",
            metadata={"page": 1, "page_pdf": 2},
        ),
    ]


def test_format_docs_includes_page_headers():
    text = format_docs(_sample_chunks())
    assert "[Page 1]" in text
    assert "[Page 2]" in text
    assert "RAG retrieves" in text


def test_build_or_load_vectorstore_and_get_retriever(tmp_path: Path):
    emb = create_embeddings()
    vs = build_faiss_index(_sample_chunks(), embeddings=emb, index_dir=tmp_path / "idx")
    set_vectorstore(vs)

    retriever = get_retriever(k=2)
    docs = retriever.invoke("What is RAG?")
    assert len(docs) == 2
    assert all(d.metadata.get("page_pdf") for d in docs)


def test_answer_with_sources_contract(tmp_path: Path, monkeypatch):
    emb = create_embeddings()
    vs = build_faiss_index(_sample_chunks(), embeddings=emb, index_dir=tmp_path / "idx")
    set_vectorstore(vs)

    monkeypatch.setenv("LLM_PROVIDER", "mock")
    result = answer_with_sources("What is RAG?", k=RETRIEVER_K_DEFAULT)

    assert set(result.keys()) == {"answer", "pages"}
    assert isinstance(result["answer"], str)
    assert result["answer"].strip()
    assert isinstance(result["pages"], list)
    assert all(isinstance(p, int) for p in result["pages"])


def test_build_or_load_vectorstore_persists(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("app.vectorstore.default_index_dir", lambda: tmp_path / "faiss_index")
    chunks = _sample_chunks()
    emb = create_embeddings()

    build_or_load_vectorstore(chunks, embeddings=emb, rebuild_index=True)
    second = build_or_load_vectorstore(chunks, embeddings=emb, rebuild_index=False)

    retriever = get_retriever(k=1, vectorstore=second)
    assert len(retriever.invoke("vector")) >= 1
