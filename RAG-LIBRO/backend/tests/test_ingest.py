"""Tests Fase 1a — ingestión PDF (gates 1.1–1.3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.ingest import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DEFAULT_PDF_PATH,
    chunk_length_stats,
    chunks_on_pages,
    get_paths,
    ingest_pdf,
    load_pdf_documents,
    page_pdf_1based,
    pdf_page_count,
    split_documents,
)

PDF_PATH = DEFAULT_PDF_PATH


@pytest.fixture(scope="module")
def page_docs():
    if not PDF_PATH.is_file():
        pytest.skip(f"PDF no encontrado: {PDF_PATH}")
    return load_pdf_documents()


@pytest.fixture(scope="module")
def chunk_docs(page_docs):
    return split_documents(page_docs)


def test_paths_resolve():
    paths = get_paths()
    assert paths.project_root.name == "RAG-LIBRO"
    assert paths.pdf_path == PDF_PATH
    assert paths.storage_dir == paths.backend_root / "storage"


def test_pdf_exists_and_page_count():
    if not PDF_PATH.is_file():
        pytest.skip(f"PDF no encontrado: {PDF_PATH}")
    count = pdf_page_count()
    assert count >= 500, f"esperado ~542 páginas, obtuvo {count}"


def test_load_one_document_per_page(page_docs):
    pdf_pages = pdf_page_count()
    assert len(page_docs) == pdf_pages


def test_page_metadata_1based(page_docs):
    for doc in page_docs[:5]:
        p = page_pdf_1based(doc)
        assert p is not None
        assert 1 <= p <= pdf_page_count()
        assert doc.metadata.get("page") == p - 1


def test_split_produces_chunks(chunk_docs, page_docs):
    assert len(chunk_docs) > len(page_docs)
    stats = chunk_length_stats(chunk_docs)
    assert stats["count"] > 0
    assert stats["max"] <= CHUNK_SIZE + 50  # splitter may add small margin


def test_chunk_metadata_preserves_page(chunk_docs):
    for chunk in chunk_docs[:20]:
        assert page_pdf_1based(chunk) is not None
        assert chunk.metadata.get("page_pdf") == page_pdf_1based(chunk)


def test_q05_gate_chunks_on_pages_180_181(chunk_docs):
    """Gate 1.3: chunks etiquetados en páginas de Q05 (FAISS)."""
    hits = chunks_on_pages(chunk_docs, {180, 181})
    assert len(hits) >= 1
    sample = hits[0]
    assert page_pdf_1based(sample) in (180, 181)
    assert len(sample.page_content) > 0


def test_ingest_pdf_tuple():
    if not PDF_PATH.is_file():
        pytest.skip(f"PDF no encontrado: {PDF_PATH}")
    pages, chunks = ingest_pdf()
    assert len(pages) == pdf_page_count()
    assert len(chunks) > len(pages)


def test_chunk_params_documented():
    assert CHUNK_SIZE == 1000
    assert CHUNK_OVERLAP == 200
