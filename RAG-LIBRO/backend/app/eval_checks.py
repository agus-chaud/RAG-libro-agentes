"""Criterios binarios de evaluación RAG (Fase 0.5)."""

from __future__ import annotations


def retrieval_passes(retrieved_pages: list[int], expected_pages: list[int]) -> bool:
    """Criterio A: al menos una página esperada en el top-k recuperado."""
    if not expected_pages:
        return False
    retrieved = {int(p) for p in retrieved_pages}
    return any(int(p) in retrieved for p in expected_pages)


def answer_passes(answer: str, key_concepts: list[str]) -> bool:
    """Criterio B: todos los conceptos clave presentes (case-insensitive)."""
    if not key_concepts:
        return False
    text = answer.lower()
    return all(concept.strip().lower() in text for concept in key_concepts)


def query_passes(
    retrieved_pages: list[int],
    answer: str,
    expected_pages: list[int],
    key_concepts: list[str],
) -> bool:
    return retrieval_passes(retrieved_pages, expected_pages) and answer_passes(
        answer, key_concepts
    )
