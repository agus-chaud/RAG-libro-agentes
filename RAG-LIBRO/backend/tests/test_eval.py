"""
Evaluación RAG — Fase 0.5.

- Tests unitarios de criterios A/B (corren siempre).
- Tests de integración contra el pipeline RAG (skip hasta Fase 1).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader

from app.eval_cases import EVAL_CASES, EVAL_K_DEFAULT, PASS_THRESHOLD
from app.eval_checks import answer_passes, query_passes, retrieval_passes

PDF_PATH = Path(__file__).resolve().parents[1] / "data" / "libro.pdf"


def _pdf_page_count() -> int:
    if not PDF_PATH.is_file():
        pytest.skip(f"PDF no encontrado: {PDF_PATH}")
    return len(PdfReader(str(PDF_PATH)).pages)


@pytest.mark.parametrize("case", EVAL_CASES, ids=lambda c: c.id)
def test_expected_pages_exist_in_pdf(case):
    total = _pdf_page_count()
    for page in case.expected_pages:
        assert 1 <= page <= total, (
            f"{case.id}: página {page} fuera de rango (PDF tiene {total} páginas)"
        )


def test_eval_dataset_has_ten_queries():
    assert len(EVAL_CASES) == 10


def test_eval_difficulty_mix():
    by_diff = {}
    for case in EVAL_CASES:
        by_diff[case.difficulty] = by_diff.get(case.difficulty, 0) + 1
    assert by_diff.get("fácil") == 3
    assert by_diff.get("media") == 4
    assert by_diff.get("cross-chapter") == 3


def test_retrieval_criterion_pass_and_fail():
    assert retrieval_passes([34, 100], [34, 35]) is True
    assert retrieval_passes([100, 101], [34, 35]) is False
    assert retrieval_passes([], [34]) is False


def test_answer_criterion_pass_and_fail():
    answer = "ReAct combines reasoning and acting in an agent loop."
    assert answer_passes(answer, ["ReAct", "reasoning", "acting"]) is True
    assert answer_passes(answer, ["ReAct", "missing-concept"]) is False
    assert answer_passes("", ["agent"]) is False


def test_query_passes_requires_both_criteria():
    assert query_passes([181], "FAISS stores embeddings in a vectorstore.", [181], ["FAISS", "embeddings"]) is True
    assert query_passes([181], "FAISS stores embeddings.", [180], ["FAISS", "embeddings"]) is False


def run_eval_suite(run_query_fn, k: int = EVAL_K_DEFAULT) -> dict[str, object]:
    """
    Ejecuta el dataset completo. `run_query_fn(query) -> (answer, retrieved_pages)`.

    Usado en Fase 1 desde notebook o tests de integración.
    """
    results = []
    for case in EVAL_CASES:
        answer, pages = run_query_fn(case.query, k=k)
        passed = query_passes(pages, answer, list(case.expected_pages), list(case.key_concepts))
        results.append(
            {
                "id": case.id,
                "passed": passed,
                "retrieval_ok": retrieval_passes(pages, list(case.expected_pages)),
                "answer_ok": answer_passes(answer, list(case.key_concepts)),
                "retrieved_pages": pages,
            }
        )
    passed_count = sum(1 for r in results if r["passed"])
    rate = passed_count / len(EVAL_CASES) if EVAL_CASES else 0.0
    return {
        "results": results,
        "passed": passed_count,
        "total": len(EVAL_CASES),
        "pass_rate": rate,
        "meets_baseline": rate >= PASS_THRESHOLD,
    }


@pytest.mark.integration
@pytest.mark.parametrize("case", EVAL_CASES, ids=lambda c: c.id)
def test_eval_query_against_rag_pipeline(case):
    """Fase 1+: conectar con `app.rag` cuando exista el retriever."""
    pytest.importorskip("app.rag", reason="Pipeline RAG aún no implementado (Fase 1)")
    from app.rag import answer_with_sources  # type: ignore[import-not-found]

    result = answer_with_sources(case.query, k=EVAL_K_DEFAULT)
    assert query_passes(
        result["pages"],
        result["answer"],
        list(case.expected_pages),
        list(case.key_concepts),
    ), f"{case.id} falló: {result}"
