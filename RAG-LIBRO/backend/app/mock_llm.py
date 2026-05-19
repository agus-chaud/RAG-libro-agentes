"""
Mock LLM y embeddings offline para RAG-LIBRO.

Adaptado desde chapter06/agent_utils.py (Imran Ahmad, cap. 06 — Knowledge Agents).
Permite desarrollo y tests sin API keys cuando LLM_PROVIDER=mock.
"""

from __future__ import annotations

import hashlib
from typing import Any, List, Optional

import numpy as np
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.llms import LLM
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class MockLLM(LLM):
    """
    LLM simulado con respuestas orientadas al libro / RAG.
    Compatible con cadenas LangChain (invoke, LCEL).
    """

    RESPONSES: dict[str, str] = {
        "rag_general": (
            "[SIMULATION MODE] Según el contexto recuperado del libro, un pipeline RAG "
            "típico incluye: carga de documentos, chunking, embeddings, índice vectorial "
            "(p. ej. FAISS), recuperación top-k y generación condicionada al contexto. "
            "Limitaciones habituales: ruido en chunks, frescura del índice, latencia de "
            "retrieval y sensibilidad a chunk_size/overlap."
        ),
        "agent_foundation": (
            "[SIMULATION MODE] Los agentes de IA combinan percepción, razonamiento, "
            "planificación, acción y aprendizaje en un ciclo cerrado. El libro enfatiza "
            "patrones de producción, herramientas (MCP, RAG) y evaluación medible."
        ),
        "default": (
            "[SIMULATION MODE] Respuesta simulada para desarrollo offline. "
            "Configurá GROQ_API_KEY u OPENROUTER_API_KEY y LLM_PROVIDER=groq|openrouter "
            "para respuestas reales basadas en el PDF indexado."
        ),
    }

    @property
    def _llm_type(self) -> str:
        return "rag_libro_mock_llm"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        return self._route(prompt)

    def invoke(self, input: Any, config: Optional[dict] = None, **kwargs: Any) -> str:
        text = input if isinstance(input, str) else str(input)
        return self._route(text)

    def _route(self, prompt: str) -> str:
        p = prompt.lower()
        if any(kw in p for kw in ("rag", "retrieval", "embedding", "faiss", "chunk")):
            return self.RESPONSES["rag_general"]
        if any(kw in p for kw in ("agent", "perception", "planning", "mcp", "tool")):
            return self.RESPONSES["agent_foundation"]
        return self.RESPONSES["default"]


class MockChatModel(BaseChatModel):
    """Chat model offline compatible con `with_fallbacks` y cadenas LCEL."""

    @property
    def _llm_type(self) -> str:
        return "rag_libro_mock_chat"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        prompt = messages[-1].content if messages else ""
        text = MockLLM()._route(str(prompt))
        message = AIMessage(content=text)
        return ChatResult(generations=[ChatGeneration(message=message)])


class MockEmbeddings(Embeddings):
    """
    Embeddings deterministas (hash-seeded) para indexar sin red.
    Ref. chapter06 MockEmbeddings — 256 dims.
    """

    DIMENSION: int = 256

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        seed = int(hashlib.md5(text.encode(), usedforsecurity=False).hexdigest()[:8], 16) % (2**31)
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.DIMENSION).astype(float)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist() if norm > 0 else vec.tolist()
