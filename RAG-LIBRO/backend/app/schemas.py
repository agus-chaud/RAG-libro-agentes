"""
Fase 2b: schemas Pydantic para la API.

Separar schemas de main.py tiene dos ventajas:
- Los tests de Fase 2f los importan directamente sin arrancar la app.
- La documentación de /docs queda separada del routing.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.rag import RETRIEVER_K_DEFAULT


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="Pregunta sobre el libro '30 Agents Every AI Engineer Must Build'.",
        examples=["¿Qué es el loop ReAct?"],
    )
    k: int = Field(
        default=RETRIEVER_K_DEFAULT,
        ge=1,
        le=20,
        description=(
            "Cantidad de chunks a recuperar del índice FAISS. "
            "Valores altos dilatan el contexto y degradan modelos pequeños (ver EVAL.md sweep k)."
        ),
    )


class ChatResponse(BaseModel):
    answer: str = Field(description="Respuesta generada por el LLM a partir del contexto recuperado.")
    pages: list[int] = Field(description="Páginas del PDF (1-based) usadas como fuentes.")
