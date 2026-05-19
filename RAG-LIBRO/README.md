# RAG-LIBRO

RAG sobre el PDF **"30 Agents Every AI Engineer Must Build"** (Imran Ahmad): backend Python (LangChain + FastAPI) y frontend Next.js con streaming SSE.

Proyecto de portfolio con enfoque **eval-first** (`EVAL.md` + tests), APIs de LLMs gratuitos y modo offline vía `MockLLM` (adaptado del capítulo 06 del repo del libro).

## Estructura

```
RAG-LIBRO/
├── backend/
│   ├── app/          # Pipeline RAG, LLM router, API (fases 1–2)
│   ├── data/         # libro.pdf (gitignored)
│   ├── storage/      # índice FAISS persistido (gitignored)
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

**LLM:** cadena `openrouter → groq → mock` (`LLM_FALLBACK_CHAIN`). Modelo principal en OpenRouter: `google/gemma-2-9b-it:free`. Ante error de API, timeout o respuesta vacía pasa al siguiente. Sin claves válidas termina en `mock`.

## Levantar la API (Fase 2)

Requiere que el índice FAISS esté construido (Fase 1 completa).

```powershell
cd RAG-LIBRO\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

- API en `http://localhost:8000`
- Docs interactivos en `http://localhost:8000/docs`

### Endpoints disponibles (Fase 2a–2b)

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
| `k` | int | `4` | Chunks a recuperar del índice (rango 1–20) |

Errores:
- **422** — payload inválido (ej. `message` vacío) — Pydantic lo valida automáticamente.
- **503** — índice FAISS no cargado — reiniciá el servidor.

### CORS

La API permite requests cross-origin desde `http://localhost:3000` (Next.js). Si desarrollás el frontend en otro puerto, agregá el origen en `app.add_middleware(CORSMiddleware, allow_origins=[...])` dentro de `backend/app/main.py`.

No uses `allow_origins=["*"]` — bloquea `allow_credentials` y abre la API a cualquier origen externo en producción.

## Roadmap

| Fase | Entregable |
|------|------------|
| 0 | Scaffold (este commit) |
| 0.5 | `EVAL.md` completo + `test_eval.py` |
| 1 | Notebook RAG + `llm.py` (groq / openrouter / mock) |
| 2 | FastAPI `/health`, `/chat`, `/chat/stream` |
| 3 | UI Next.js con fuentes por página |
| 4 | `PROJECT_OVERVIEW.md` (gitignored) |
| 5 | E2E + README final |

## Referencias

- Libro / repo: `30-Agents-Every-AI-Engineer-Must-Build`
- Cap. 06 — RAG y mocks: `chapter06/agent_utils.py`
