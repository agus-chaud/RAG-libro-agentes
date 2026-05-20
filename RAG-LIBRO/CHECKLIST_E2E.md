# Checklist E2E — RAG-LIBRO (Fase 3e → Fase 5)

> **Gate 3.8 (fase-3e):** smoke automatizado en `scripts/smoke_ui_e2e.py`.  
> **Fase 5:** repetir este checklist con evidencia (capturas o notas en commit/PR).

## Prerrequisitos

- [ ] `backend/data/libro.pdf` presente
- [ ] Índice FAISS en `backend/storage/faiss_index/` (`index_loaded: true` en `/health`)
- [ ] `.env` en raíz `RAG-LIBRO/` con cadena LLM válida (recomendado: `groq,openrouter,mock`)
- [ ] Backend: `uvicorn app.main:app --reload` → `http://localhost:8000`
- [ ] Frontend: `npm run dev` en `frontend/` → `http://localhost:3000`
- [ ] `frontend/.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000`

## A — Smoke automatizado (API, mismo contrato que la UI)

```powershell
cd RAG-LIBRO\backend
.\.venv\Scripts\Activate.ps1
python ..\scripts\smoke_ui_e2e.py
# Otra query del golden set:
python ..\scripts\smoke_ui_e2e.py --query-id Q03
```

Criterios PASS del script:

| # | Criterio |
|---|----------|
| A1 | `GET /health` → `index_loaded: true` |
| A2 | `POST /chat/stream` emite `event: sources` con `data` = JSON array de enteros |
| A3 | Al menos un `event: token` |
| A4 | `event: done` al final |
| A5 | Respuesta acumulada ≥ 20 caracteres |

## B — Smoke manual en UI (localhost:3000)

Usar **Q01** de `EVAL.md` (o pegar desde la tabla):

> *What is an AI agent according to this book?*

| # | Paso | Esperado | ✓ |
|---|------|----------|---|
| B1 | Abrir `http://localhost:3000` | Header muestra API `http://localhost:8000` | |
| B2 | Estado inicial | Pill **Listo** (`idle`) | |
| B3 | Enviar Q01 | Pill pasa a **Generando…** (`streaming`); input deshabilitado | |
| B4 | Durante stream | Texto del asistente crece token a token (cursor parpadeante) | |
| B5 | Durante stream | Chips ámbar **p. N** aparecen bajo la burbuja (evento `sources`) | |
| B6 | Al terminar | Pill **Completado** (`done`); mensaje fijo en historial | |
| B7 | Tras completar | Chips de páginas persisten bajo el mensaje del asistente | |
| B8 | Segunda pregunta | Input habilitado de nuevo | |
| B9 | Error forzado | Con backend apagado: pill **Error** + mensaje legible | |

## C — Regresión backend (CI / local)

```powershell
cd RAG-LIBRO\backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v -m "not integration"   # suite completa offline
# O por archivo:
python -m pytest tests/test_api.py -v
python -m pytest tests/test_eval.py -v -m "not integration"
```

**Última corrida (2026-05-20, Fase 5):** **55 passed, 10 deselected, 3 warnings — 92.8 s.**
Cubre ingestión, vectorstore, RAG core, LLM fallback, MockLLM, API (health/chat/stream con 422/503) y dataset de eval.

## D — Fase 5 (cierre portfolio)

| # | Item | Estado |
|---|------|--------|
| D1 | `pytest tests/test_eval.py -v -m integration` → PASS rate ≥ 70% documentado en `EVAL.md` | ✓ 7/10 (`EVAL.md` § Registro 2026-05-20) |
| D2 | `curl` sync + stream documentados en `README.md` probados | Cubierto por smoke A (mismo contrato) |
| D3 | `/docs` FastAPI revisado | Manual al hacer demo |
| D4 | Captura o GIF del chat con Q01 + fuentes | Pendiente humano |
| D5 | Tag git `fase-5-readme` o PR con checklist B marcado | Pendiente humano |
| D6 | Sección Arquitectura + Validación E2E en `README.md` | ✓ 2026-05-20 |
| D7 | `PROJECT_OVERVIEW.md` (ADRs 01–12, escalado, límites) | ✓ Fase 4 |

## Registro smoke 3e

| Fecha | Query | Script | UI manual | Notas |
|-------|-------|--------|-----------|-------|
| 2026-05-20 | Q01 | **PASS** (`pages=[2,32,34,36]`, 1 token batch, 171 chars) | pendiente usuario (B1–B9) | Gate API OK; overlap eval p.34. `npm run build` frontend OK. |

## Registro regresión backend (Fase 5)

| Fecha | Comando | Resultado | Notas |
|-------|---------|-----------|-------|
| 2026-05-20 | `pytest tests/ -v -m "not integration"` | **55 passed**, 10 deselected, 3 warnings, 92.8 s | Cierre Fase 5 ítem D6. SwigPy deprecation warnings vienen de FAISS — no acción. |
