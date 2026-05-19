"""
Ingestión PDF → Documents → chunks (Fase 1a).

PyPDFLoader + RecursiveCharacterTextSplitter. Páginas en metadata:
- `page`: índice 0-based del loader (LangChain / PyPDF)
- `page_pdf`: índice 1-based para eval y citas (EVAL.md, pypdf)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

# RAG-LIBRO/ (raíz del proyecto)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
DEFAULT_PDF_PATH = BACKEND_ROOT / "data" / "libro.pdf"


@dataclass(frozen=True)
class IngestPaths:
    project_root: Path
    backend_root: Path
    pdf_path: Path
    storage_dir: Path


def get_paths(pdf_path: Path | None = None) -> IngestPaths:
    pdf = pdf_path or DEFAULT_PDF_PATH
    return IngestPaths(
        project_root=PROJECT_ROOT,
        backend_root=BACKEND_ROOT,
        pdf_path=pdf,
        storage_dir=BACKEND_ROOT / "storage",
    )


def pdf_page_count(pdf_path: Path | None = None) -> int:
    path = pdf_path or DEFAULT_PDF_PATH
    if not path.is_file():
        raise FileNotFoundError(f"PDF no encontrado: {path}")
    return len(PdfReader(str(path)).pages)


def _attach_page_pdf(doc: Document) -> Document:
    """Añade page_pdf (1-based) a partir de metadata page (0-based)."""
    meta = dict(doc.metadata)
    raw = meta.get("page")
    if raw is not None:
        meta["page_pdf"] = int(raw) + 1
    doc.metadata = meta
    return doc


def page_pdf_1based(doc: Document) -> int | None:
    """Página PDF 1-based para eval (criterio A)."""
    if "page_pdf" in doc.metadata:
        return int(doc.metadata["page_pdf"])
    raw = doc.metadata.get("page")
    if raw is None:
        return None
    return int(raw) + 1


def load_pdf_documents(pdf_path: Path | None = None) -> list[Document]:
    path = pdf_path or DEFAULT_PDF_PATH
    if not path.is_file():
        raise FileNotFoundError(f"PDF no encontrado: {path}")
    docs = PyPDFLoader(str(path)).load()
    return [_attach_page_pdf(d) for d in docs]


def split_documents(
    docs: list[Document],
    *,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    return [_attach_page_pdf(c) for c in chunks]


def ingest_pdf(pdf_path: Path | None = None) -> tuple[list[Document], list[Document]]:
    """Carga y parte el PDF. Retorna (páginas, chunks)."""
    pages = load_pdf_documents(pdf_path)
    chunks = split_documents(pages)
    return pages, chunks


def chunk_length_stats(chunks: list[Document]) -> dict[str, float | int]:
    lengths = [len(c.page_content) for c in chunks]
    if not lengths:
        return {"count": 0, "min": 0, "max": 0, "mean": 0.0}
    return {
        "count": len(lengths),
        "min": min(lengths),
        "max": max(lengths),
        "mean": round(sum(lengths) / len(lengths), 1),
    }


def chunks_on_pages(chunks: list[Document], pages_1based: set[int]) -> list[Document]:
    return [c for c in chunks if page_pdf_1based(c) in pages_1based]
