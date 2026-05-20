# RAG-LIBRO

RAG sobre el PDF **"30 Agents Every AI Engineer Must Build"** (Imran Ahmad): backend Python (LangChain + FastAPI) y frontend Next.js con streaming SSE.

Proyecto de portfolio con enfoque **eval-first** (`EVAL.md` + tests), APIs de LLMs gratuitos y modo offline vía `MockLLM` (adaptado del capítulo 06 del repo del libro).

**Baseline actual:** 7/10 PASS (70%) con Groq `llama-3.1-8b-instant`, `RETRIEVER_K=4` — validado en benchmark Fase A/B (2026-05-20). Detalle en `EVAL.md` § Benchmark de modelos.

## Estructura

```
RAG-LIBRO/
├── backend/
│   ├── app/          # Pipeline RAG, LLM router, API (fases 1–2)
│   ├── data/         # libro.pdf (gitignored)
│   ├── storage/      # índice FAISS persistido (gitignored)
│   ├── eval_runner.py # benchmark de modelos y sweep de k (Fase 1e+)
│   └── tests/        # evals automatizados (fase 0.5+)
├── frontend/         # Next.js 14 + chat SSE (fase 3)
├── EVAL.md           # 10 queries y criterios PASS/FAIL
└── .env
```

## Requisitos

- Python 3.10+
- Node.js 18+ (fase 3)

## Setup rápido (Fase 0)

```powershell
cd RAG-LIBRO\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example ..\.env
```

Colocá el PDF en `backend/data/libro.pdf` (ya copiado desde Downloads si ejecutaste el scaffold).

### Si moviste la carpeta del proyecto

Los scripts de `.venv` guardan la ruta absoluta del Python. Si ves `Fatal error in launcher: Unable to create process` apuntando a otra carpeta, **borrá `.venv` y recrealo** en `backend/`:

```powershell
cd RAG-LIBRO\backend
Remove-Item -Recurse -Force .venv
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Para tests de ingestión (Fase 1a) alcanza con:

```powershell
python -m pip install python-dotenv pypdf pytest langchain langchain-core langchain-community langchain-text-splitters faiss-cpu numpy
```

Preferí `python -m pytest` en lugar de `pytest` directo (siempre usa el intérprete del venv activo).

**LLM (config recomendada, post-benchmark):**

| Variable | Valor | Notas |
|----------|-------|-------|
| `LLM_FALLBACK_CHAIN` | `groq,openrouter,mock` | Groq primero (mejor PASS en eval); OR como respaldo |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | 7/10 en k=4/6/8; 70B versatile quedó en 6/10 |
| `OPENROUTER_MODEL` | `meta-llama/llama-3.3-70b-instruct:free` | Fallback; cupo free ~50 req/día |
| `OPENROUTER_MODEL_FALLBACK` | `nvidia/nemotron-3-super-120b-a12b:free` | Segundo intento dentro de OR |
| `RETRIEVER_K` | `4` | Óptimo en Fase B (k=6/8 no mejoran PASS rate) |

Ante error de API, timeout o respuesta vacía pasa al siguiente proveedor. Sin claves válidas termina en `mock`.

## Levantar la API (Fase 2)

Requiere que el índice FAISS esté construido (Fase 1 completa).

```powershell
cd RAG-LIBRO\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

- API en `http://localhost:8000`
- Docs interactivos en `http://localhost:8000/docs`

### Endpoints disponibles (Fase 2)

#### `GET /health`

```powershell
curl http://localhost:8000/health
# → {"status":"ok","index_loaded":true}
```

`index_loaded: false` indica que el índice FAISS no está en RAM — ejecutá el notebook de Fase 1 primero para construirlo en `backend/storage/faiss_index/`.

#### `POST /chat` — respuesta sincrónica

```powershell
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "What is the ReAct loop?"}'
# → {"answer":"...","pages":[23,45]}
```

Parámetros del body:

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `message` | string | requerido | Pregunta sobre el libro (mínimo 1 carácter) |
| `k` | int | `4` | Chunks a recuperar (rango 1–20; default validado en benchmark) |

#### `POST /chat/stream` — respuesta en streaming (SSE)

```powershell
curl -X POST http://localhost:8000/chat/stream `
  -H "Content-Type: application/json" `
  -d '{"message": "What is the ReAct loop?"}' `
  --no-buffer
# event: sources → event: token (×N) → event: done
```

Errores:
- **422** — payload inválido (ej. `message` vacío) — Pydantic lo valida automáticamente.
- **503** — índice FAISS no cargado — reiniciá el servidor.

### CORS

La API permite requests cross-origin desde `http://localhost:3000` (Next.js). Si desarrollás el frontend en otro puerto, agregá el origen en `app.add_middleware(CORSMiddleware, allow_origins=[...])` dentro de `backend/app/main.py`.

No uses `allow_origins=["*"]` — bloquea `allow_credentials` y abre la API a cualquier origen externo en producción.

## Frontend (Fases 3a y 3b)

Interfaz de chat en **Next.js 14** (App Router + Tailwind). Por ahora el texto del asistente es **simulado** en el navegador; la conexión real al stream SSE del backend llega en la fase **3c**.

Requisitos: Node.js 18+. La API en `:8000` no es obligatoria para probar la UI del chat, pero conviene tenerla lista para las fases siguientes.

```powershell
cd RAG-LIBRO\frontend
copy .env.example .env.local
npm install
npm run dev
```

- UI en `http://localhost:3000`
- Variable `NEXT_PUBLIC_API_URL` en `.env.local` (default `http://localhost:8000`) — se muestra en el header del chat vía `frontend/lib/api.ts`

### Qué hay hecho

| Fase | Qué es | Qué podés ver |
|------|--------|----------------|
| **3a** | Proyecto Next creado con `create-next-app` | La app arranca en el puerto 3000; el badge **API:** muestra la URL del backend |
| **3b** | Pantalla de chat (sin SSE todavía) | Lista de mensajes, caja de texto, botón **Enviar**, indicador de estado |

### Estados del chat (3b)

La UI maneja cuatro estados. El input y el botón **Enviar** solo funcionan cuando no está en *Generando…*:

| Estado | Significado en pantalla |
|--------|-------------------------|
| `idle` | Listo — podés escribir |
| `streaming` | Generando… — entrada bloqueada, ves el texto del asistente aparecer de a poco (simulado) |
| `done` | Completado — respuesta fijada en la lista, podés enviar otra pregunta |
| `error` | Error — mensaje en rojo; podés reintentar |

Para probar el estado de error en desarrollo, enviá exactamente el mensaje `__mock_error__`.

### Estructura del frontend (3b)

```
frontend/
├── app/page.tsx              # Monta el chat
├── components/
│   ├── ChatShell.tsx         # Orquesta mensajes y estados
│   ├── MessageList.tsx       # Burbujas usuario / asistente
│   ├── ChatInput.tsx         # Textarea + Enviar
│   ├── ChatStatusBar.tsx     # Pill de estado (idle / streaming / …)
│   └── ApiUrlBadge.tsx       # Muestra NEXT_PUBLIC_API_URL
└── lib/
    ├── api.ts                # URL del backend
    └── chat.ts               # Tipos ChatStatus, ChatMessage
```

Próximo paso (**3c**): conectar `POST /chat/stream` con `@microsoft/fetch-event-source` y reemplazar el mock en `ChatShell.tsx`.

## Evaluación y benchmark de modelos

Golden set de 10 queries en `EVAL.md` (criterios A: retrieval, B: generación). Correr desde `backend/`:

```powershell
.\.venv\Scripts\Activate.ps1
# Suite completa (default: k=4, cadena del .env)
python eval_runner.py

# Benchmark: otro modelo / proveedor y guardar en EVAL.md
python eval_runner.py --k 4 --groq-model llama-3.1-8b-instant --chain groq --save-results

# Profiling de k (delay auto-escala con k para límite TPM de Groq)
python eval_runner.py --k 4 6 8 --chain groq --save-results

# Smoke: una query (Q01) para validar disponibilidad sin gastar cupo
python eval_runner.py --smoke --openrouter-model meta-llama/llama-3.3-70b-instruct:free --chain openrouter

pytest tests/test_eval.py -v -m "not integration"   # dataset / criterios
pytest tests/test_eval.py -v -m integration         # pipeline + LLM real
pytest tests/test_api.py -v                         # API (mock, sin red)
```

Flags útiles: `--groq-model`, `--openrouter-model`, `--chain`, `--smoke`, `--save-results`, `--delay`, `--inter-k-pause`.

## Roadmap

| Fase | Entregable | Estado |
|------|------------|--------|
| 0 | Scaffold | ✓ |
| 0.5 | `EVAL.md` + `test_eval.py` | ✓ |
| 1 | Notebook RAG, FAISS, `rag.py`, eval ≥70% | ✓ (7/10) |
| 1e+ | `eval_runner.py`, benchmark modelos (Fase A/B) | ✓ |
| 2 | FastAPI `/health`, `/chat`, `/chat/stream`, tests API | ✓ |
| 3a | Next.js 14 scaffold + `NEXT_PUBLIC_API_URL` | ✓ |
| 3b | Shell del chat (layout + estados idle/streaming/done/error) | ✓ |
| 3c–3e | Cliente SSE, badges de páginas, E2E UI | pendiente |
| 4 | `PROJECT_OVERVIEW.md` (gitignored, defensa técnica) | en curso |
| 5 | E2E + pulido portfolio | pendiente |

## Referencias

- Libro / repo: `30-Agents-Every-AI-Engineer-Must-Build`
- Cap. 06 — RAG y mocks: `chapter06/agent_utils.py`
