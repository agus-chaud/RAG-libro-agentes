"""
Fases 2a-2c: entrypoint FastAPI.

Arrancá con:
    uvicorn app.main:app --reload

El lifespan carga el índice FAISS UNA SOLA VEZ al startup y lo mantiene en RAM
para todos los requests (ver app.rag._vectorstore). No se re-embedea por request.

CORS habilitado para http://localhost:3000 (Next.js Fase 3). Lista blanca explícita:
nunca usar allow_origins=["*"] porque bloquea allow_credentials y abre la API a
cualquier origen externo en producción.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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
    version="0.3.0",
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
