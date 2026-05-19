"""
Fase 2a: entrypoint FastAPI.

Arrancá con:
    uvicorn app.main:app --reload

El lifespan carga el índice FAISS UNA SOLA VEZ al startup y lo mantiene en RAM
para todos los requests (ver app.rag._vectorstore). No se re-embedea por request.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import rag

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
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    """
    Readiness check: confirma que el servidor levantó Y que el índice está en RAM.

    index_loaded=false indica que el lifespan falló silenciosamente o que el
    índice aún no fue construido (ejecutá el notebook de Fase 1 primero).
    """
    return {"status": "ok", "index_loaded": rag.is_index_loaded()}
