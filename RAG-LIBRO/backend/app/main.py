"""
Fases 2a-2e: entrypoint FastAPI.

Arrancá con:
    uvicorn app.main:app --reload

El lifespan carga el índice FAISS UNA SOLA VEZ al startup y lo mantiene en RAM
para todos los requests (ver app.rag._vectorstore). No se re-embedea por request.

CORS habilitado para http://localhost:3000 (Next.js Fase 3). Lista blanca explícita:
nunca usar allow_origins=["*"] porque bloquea allow_credentials y abre la API a
cualquier origen externo en producción.

Endpoints:
    GET  /health         — readiness check con estado del índice FAISS.
    POST /chat           — respuesta sincrónica completa {answer, pages}.
    POST /chat/stream    — SSE streaming: event:sources → event:token* → event:done.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from app import rag
from app.schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: cargando índice FAISS...")
    rag.build_or_load_vectorstore()
    logger.info("Índice FAISS cargado en memoria.")
    yield
    rag.clear_vectorstore_cache()
    logger.info("Shutdown: caché de vectorstore liberado.")


app = FastAPI(
    title="RAG-LIBRO API",
    description="RAG sobre '30 Agents Every AI Engineer Must Build' — FastAPI + LangChain + FAISS.",
    version="0.4.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict:
    """
    Readiness check: confirma que el servidor levantó Y que el índice está en RAM.

    index_loaded=false indica que el lifespan falló silenciosamente o que el
    índice aún no fue construido (ejecutá el notebook de Fase 1 primero).
    """
    return {"status": "ok", "index_loaded": rag.is_index_loaded()}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Endpoint sincrónico: recibe una pregunta y devuelve respuesta + páginas fuente.

    Úsalo para testing, scripts y clientes que no soporten SSE.
    Para streaming en tiempo real usá POST /chat/stream (Fase 2e).

    Errores:
    - 422: payload inválido (Pydantic — automático).
    - 503: índice FAISS no cargado en memoria (reiniciá el servidor).
    """
    if not rag.is_index_loaded():
        raise HTTPException(
            status_code=503,
            detail=(
                "El índice FAISS no está disponible. "
                "Reiniciá el servidor para cargarlo, o ejecutá el notebook de Fase 1 "
                "para construir el índice en backend/storage/faiss_index/."
            ),
        )
    result = rag.answer_with_sources(request.message, request.k)
    return ChatResponse(answer=result["answer"], pages=result["pages"])


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, http_request: Request) -> EventSourceResponse:
    """
    Endpoint de streaming SSE: emite los tokens del LLM a medida que se generan.

    Protocolo de eventos (mismo orden que stream_answer_with_sources en rag.py):

        event: sources  data: <JSON array de ints>   — páginas recuperadas (antes del 1er token)
        event: token    data: <JSON string>           — un evento por token del LLM
        event: done     data: null                    — señal de fin; cerrar EventSource

    El evento `sources` se emite antes de invocar el LLM: el cliente puede mostrar
    los badges de páginas fuente mientras el texto aún está siendo generado.

    Si el cliente cierra la conexión a mitad de stream, el generador se corta para
    no seguir pagando tokens que nadie va a ver (cancel propagation via is_disconnected).

    Errores:
    - 422: payload inválido (Pydantic — automático).
    - 503: índice FAISS no cargado en memoria (reiniciá el servidor).
    """
    if not rag.is_index_loaded():
        raise HTTPException(
            status_code=503,
            detail=(
                "El índice FAISS no está disponible. "
                "Reiniciá el servidor para cargarlo, o ejecutá el notebook de Fase 1 "
                "para construir el índice en backend/storage/faiss_index/."
            ),
        )

    async def event_generator():
        async for event_type, data in rag.stream_answer_with_sources(
            request.message, request.k
        ):
            if await http_request.is_disconnected():
                logger.info("Cliente desconectado — stream cancelado antes de 'done'.")
                break
            yield {"event": event_type, "data": json.dumps(data)}

    return EventSourceResponse(event_generator())
