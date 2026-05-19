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
- Health check: `curl http://localhost:8000/health`

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
