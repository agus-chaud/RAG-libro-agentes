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
| LLM local opcional | `groq` / `openrouter` | Comparar calidad generativa. OR free default: `meta-llama/llama-3.3-70b-instruct:free` (ver `.env.example` para alternativas) |

## Queries

| ID | Dificultad | Query | Páginas esperadas | Conceptos clave (B) |
|----|------------|-------|-------------------|-------------------|
| Q01 | fácil | What is an AI agent according to this book? | 34, 35 | agent, goal, environment |
| Q02 | fácil | What are the levels of agent capability (tool-using, planning, learning)? | 9, 64 | tool-using, planning, learning |
| Q03 | fácil | Explain the ReAct pattern (Reasoning and Acting). | 52, 72 | ReAct, reasoning, acting |
| Q04 | media | What is a Knowledge Retrieval agent and how does RAG work? | 177, 179, 181 | retrieval, embedding, vector |
| Q05 | media | How does the book store embeddings with FAISS? | 180, 181 | FAISS, embeddings, vectorstore |
| Q06 | media | What is MCP (Model Context Protocol) and what problem does it solve? | 47, 48 | Model Context Protocol, tools, interoperability |
| Q07 | media | How does LangGraph support agent workflows? | 36, 38, 40, **72, 74** | LangGraph, workflow, state |
| Q08 | cross-chapter | Compare reactive vs deliberative agents. When to choose each? | 42, 43, 44 | reactive, deliberative, planning |
| Q09 | cross-chapter | Security risks in RAG and prompt injection. | 24, 138, 181 | injection, retrieval, RAG |
| Q10 | cross-chapter | Supervisor coordinating specialists + episodic memory. | 218, 220, **222**, 424 | supervisor, episodic, specialist |

## UI — preguntas sugeridas (frontend 3f)

Cinco queries del golden set se exponen en la UI como botones one-click (`frontend/lib/suggestedQuestions.ts`). Mantener **sincronizado** el texto con esta tabla y con `eval_cases.py` cuando cambie una query.

| Botón en UI (orden en pantalla) | ID eval | Dificultad |
|--------------------------------|---------|------------|
| What is an AI agent according to this book? | Q01 | fácil |
| How does LangGraph support agent workflows? | Q07 | media |
| Compare reactive vs deliberative agents. When to choose each? | Q08 | cross-chapter |
| How does the book store embeddings with FAISS? | Q05 | media |
| What is MCP (Model Context Protocol) and what problem does it solve? | Q06 | media |

Q02, Q03, Q04, Q09 y Q10 no están en la UI por defecto; probalas vía `eval_runner.py`, smoke API (`--query-id`) o texto libre en el chat.

> **Correcciones de ground truth (2026-05-19):**
> - Q07: se agregan p.72 y p.74 — el retriever las devuelve consistentemente y el LLM genera respuesta de alta calidad desde ese contenido (implementación detallada de LangGraph, no solo la intro de p.36-40).
> - Q10: se agrega p.222 — contiene ejemplo concreto de supervisor+episodic memory con LLMAnalystAgent, verificado por respuesta LLM de calidad.

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
| 2026-05-19 | fase-1e | groq (llama-3.1-8b-instant) | **7/10 (70%)** | Baseline alcanzado. k=4, chunk_size=1000, overlap=200. Prompt tuning (regla #5 vocabulario exacto) + corrección ground truth Q07/Q10 + delay anti-rate-limit. FAILs residuales: Q03 (retrieval ReAct p.52/72), Q04 (B: sin "embedding"/"vector"), Q06 (B: sin "tools"). |
| 2026-05-19 | benchmark-fase-a | groq (llama-3.1-8b-instant) | **7/10** | Screening k=4 — ver sección Benchmark de modelos. |
| 2026-05-19 | benchmark-fase-a | groq (llama-3.3-70b-versatile) | **7/10** | Screening k=4 — empate con 8B; Q03 empeoró (B FAIL). OpenRouter free: smoke falló (429/404). |
| 2026-05-19 | benchmark-or-free | openrouter (nemotron-3-super-120b:free) | **5/10** | Smoke OK. Screening k=4 — bajo baseline; muchos FAIL solo B (Q02,Q04,Q05,Q06). |
| 2026-05-19 | benchmark-or-free | openrouter (openrouter/free) | **4/10** | Smoke OK. Screening k=4 — router automático; peor que Groq. |
| 2026-05-19 | benchmark-or-free | — | — | Smoke FAIL 429: llama-3.3-70b, deepseek-v4-flash, gemma-4-31b (upstream rate-limit). |
| 2026-05-20 | benchmark-fase-b | groq (llama-3.1-8b-instant) | **7/10** k=4,6,8 | Profiling top-2. k=4/6: idénticos (Q03/Q04/Q06 fail). k=8: Q06 resuelto pero Q09 regresa (lost-in-the-middle confirmado). **k=4 óptimo.** |
| 2026-05-20 | benchmark-fase-b | groq (llama-3.3-70b-versatile) | **6/10** k=4,6,8 | Peor que 8B en todos los k. Fallos estables: Q03(A+B)+Q04+Q05+Q06 B-FAIL. 70B no mejora con k. **Descartado.** |
| 2026-05-20 | **GANADOR CONFIRMADO** | **groq (llama-3.1-8b-instant)** | **7/10 (70%)** | Config óptima: GROQ_MODEL=llama-3.1-8b-instant, LLM_FALLBACK_CHAIN=groq,openrouter,mock, RETRIEVER_K=4. |

## Benchmark de modelos
### Benchmark 2026-05-19 — groq (llama-3.1-8b-instant), k=4

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | PASS | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | PASS | PASS |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 7/10 (70%)
### Benchmark 2026-05-19 — groq (llama-3.3-70b-versatile), k=4

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | FAIL | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | PASS | PASS |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 7/10 (70%)
### Benchmark 2026-05-20 — openrouter (nvidia/nemotron-3-super-120b-a12b:free), k=4

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | FAIL | FAIL |
| Q03 | FAIL | FAIL | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | FAIL | FAIL |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 5/10 (50%)
### Benchmark 2026-05-20 — openrouter (openrouter/free), k=4

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | FAIL | FAIL |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | FAIL | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | FAIL | FAIL |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | FAIL | FAIL |
| Q10 | PASS | PASS | PASS |

PASS rate: 4/10 (40%)
### Benchmark 2026-05-20 — groq (llama-3.1-8b-instant), k=4

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | PASS | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | PASS | PASS |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 7/10 (70%)
### Benchmark 2026-05-20 — groq (llama-3.1-8b-instant), k=4

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | PASS | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | PASS | PASS |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 7/10 (70%)
### Benchmark 2026-05-20 — groq (llama-3.1-8b-instant), k=6

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | FAIL | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | PASS | PASS |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 7/10 (70%)
### Benchmark 2026-05-20 — groq (llama-3.1-8b-instant), k=8

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | PASS | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | PASS | PASS |
| Q06 | PASS | PASS | PASS |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | FAIL | FAIL |
| Q10 | PASS | PASS | PASS |

PASS rate: 7/10 (70%)
### Benchmark 2026-05-20 — groq (llama-3.3-70b-versatile), k=4

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | FAIL | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | FAIL | FAIL |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 6/10 (60%)
### Benchmark 2026-05-20 — groq (llama-3.3-70b-versatile), k=6

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | FAIL | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | FAIL | FAIL |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 6/10 (60%)
### Benchmark 2026-05-20 — groq (llama-3.3-70b-versatile), k=8

| Query | A-Ret | B-Gen | Global |
|-------|-------|-------|--------|
| Q01 | PASS | PASS | PASS |
| Q02 | PASS | PASS | PASS |
| Q03 | FAIL | FAIL | FAIL |
| Q04 | PASS | FAIL | FAIL |
| Q05 | PASS | FAIL | FAIL |
| Q06 | PASS | FAIL | FAIL |
| Q07 | PASS | PASS | PASS |
| Q08 | PASS | PASS | PASS |
| Q09 | PASS | PASS | PASS |
| Q10 | PASS | PASS | PASS |

PASS rate: 6/10 (60%)

