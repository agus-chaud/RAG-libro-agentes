"""
Tests — API endpoints (Fase 2f).

Tarea 2.13: GET /health, POST /chat sync con LLM mock, errores 422/503.
Tarea 2.14: POST /chat/stream — protocolo SSE completo (sources → token* → done).

Estrategia de fixtures:
  - `_seeded_vectorstore`: construye un índice FAISS offline con MockEmbeddings
    y lo registra en `rag._vectorstore` para que los endpoints lo encuentren.
  - `client`: TestClient con lifespan activo; parchea `build_or_load_vectorstore`
    para que el lifespan no pise el índice mock ni toque el disco.

Estrategia para el stream (tarea 2.14):
  Se mockea `rag.stream_answer_with_sources` con un generador determinista.
  Esto aísla el transporte HTTP (lo que testea este archivo) de la lógica RAG
  (testeada en test_rag.py). Cada capa se testea sola.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from app import rag
from app.main import app
from app.mock_llm import MockEmbeddings
from app.vectorstore import build_faiss_index

# ───────────────────────── datos de prueba ──────────────────────────────────

_SAMPLE_DOCS = [
    Document(
        page_content="RAG retrieves relevant chunks and generates answers from context.",
        metadata={"page": 0, "page_pdf": 1},
    ),
    Document(
        page_content="FAISS is a vector index for efficient similarity search.",
        metadata={"page": 1, "page_pdf": 2},
    ),
]

# ───────────────────────── fixtures ─────────────────────────────────────────


@pytest.fixture()
def _seeded_vectorstore(tmp_path: Path):
    """
    Índice FAISS offline registrado en rag antes del test.

    Usa MockEmbeddings (256 dims, determinista, sin red) para que los tests
    corran en CI sin HuggingFace ni conexión a internet.
    """
    vs = build_faiss_index(
        _SAMPLE_DOCS,
        embeddings=MockEmbeddings(),
        index_dir=tmp_path / "idx",
    )
    rag.set_vectorstore(vs)
    yield vs
    rag.clear_vectorstore_cache()


@pytest.fixture()
def client(monkeypatch, _seeded_vectorstore):
    """
    TestClient con lifespan activo y LLM mock.

    `build_or_load_vectorstore` se reemplaza para que el lifespan no sobrescriba
    el índice mock con un load desde disco (que podría no existir en CI).
    """
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setattr(
        rag, "build_or_load_vectorstore", lambda *a, **kw: _seeded_vectorstore
    )
    with TestClient(app) as tc:
        yield tc


# ───────────────────────── helpers SSE ──────────────────────────────────────


def _parse_sse(text: str) -> list[dict[str, Any]]:
    """
    Parsea texto SSE crudo en lista de dicts ``{"event": str, "data": Any}``.

    El formato SSE es líneas clave:valor separadas por líneas vacías.
    """
    events: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                events.append(current)
                current = {}
        elif stripped.startswith("event:"):
            current["event"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("data:"):
            raw = stripped.split(":", 1)[1].strip()
            try:
                current["data"] = json.loads(raw)
            except json.JSONDecodeError:
                current["data"] = raw
    if current:
        events.append(current)
    return events


# ───────────────────────── GET /health ──────────────────────────────────────


def test_health_ok_with_index_loaded(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["index_loaded"] is True


def test_health_index_not_loaded(monkeypatch):
    """Sin índice en memoria el health debe reportar index_loaded: false."""
    rag.clear_vectorstore_cache()
    monkeypatch.setattr(rag, "build_or_load_vectorstore", lambda *a, **kw: None)
    with TestClient(app) as tc:
        resp = tc.get("/health")
    assert resp.status_code == 200
    assert resp.json()["index_loaded"] is False


# ───────────────────────── POST /chat ───────────────────────────────────────


def test_chat_returns_answer_and_pages(client):
    resp = client.post("/chat", json={"message": "What is RAG?"})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["answer"], str) and body["answer"].strip()
    assert isinstance(body["pages"], list)
    assert all(isinstance(p, int) for p in body["pages"])


def test_chat_422_on_empty_message(client):
    """Pydantic debe rechazar message vacío con 422."""
    resp = client.post("/chat", json={"message": ""})
    assert resp.status_code == 422


def test_chat_422_on_missing_message(client):
    """Pydantic debe rechazar payload sin message con 422."""
    resp = client.post("/chat", json={})
    assert resp.status_code == 422


def test_chat_422_on_k_out_of_range(client):
    """k fuera del rango [1, 20] debe devolver 422."""
    resp = client.post("/chat", json={"message": "test", "k": 0})
    assert resp.status_code == 422


def test_chat_503_when_no_index(monkeypatch):
    """Sin índice cargado el endpoint debe devolver 503 con mensaje accionable."""
    rag.clear_vectorstore_cache()
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setattr(rag, "build_or_load_vectorstore", lambda *a, **kw: None)
    with TestClient(app) as tc:
        resp = tc.post("/chat", json={"message": "What is RAG?"})
    assert resp.status_code == 503
    assert "FAISS" in resp.json()["detail"]


# ───────────────────────── POST /chat/stream ────────────────────────────────


async def _fake_stream(
    query: str, k: int = 4
) -> AsyncGenerator[tuple[str, Any], None]:
    """
    Generador determinista que reemplaza a stream_answer_with_sources en los tests.

    Permite testear el endpoint (transporte SSE) sin depender del LLM ni del índice.
    Sigue exactamente el protocolo definido en tarea 2.9.
    """
    yield ("sources", [1, 2])
    yield ("token", "[MOCK] ")
    yield ("token", "streaming response")
    yield ("done", None)


def test_chat_stream_sse_protocol(client, monkeypatch):
    """
    Tarea 2.14: verifica el protocolo SSE completo del endpoint /chat/stream.

    Invariantes:
    - Content-Type: text/event-stream
    - Primer evento: sources con array de ints
    - Al menos un evento: token con string
    - Último evento: done con data null
    """
    monkeypatch.setattr(rag, "stream_answer_with_sources", _fake_stream)

    resp = client.post("/chat/stream", json={"message": "What is RAG?"})

    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]

    events = _parse_sse(resp.text)
    assert events, "La respuesta SSE no contiene eventos"

    event_types = [e.get("event") for e in events]
    assert event_types[0] == "sources", "El primer evento debe ser 'sources'"
    assert "token" in event_types, "Debe haber al menos un evento 'token'"
    assert event_types[-1] == "done", "El último evento debe ser 'done'"

    sources_ev = events[0]
    assert isinstance(sources_ev["data"], list), "sources.data debe ser un array"
    assert all(isinstance(p, int) for p in sources_ev["data"])

    token_events = [e for e in events if e.get("event") == "token"]
    assert all(isinstance(e["data"], str) for e in token_events), (
        "Cada token.data debe ser un string JSON"
    )

    done_ev = events[-1]
    assert done_ev["data"] is None, "done.data debe ser null"


def test_chat_stream_422_on_empty_message(client, monkeypatch):
    monkeypatch.setattr(rag, "stream_answer_with_sources", _fake_stream)
    resp = client.post("/chat/stream", json={"message": ""})
    assert resp.status_code == 422


def test_chat_stream_503_when_no_index(monkeypatch):
    """El chequeo 503 debe ocurrir ANTES de abrir el stream."""
    rag.clear_vectorstore_cache()
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setattr(rag, "build_or_load_vectorstore", lambda *a, **kw: None)
    with TestClient(app) as tc:
        resp = tc.post("/chat/stream", json={"message": "What is RAG?"})
    assert resp.status_code == 503
