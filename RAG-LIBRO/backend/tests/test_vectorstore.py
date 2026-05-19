"""Tests Fase 1b — FAISS persistido + carga idempotente."""

from __future__ import annotations

from pathlib import Path

import pytest
from langchain_core.documents import Document

from app.mock_llm import MockEmbeddings
from app.vectorstore import (
    FAISS_INDEX_DIRNAME,
    build_or_load_faiss_index,
    build_faiss_index,
    index_files_exist,
    load_faiss_index,
    resolve_rebuild_flag,
)


def _docs() -> list[Document]:
    return [
        Document(page_content="FAISS is a vector index.", metadata={"page": 0, "page_pdf": 1}),
        Document(page_content="Embeddings map text to vectors.", metadata={"page": 1, "page_pdf": 2}),
        Document(page_content="RAG retrieves chunks and answers with context.", metadata={"page": 2, "page_pdf": 3}),
    ]


def test_build_faiss_persists_index_files(tmp_path: Path):
    index_dir = tmp_path / FAISS_INDEX_DIRNAME
    vectorstore = build_faiss_index(_docs(), embeddings=MockEmbeddings(), index_dir=index_dir)
    assert vectorstore is not None
    assert index_files_exist(index_dir)


def test_load_faiss_from_existing_index(tmp_path: Path):
    index_dir = tmp_path / FAISS_INDEX_DIRNAME
    build_faiss_index(_docs(), embeddings=MockEmbeddings(), index_dir=index_dir)
    loaded = load_faiss_index(embeddings=MockEmbeddings(), index_dir=index_dir)
    assert loaded is not None
    hits = loaded.similarity_search("What is FAISS?", k=2)
    assert len(hits) == 2


def test_build_or_load_idempotent_without_rebuild(tmp_path: Path):
    index_dir = tmp_path / FAISS_INDEX_DIRNAME

    first = build_or_load_faiss_index(
        _docs(),
        embeddings=MockEmbeddings(),
        index_dir=index_dir,
        rebuild_index=False,
    )
    second = build_or_load_faiss_index(
        _docs(),
        embeddings=MockEmbeddings(),
        index_dir=index_dir,
        rebuild_index=False,
    )

    assert first.built_new is True
    assert second.built_new is False
    assert index_files_exist(index_dir)


def test_build_or_load_rebuild_forces_new_build(tmp_path: Path):
    index_dir = tmp_path / FAISS_INDEX_DIRNAME
    build_or_load_faiss_index(
        _docs(),
        embeddings=MockEmbeddings(),
        index_dir=index_dir,
        rebuild_index=False,
    )
    rebuilt = build_or_load_faiss_index(
        _docs(),
        embeddings=MockEmbeddings(),
        index_dir=index_dir,
        rebuild_index=True,
    )
    assert rebuilt.built_new is True


def test_resolve_rebuild_flag_explicit_value_wins(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("REBUILD_INDEX", "false")
    assert resolve_rebuild_flag(True) is True
    assert resolve_rebuild_flag(False) is False


def test_resolve_rebuild_flag_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("REBUILD_INDEX", "true")
    assert resolve_rebuild_flag(None) is True
    monkeypatch.setenv("REBUILD_INDEX", "0")
    assert resolve_rebuild_flag(None) is False
