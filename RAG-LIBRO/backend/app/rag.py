"""
Fase 1d: pipeline RAG empaquetado — vectorstore, retriever, answer_with_sources.

Contrato para eval y API (Fase 2):
    answer_with_sources(query, k) -> {"answer": str, "pages": list[int]}

`pages` provienen del retriever (1-based), no del texto del LLM (criterio A en EVAL.md).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from app.ingest import ingest_pdf, page_pdf_1based
from app.llm import get_llm
from app.vectorstore import (
    build_or_load_faiss_index,
    create_embeddings,
    default_index_dir,
    index_files_exist,
    load_faiss_index,
)

RETRIEVER_K_DEFAULT = 4

RAG_SYSTEM_PROMPT = """\
You are a helpful assistant answering questions about the book \
"30 Agents Every AI Engineer Must Build" by Imran Ahmad.

Rules:
1. Answer ONLY based on the provided context excerpts.
2. Cite the page numbers (e.g., [p.34, p.35]) from which you derive your answer.
3. If the context does not contain enough information, say: \
"No tengo información suficiente en el contexto proporcionado."
4. Be concise but precise.
5. Use the exact technical terminology that appears in the context. \
Do NOT paraphrase technical terms: if the context says "embeddings", use "embeddings"; \
if it says "vector", use "vector"; if it says "tools", use "tools"; \
if it says "injection", use "injection". Preserve the author's vocabulary.
"""

RAG_USER_TEMPLATE = """\
Context:
{context}

Question: {question}
"""

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_SYSTEM_PROMPT),
        ("human", RAG_USER_TEMPLATE),
    ]
)

_vectorstore: FAISS | None = None


def set_vectorstore(vectorstore: FAISS) -> FAISS:
    """Registra el índice en memoria (notebook, tests, warm-up de API)."""
    global _vectorstore
    _vectorstore = vectorstore
    return vectorstore


def clear_vectorstore_cache() -> None:
    """Limpia caché en memoria (tests)."""
    global _vectorstore
    _vectorstore = None


def _get_cached_vectorstore() -> FAISS:
    if _vectorstore is not None:
        return _vectorstore
    if index_files_exist(default_index_dir()):
        return set_vectorstore(load_faiss_index())
    raise FileNotFoundError(
        "Índice FAISS no encontrado. Ejecutá build_or_load_vectorstore() primero "
        f"(esperado en {default_index_dir()})."
    )


def format_docs(docs: list[Document]) -> str:
    """Formatea chunks recuperados como contexto con número de página."""
    parts: list[str] = []
    for doc in docs:
        page = page_pdf_1based(doc)
        header = f"[Page {page}]" if page else "[Page ?]"
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def build_or_load_vectorstore(
    documents: list[Document] | None = None,
    *,
    pdf_path: Path | None = None,
    embeddings: Embeddings | None = None,
    rebuild_index: bool | None = None,
) -> FAISS:
    """
    Ingesta PDF (si no se pasan chunks) y construye o carga índice FAISS persistido.
    """
    chunks = documents
    if chunks is None:
        _, chunks = ingest_pdf(pdf_path)
    emb = embeddings or create_embeddings()
    result = build_or_load_faiss_index(
        chunks,
        embeddings=emb,
        rebuild_index=rebuild_index,
    )
    return set_vectorstore(result.vectorstore)


def get_retriever(
    k: int = RETRIEVER_K_DEFAULT,
    *,
    vectorstore: FAISS | None = None,
):
    """Retriever sobre el índice (caché, disco o vectorstore explícito)."""
    vs = vectorstore or _get_cached_vectorstore()
    return vs.as_retriever(search_kwargs={"k": k})


def answer_with_sources(query: str, k: int = RETRIEVER_K_DEFAULT) -> dict[str, Any]:
    """
    Ejecuta retrieval + generación LCEL.

    Returns:
        {"answer": str, "pages": list[int]} — páginas 1-based del top-k recuperado.
    """
    retriever = get_retriever(k=k)
    docs = retriever.invoke(query)
    pages = sorted({p for d in docs if (p := page_pdf_1based(d))})

    chain = (
        {
            "context": RunnableLambda(lambda _: format_docs(docs)),
            "question": RunnablePassthrough(),
        }
        | RAG_PROMPT
        | get_llm()
        | StrOutputParser()
    )
    answer = chain.invoke(query)
    return {"answer": answer, "pages": pages}
