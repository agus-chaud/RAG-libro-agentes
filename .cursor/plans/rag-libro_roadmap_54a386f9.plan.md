---
name: RAG-LIBRO roadmap
overview: Implementar un proyecto RAG completo (backend FastAPI + frontend Next.js) sobre el PDF del libro, con enfoque eval-first, streaming SSE y workflow de Git por fases para portfolio profesional.
todos:
  - id: fase-0-scaffold
    content: Crear carpeta RAG-LIBRO y estructura base con env/gitignore/dependencias.
    status: completed
  - id: fase-05-eval
    content: Definir EVAL.md con 10 queries y criterios PASS/FAIL medibles.
    status: completed
  - id: fase-1a-notebook-ingest
    content: "1.1–1.3: Notebook scaffold + PyPDFLoader + splitter (1000/200) con metadata de página."
    status: completed
  - id: fase-1b-faiss-index
    content: "1.4–1.6: Embeddings MiniLM + FAISS en storage/ + carga idempotente (REBUILD_INDEX)."
    status: completed
  - id: fase-1c-lcel-chain
    content: "1.7–1.10: Retriever k=4 + prompt + chain LCEL + verificar get_llm() desde notebook."
    status: in_progress
  - id: fase-1d-rag-module
    content: "1.11–1.12: Extraer app/rag.py (answer_with_sources) y alinear notebook con el módulo."
    status: pending
  - id: fase-1e-eval-tune
    content: "1.13–1.18: run_eval_suite + pytest integration + tuning A/B + documentar ≥70% en EVAL.md."
    status: pending
  - id: fase-2a-scaffold
    content: "2.1–2.3: main.py, lifespan singleton FAISS, GET /health."
    status: pending
  - id: fase-2b-chat-sync
    content: "2.4–2.6: schemas Pydantic + POST /chat sync + errores HTTP."
    status: pending
  - id: fase-2c-cors
    content: "2.7: CORSMiddleware para http://localhost:3000."
    status: pending
  - id: fase-2d-rag-stream
    content: "2.8–2.9: stream_answer_with_sources en rag.py (astream, no fake stream)."
    status: pending
  - id: fase-2e-sse-endpoint
    content: "2.10–2.12: POST /chat/stream SSE (token, sources, done) sin bloquear loop."
    status: pending
  - id: fase-2f-api-tests
    content: "2.13–2.14: test_api.py con TestClient (health, chat, stream mínimo)."
    status: pending
  - id: fase-3a-next-scaffold
    content: "3.1–3.2: Next.js 14 + Tailwind + NEXT_PUBLIC_API_URL."
    status: completed
  - id: fase-3b-chat-shell
    content: "3.3–3.4: layout chat + estados idle | streaming | done | error."
    status: completed
  - id: fase-3c-sse-client
    content: "3.5–3.6: fetch-event-source POST + handlers token/sources/done."
    status: completed
  - id: fase-3d-sources-ui
    content: "3.7: badges de páginas bajo respuesta del asistente."
    status: completed
  - id: fase-3e-ui-gate
    content: "3.8: smoke E2E manual UI → API (query de EVAL.md)."
    status: completed
  - id: fase-3f-suggested-questions
    content: "3.9: preguntas sugeridas one-click (Q01,Q07,Q08,Q05,Q06); ocultar las ya enviadas."
    status: completed
  - id: fase-4-overview
    content: Documentar defensa técnica en PROJECT_OVERVIEW.md (gitignored).
    status: completed
  - id: fase-5-verify
    content: Validar flujo end-to-end, README final y evidencia de portfolio.
    status: completed
isProject: false
---

# Plan de implementación: RAG-LIBRO

## Objetivo

Construir en este proyecto una solución RAG funcional sobre el PDF **"30 Agents Every AI Engineer Must Build"**, con arquitectura separada (Python API + UI web), evaluación medible desde el inicio y trazabilidad de decisiones para entrevistas técnicas.

## Alcance y criterio de éxito

- Crear la base del proyecto en una carpeta nueva: `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO)`.
- Entregar backend FastAPI con endpoints `/health`, `/chat`, `/chat/stream`.
- Entregar frontend Next.js con chat streaming y fuentes (páginas) visibles.
- Definir y usar `EVAL.md` antes de implementar el core RAG.
- Alcanzar baseline de evaluación: al menos 70% de queries aprobadas.

## Arquitectura objetivo

```mermaid
flowchart LR
    nextUi[NextJsUI localhost3000] -->|HTTP JSON SSE| fastApi[FastAPI localhost8000]
    fastApi --> ragCore[RAGPipeline LangChain]
    ragCore --> vectorDb[FAISSIndex PersistedDisk]
    ragCore --> llmRouter[LLMRouter Groq OpenRouter Mock]
    ragCore --> pdfChunks[ChunkedPDFPages]
```



## Fases



```markdown
## Metodología — skill `senior-ai-engineer-mentor`

**Regla global**: en cada sesión de desarrollo (Fase 0 → 5), el agente debe **leer y aplicar** la skill [`senior-ai-engineer-mentor`](C:\Users\Dell\.agents\skills\senior-ai-engineer-mentor\SKILL.md) antes de implementar.

| Principio | Qué implica en la práctica |
|-----------|---------------------------|
| **CONCEPTS > CODE** | Explicar el *por qué* antes del snippet; no volcar soluciones completas sin que hayas corrido/entendido el paso anterior |
| **Libro = gimnasio** | Cruzar cada paso con capítulos del repo `30-Agents-Every-AI-Engineer-Must-Build` (sobre todo cap 06 para RAG, cap 02/04 según fase) |
| **Evidencia de mastery** | Tras cada fase, actualizar Engram (`mem_save`) con nivel `explored` → `practiced` según evidencia real |
| **Gates obligatorios** | No avanzar de fase sin pasar el *gate* de esa fase (ver tabla abajo) |

**Comandos útiles durante el proyecto**

- `/ai-mentor` — fuerza modo mentor aunque el mensaje sea operativo (“creá el endpoint”)
- `review` + tu código — feedback quirúrgico post-implementación
- `interview {concepto}` — simulacro antes de cerrar una fase (ej. `interview chunking-strategy`)
- `/no-mentor` — un solo turno sin mentoría (solo cuando necesitás velocidad pura)
```



### Fase 0 — Scaffold inicial

- Crear carpeta raíz `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO)`.
- Crear estructura base:
  - `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend)`
  - `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\frontend](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\frontend)`
  - `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\app](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\app)
  - `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\tests](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\tests)
  - `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\data](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\data)
  - `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\storage](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\storage)
- Crear archivos base: `.gitignore`, `.env.example`, `README.md`, `EVAL.md`.
- Inicializar entorno Python y `requirements.txt` alineado a LangChain 0.3+.
- Incorporar MockLLM reutilizable desde capítulo 06 como fallback offline.

### Fase 0.5 — Evaluación primero (eval-first)

- Diseñar `EVAL.md` con 10 queries (fáciles, medias, cross-chapter).
- Definir criterios binarios por query:
  - Recuperación de páginas esperadas en top-k.
  - Presencia mínima de conceptos clave en respuesta.
- Crear esqueleto de test en `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\tests\test_eval.py](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\backend\tests\test_eval.py)`.
- Completar páginas esperadas con inspección real del PDF (sin inventar referencias).

### Fase 1 — Core RAG en notebook

**Estado previo (Fase 0):** [`RAG-LIBRO/backend/app/llm.py`](RAG-LIBRO/backend/app/llm.py) ya tiene `get_llm()` con `groq | openrouter | mock` + fallback. En 1.10 solo **verificar** integración con LCEL, no reimplementar.

**Requisito crítico:** chunks con **página PDF 1-based** en metadata (`PyPDFLoader` usa `page` 0-based → +1 al evaluar criterio A).

**Gate de fase:** `pass_rate >= 0.70` en [`run_eval_suite`](RAG-LIBRO/backend/tests/test_eval.py) con embeddings reales; notebook reproducible; [`app/rag.py`](RAG-LIBRO/backend/app/rag.py) listo para Fase 2.

#### Bloque A — Notebook e ingestión (fase-1a)

| ID | Tarea | Gate |
|----|-------|------|
| 1.1 | Scaffold [`backend/notebooks/rag_exploration.ipynb`](RAG-LIBRO/backend/notebooks/rag_exploration.ipynb): paths, `load_dotenv`, check PDF | Kernel + ~542 páginas |
| 1.2 | Load con `PyPDFLoader`; inspeccionar `metadata` (`page`, `source`) | `len(docs)` = páginas PDF |
| 1.3 | `RecursiveCharacterTextSplitter` 1000/200; propagar `page` a cada chunk | chunks > 0, metadata ok |

#### Bloque B — Índice FAISS (fase-1b)

| ID | Tarea | Gate |
|----|-------|------|
| 1.4 | `HuggingFaceEmbeddings(all-MiniLM-L6-v2)` — **no** MockEmbeddings para eval A | vector dim estable |
| 1.5 | `FAISS.from_documents` → `backend/storage/faiss_index/` | carpeta persistida |
| 1.6 | Carga idempotente (`REBUILD_INDEX`); `load_local` si existe | 2ª corrida sin re-embedear |

#### Bloque C — Retriever y LCEL (fase-1c)

| ID | Tarea | Gate |
|----|-------|------|
| 1.7 | Retriever `k=4`; smoke Q01/Q05 con páginas 1-based en top-k | Q05: p.180–181 en top-4 |
| 1.8 | `ChatPromptTemplate` (solo contexto, citar páginas, “no sé”) + `format_docs` | prompt renderizado ok |
| 1.9 | Chain LCEL: retriever → prompt → `get_llm()` → `StrOutputParser()` | respuesta + `list[int]` páginas |
| 1.10 | Verificar `get_llm(provider=...)` desde notebook; `pytest test_llm_fallback.py` verde | wiring LLM ok |

#### Bloque D — Módulo `rag.py` (fase-1d)

| ID | Tarea | Gate |
|----|-------|------|
| 1.11 | Crear [`app/rag.py`](RAG-LIBRO/backend/app/rag.py): `build_or_load_vectorstore`, `get_retriever`, `answer_with_sources(query, k) -> {answer, pages}` | import desde `backend/` |
| 1.12 | Notebook importa `app.rag` (sin duplicar lógica) | misma salida notebook vs módulo |

Contrato para tests: [`test_eval.py`](RAG-LIBRO/backend/tests/test_eval.py) L102–104 espera `answer_with_sources`.

#### Bloque E — Eval y tuning (fase-1e)

| ID | Tarea | Gate |
|----|-------|------|
| 1.13 | `run_eval_suite` en notebook; tabla A/B por query | PASS rate calculado |
| 1.14 | `pytest tests/test_eval.py -m integration -v` | harness corre |
| 1.15 | Diagnóstico por FAIL: solo A → retrieval; solo B → prompt/LLM | patrón documentado |
| 1.16 | Tuning retrieval (una var.): `k` 4→6→8, `chunk_size` 1000→800, `overlap` 200→300 | mejora en cross-chapter |
| 1.17 | Tuning generación si A ok: prompt estricto, `temperature`, modelo real (no mock para B) | B pasa con proveedor real |
| 1.18 | Actualizar [`EVAL.md`](RAG-LIBRO/EVAL.md) + ADR-06 en [`PROJECT_OVERVIEW.md`](RAG-LIBRO/PROJECT_OVERVIEW.md); Engram `practiced` | **≥70%** PASS |

```mermaid
flowchart TD
    nb[Notebook] --> idx[FAISS storage]
    idx --> ret[Retriever k=4]
    ret --> lcel[LCEL + get_llm]
    lcel --> ragMod[app/rag.py]
    ragMod --> eval[run_eval_suite]
    eval --> tune{PASS menor 70%?}
    tune -->|solo A| retTune[chunk/k]
    tune -->|solo B| genTune[prompt/LLM]
    tune -->|ok| gate[Gate Fase 1]
```

**Fuera de Fase 1:** API HTTP → Fase 2a–2f; UI → Fase 3a–3e.

### Fase 2 — FastAPI + SSE

**Prerequisito:** gate Fase 1 — [`app/rag.py`](RAG-LIBRO/backend/app/rag.py) con `answer_with_sources` y eval ≥70%.

**Gate de fase:** `uvicorn` sin recargar FAISS por request; `GET /health` OK; `POST /chat` devuelve `{answer, pages}`; `POST /chat/stream` emite `sources` → `token`* → `done`; CORS para `http://localhost:3000`; `pytest tests/test_api.py` verde.

#### Bloque A — Scaffold y lifespan (fase-2a)

| ID | Tarea | Gate |
|----|-------|------|
| 2.1 | Crear [`backend/app/main.py`](RAG-LIBRO/backend/app/main.py): app FastAPI; documentar `uvicorn app.main:app --reload` en README | servidor arranca |
| 2.2 | `lifespan`: startup `build_or_load_vectorstore()` o `load_faiss_index()` + `set_vectorstore`; shutdown opcional `clear_vectorstore_cache` | 2ª request no re-embedea |
| 2.3 | `GET /health` → `{"status":"ok","index_loaded":true}` (o similar) | curl 200 |

#### Bloque B — Contrato HTTP sync (fase-2b)

| ID | Tarea | Gate |
|----|-------|------|
| 2.4 | Schemas Pydantic: `ChatRequest { message, k? }`, `ChatResponse { answer, pages }` | visible en `/docs` |
| 2.5 | `POST /chat` → `answer_with_sources(request.message, k)` | curl devuelve answer + pages |
| 2.6 | Errores: 422 validación; 503 si índice ausente (mensaje accionable) | test o curl sin índice |

#### Bloque C — CORS (fase-2c)

| ID | Tarea | Gate |
|----|-------|------|
| 2.7 | `CORSMiddleware`: origins `http://localhost:3000`, methods `GET,POST`, headers `Content-Type` | preflight OK desde browser (Fase 3) |

#### Bloque D — Streaming en el core (fase-2d)

| ID | Tarea | Gate |
|----|-------|------|
| 2.8 | En [`rag.py`](RAG-LIBRO/backend/app/rag.py): `stream_answer_with_sources(query, k)` — retrieval una vez, yield páginas, luego `chain.astream()` (tokens reales del LLM) | generator documentado |
| 2.9 | Contrato interno: `("sources", pages)`, `("token", str)`, `("done", None)` — no simular stream post-`invoke` | docstring o nota en README |

#### Bloque E — Endpoint SSE (fase-2e)

| ID | Tarea | Gate |
|----|-------|------|
| 2.10 | `POST /chat/stream`: `EventSourceResponse` (`sse-starlette`) → SSE `event: sources`, `event: token`, `event: done` con `data` JSON | curl/httpie ve stream |
| 2.11 | Orden: `sources` primero (páginas del retriever), luego tokens, luego `done` | UI puede mostrar badges durante el stream |
| 2.12 | Evitar bloquear event loop (usar `astream` o `run_in_executor` si el LLM es sync) | revisión: ¿bloqueás el loop? |

#### Bloque F — Tests API (fase-2f)

| ID | Tarea | Gate |
|----|-------|------|
| 2.13 | [`backend/tests/test_api.py`](RAG-LIBRO/backend/tests/test_api.py): `TestClient` — health, chat sync (mock LLM o fixture) | `pytest tests/test_api.py -v` |
| 2.14 | Test mínimo `/chat/stream`: leer eventos `sources` + al menos un `token` | opcional `@pytest.mark.slow` con LLM real |

```mermaid
flowchart TD
    start[Lifespan startup] --> vs[FAISS en memoria]
    vs --> health[GET /health]
    vs --> sync[POST /chat]
    vs --> streamFn[stream_answer_with_sources]
    streamFn --> sse[POST /chat/stream]
    sync --> tests[test_api.py]
    sse --> tests
```

**Fuera de Fase 2:** UI Next.js → Fase 3.

### Fase 3 — Frontend Next.js

**Prerequisito:** gate Fase 2 — API estable; SSE verificado con curl.

**Gate de fase:** chat en `localhost:3000` con streaming visible; badges de páginas tras evento `sources`; estados `idle | streaming | done | error` correctos.

#### Bloque A — Scaffold (fase-3a)

| ID | Tarea | Gate |
|----|-------|------|
| 3.1 | `create-next-app` en [`frontend/`](RAG-LIBRO/frontend): Next 14, App Router, Tailwind | `npm run dev` en :3000 |
| 3.2 | `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000` | variable leída en cliente |

#### Bloque B — Shell del chat (fase-3b)

| ID | Tarea | Gate |
|----|-------|------|
| 3.3 | Layout: lista de mensajes + input + enviar | UI estática renderiza |
| 3.4 | Estado `idle \| streaming \| done \| error`; input disabled mientras `streaming` | transiciones visibles |

#### Bloque C — Cliente SSE (fase-3c)

| ID | Tarea | Gate |
|----|-------|------|
| 3.5 | `@microsoft/fetch-event-source`: `POST` a `/chat/stream` con `{ message }` | sin error CORS |
| 3.6 | Handlers por `event`: append `token`, set `pages` en `sources`, cerrar en `done` | texto crece en pantalla |

#### Bloque D — Fuentes (fase-3d)

| ID | Tarea | Gate |
|----|-------|------|
| 3.7 | Badges/chips con `pages[]` bajo mensaje del asistente | páginas visibles en UI |

#### Bloque E — Gate E2E UI (fase-3e)

| ID | Tarea | Gate |
|----|-------|------|
| 3.8 | Smoke manual: pregunta de `EVAL.md` → respuesta stream + fuentes | checklist anticipado Fase 5 |

#### Bloque F — UX demo (fase-3f)

| ID | Tarea | Gate |
|----|-------|------|
| 3.9 | `SuggestedQuestions` + `lib/suggestedQuestions.ts`: 5 botones (Q01, Q07, Q08, Q05, Q06); clic = `handleSubmit`; ocultar sugerencias ya enviadas (match exacto user) | B1, B8, B10 en `CHECKLIST_E2E.md`; doc en `frontend/README.md`, `EVAL.md` § UI |

```mermaid
flowchart LR
    f2f[Gate Fase 2] --> f3a[3a Next scaffold]
    f3a --> f3b[3b chat shell]
    f3b --> f3c[3c SSE client]
    f3c --> f3d[3d sources UI]
    f3d --> f3e[3e E2E gate]
    f3e --> f3f[3f suggested Q]
```

### Fase 4 — Documento de defensa técnica

- Crear `[C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\PROJECT_OVERVIEW.md](C:\Users\Dell\Agus\Ai Agents Imran Ahmad\RAG-LIBRO\PROJECT_OVERVIEW.md)` (gitignored).
- Documentar decisiones, trade-offs, limitaciones y plan de escalado.
- Mantenerlo actualizado durante el desarrollo, no solo al final.

### Fase 5 — Cierre y validación end-to-end

- Consolidar `README.md` con arquitectura, setup y decisiones técnicas.
- Verificar:
  - tests backend
  - `/docs` de FastAPI
  - llamadas sync y streaming
  - flujo completo UI -> API -> RAG
- Preparar evidencia de portfolio (historial de fases, tags y resultados de eval).

## Estrategia Git y entregables

- Branch por fase: `fase-0` a `fase-5-readme`.
- Commits con conventional commits (`feat`, `fix`, `docs`, `test`, `chore`).
- PR por fase con squash merge y actualización de README.
- Mantener secretos fuera de git (`.env`), comitear solo `.env.example`.

## Riesgos y mitigaciones

- Riesgo: bajo rendimiento inicial del retrieval.
  - Mitigación: ajuste iterativo de `chunk_size`, `chunk_overlap`, `k`, prompt y comparación Groq/OpenRouter.
- Riesgo: latencia alta en generación.
  - Mitigación: SSE + carga singleton + opción de proveedor alterno.
- Riesgo: calidad no medible.
  - Mitigación: `EVAL.md` y `test_eval.py` desde el inicio.

## Orden de ejecución recomendado

1. Fase 0
2. Fase 0.5
3. Fase 1 (1a → 1e)
4. Fase 2 (2a → 2f)
5. Fase 3 (3a → 3e)
6. Fase 4
7. Fase 5

