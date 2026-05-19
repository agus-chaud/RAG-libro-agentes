"""
Fase 1b: embeddings MiniLM + FAISS persistido e idempotente.

Responsabilidades:
- Crear embeddings reales con all-MiniLM-L6-v2.
- Construir y persistir índice FAISS en storage/faiss_index.
- Reutilizar índice existente si REBUILD_INDEX no está activado.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.ingest import get_paths

EMBEDDING_MODEL_DEFAULT = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_DIRNAME = "faiss_index"
_TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class FaissIndexResult:
    vectorstore: FAISS
    index_dir: Path
    built_new: bool


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in _TRUE_VALUES


def default_index_dir() -> Path:
    return get_paths().storage_dir / FAISS_INDEX_DIRNAME


def index_files_exist(index_dir: Path) -> bool:
    return (index_dir / "index.faiss").is_file() and (index_dir / "index.pkl").is_file()


def resolve_rebuild_flag(rebuild_index: bool | None = None) -> bool:
    if rebuild_index is not None:
        return rebuild_index
    return _env_bool("REBUILD_INDEX", default=False)


def embedding_model_name(model_name: str | None = None) -> str:
    if model_name:
        return model_name
    return os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL_DEFAULT)


def create_embeddings(
    model_name: str | None = None,
    *,
    normalize_embeddings: bool = True,
) -> Embeddings:
    return HuggingFaceEmbeddings(
        model_name=embedding_model_name(model_name),
        encode_kwargs={"normalize_embeddings": normalize_embeddings},
    )


def build_faiss_index(
    documents: list[Document],
    *,
    embeddings: Embeddings | None = None,
    index_dir: Path | None = None,
) -> FAISS:
    if not documents:
        raise ValueError("No se puede construir FAISS sin documentos.")
    target_dir = index_dir or default_index_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    emb = embeddings or create_embeddings()
    vectorstore = FAISS.from_documents(documents, emb)
    vectorstore.save_local(str(target_dir))
    return vectorstore


def load_faiss_index(
    *,
    embeddings: Embeddings | None = None,
    index_dir: Path | None = None,
) -> FAISS:
    target_dir = index_dir or default_index_dir()
    if not index_files_exist(target_dir):
        raise FileNotFoundError(f"Índice FAISS no encontrado en: {target_dir}")
    emb = embeddings or create_embeddings()
    return FAISS.load_local(
        str(target_dir),
        emb,
        allow_dangerous_deserialization=True,
    )


def build_or_load_faiss_index(
    documents: list[Document],
    *,
    embeddings: Embeddings | None = None,
    index_dir: Path | None = None,
    rebuild_index: bool | None = None,
) -> FaissIndexResult:
    target_dir = index_dir or default_index_dir()
    should_rebuild = resolve_rebuild_flag(rebuild_index)
    has_index = index_files_exist(target_dir)

    if has_index and not should_rebuild:
        vectorstore = load_faiss_index(embeddings=embeddings, index_dir=target_dir)
        return FaissIndexResult(vectorstore=vectorstore, index_dir=target_dir, built_new=False)

    vectorstore = build_faiss_index(documents, embeddings=embeddings, index_dir=target_dir)
    return FaissIndexResult(vectorstore=vectorstore, index_dir=target_dir, built_new=True)
