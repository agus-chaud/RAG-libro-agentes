# Evaluación RAG — RAG-LIBRO

> **Estado:** completo (Fase 0.5). Páginas verificadas en `backend/data/libro.pdf` (542 páginas, índice PDF 1-based) con `pypdf` el 2026-05-18.
>
> Fuente machine-readable: `backend/app/eval_cases.py` (mantener sincronizado).

## Objetivo

Baseline medible **antes** de tunear el pipeline: **≥ 70%** de queries en PASS (7/10).

## Criterios por query (binarios)

| Criterio | PASS si… |
|----------|----------|
| **A — Retrieval** | Al menos una página esperada aparece en el top-k de chunks recuperados |
| **B — Respuesta** | La respuesta contiene **todos** los conceptos clave listados (match flexible, case-insensitive) |

Una query **PASS** requiere A **y** B.

## Parámetros de eval

| Parámetro | Valor inicial | Notas |
|-----------|---------------|--------|
| `k` | 4 | Retriever top-k |
| `chunk_size` / `overlap` | 1000 / 200 | Fase 1 |
| LLM en CI | `mock` | Reproducible sin API |
| LLM local opcional | `groq` / `openrouter` | Comparar calidad generativa |

## Queries

| ID | Dificultad | Query | Páginas esperadas | Conceptos clave (B) |
|----|------------|-------|-------------------|-------------------|
| Q01 | fácil | What is an AI agent according to this book? | 34, 35 | agent, goal, environment |
| Q02 | fácil | What are the levels of agent capability (tool-using, planning, learning)? | 9, 64 | tool-using, planning, learning |
| Q03 | fácil | Explain the ReAct pattern (Reasoning and Acting). | 52, 72 | ReAct, reasoning, acting |
| Q04 | media | What is a Knowledge Retrieval agent and how does RAG work? | 177, 179, 181 | retrieval, embedding, vector |
| Q05 | media | How does the book store embeddings with FAISS? | 180, 181 | FAISS, embeddings, vectorstore |
| Q06 | media | What is MCP (Model Context Protocol) and what problem does it solve? | 47, 48 | Model Context Protocol, tools, interoperability |
| Q07 | media | How does LangGraph support agent workflows? | 36, 38, 40 | LangGraph, workflow, state |
| Q08 | cross-chapter | Compare reactive vs deliberative agents. When to choose each? | 42, 43, 44 | reactive, deliberative, planning |
| Q09 | cross-chapter | Security risks in RAG and prompt injection. | 24, 138, 181 | injection, retrieval, RAG |
| Q10 | cross-chapter | Supervisor coordinating specialists + episodic memory. | 218, 220, 424 | supervisor, episodic, specialist |

### Notas de inspección PDF

- **Q01–Q03:** Capítulos 1–2 (fundamentos y toolkit).
- **Q04–Q05:** Cap. 6 — `FAISS.from_documents` y `RecursiveCharacterTextSplitter` (~p.180–181).
- **Q06:** MCP en introducción arquitectónica (~p.47–48).
- **Q08:** Figuras 1.x reactive/deliberative (~p.42–44).
- **Q09:** Prompt injection (Cap. 4) + pipeline RAG (Cap. 6).
- **Q10:** Supervisor multi-agente (p.218) + memoria episódica (p.220) + ejemplo LangGraph financiero (p.424).

## Cómo correr

```powershell
cd RAG-LIBRO\backend
.\.venv\Scripts\Activate.ps1
pytest tests/test_eval.py -v
# Solo criterios / dataset (Fase 0.5):
pytest tests/test_eval.py -v -m "not integration"
# Tras Fase 1 (pipeline RAG):
pytest tests/test_eval.py -v -m integration
```

Desde código (Fase 1+):

```python
from tests.test_eval import run_eval_suite

report = run_eval_suite(lambda q, k=4: rag.answer_with_sources(q, k=k))
print(report["pass_rate"], report["meets_baseline"])
```

## Registro de corridas

| Fecha | Commit | Proveedor | PASS | Notas |
|-------|--------|-----------|------|-------|
| 2026-05-18 | fase-0.5 | — | —/10 | Dataset + tests unitarios; integración pendiente Fase 1 |
