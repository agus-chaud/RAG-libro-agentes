"""
Dataset de evaluación RAG — fuente machine-readable (Fase 0.5).

Mantener alineado con `../../EVAL.md`. Páginas = índice 1-based del PDF
(`backend/data/libro.pdf`, 542 páginas), verificado con inspección pypdf.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Difficulty = Literal["fácil", "media", "cross-chapter"]

EVAL_K_DEFAULT = 4
PASS_THRESHOLD = 0.70


@dataclass(frozen=True)
class EvalCase:
    id: str
    difficulty: Difficulty
    query: str
    expected_pages: tuple[int, ...]
    key_concepts: tuple[str, ...]
    notes: str = ""


EVAL_CASES: tuple[EvalCase, ...] = (
    EvalCase(
        id="Q01",
        difficulty="fácil",
        query="What is an AI agent according to this book?",
        expected_pages=(34, 35),
        key_concepts=("agent", "goal", "environment"),
        notes="Cap. 1 — definición de agente (p.34 inspeccionada).",
    ),
    EvalCase(
        id="Q02",
        difficulty="fácil",
        query="What are the levels of agent capability described in the book (tool-using, planning, learning)?",
        expected_pages=(9, 64),
        key_concepts=("tool-using", "planning", "learning"),
        notes="Cap. 1 — niveles de madurez del agente.",
    ),
    EvalCase(
        id="Q03",
        difficulty="fácil",
        query="Explain the ReAct pattern (Reasoning and Acting) for agents.",
        expected_pages=(52, 72),
        key_concepts=("ReAct", "reasoning", "acting"),
        notes="Cap. 2 / toolkit — patrón ReAct (p.52, p.72).",
    ),
    EvalCase(
        id="Q04",
        difficulty="media",
        query="What is a Knowledge Retrieval agent and how does retrieval-augmented generation work?",
        expected_pages=(177, 179, 181),
        key_concepts=("retrieval", "embedding", "vector"),
        notes="Cap. 6 — arquitectura RAG y flujo modular.",
    ),
    EvalCase(
        id="Q05",
        difficulty="media",
        query="How does the book example store document embeddings using FAISS?",
        expected_pages=(180, 181),
        key_concepts=("FAISS", "embeddings", "vectorstore"),
        notes="Cap. 6 — snippet FAISS + RecursiveCharacterTextSplitter (p.180-181).",
    ),
    EvalCase(
        id="Q06",
        difficulty="media",
        query="What is the Model Context Protocol (MCP) and what problem does it solve?",
        expected_pages=(47, 48),
        key_concepts=("Model Context Protocol", "tools", "interoperability"),
        notes="Cap. 1 — MCP e interacción agente-herramientas.",
    ),
    EvalCase(
        id="Q07",
        difficulty="media",
        query="How does LangGraph support building agent workflows?",
        expected_pages=(36, 38, 40, 72, 74),
        key_concepts=("LangGraph", "workflow", "state"),
        notes="Cap. 2 — frameworks de orquestación. p.36-40: intro; p.72-74: implementación detallada (verificado: retriever encuentra p.72-74 consistentemente con contenido relevante).",
    ),
    EvalCase(
        id="Q08",
        difficulty="cross-chapter",
        query="Compare reactive agents and deliberative agents. When would you choose each?",
        expected_pages=(42, 43, 44),
        key_concepts=("reactive", "deliberative", "planning"),
        notes="Cap. 1 — arquitecturas cognitivas reactiva vs deliberativa.",
    ),
    EvalCase(
        id="Q09",
        difficulty="cross-chapter",
        query="What security risks affect RAG systems, and how does prompt injection relate to retrieval?",
        expected_pages=(24, 138, 181),
        key_concepts=("injection", "retrieval", "RAG"),
        notes="Cap. 4 (seguridad) + Cap. 6 (RAG) — riesgo cross-capítulo.",
    ),
    EvalCase(
        id="Q10",
        difficulty="cross-chapter",
        query="How does a supervisor agent coordinate specialist agents, and what role does episodic memory play?",
        expected_pages=(218, 220, 222, 424),
        key_concepts=("supervisor", "episodic", "specialist"),
        notes="Cap. 7 (orquestación) + Cap. 14 (ejemplo multi-agente). p.222 añadida: contiene ejemplo concreto supervisor+episodic memory verificado por retriever.",
    ),
)
