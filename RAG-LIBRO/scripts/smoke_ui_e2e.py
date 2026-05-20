#!/usr/bin/env python3
"""
Smoke E2E UI → API (fase 3e / tarea 3.8).

Replica el contrato que consume el frontend (lib/streamChat.ts):
  POST /chat/stream  →  event:sources  →  event:token*  →  event:done

Query por defecto: Q01 de EVAL.md / eval_cases.py.
Salida: exit 0 si pasa; exit 1 con mensaje claro si falla.

Uso (backend en :8000):
  cd RAG-LIBRO/backend && .venv\\Scripts\\python ..\\scripts\\smoke_ui_e2e.py
  python ..\\scripts\\smoke_ui_e2e.py --api http://127.0.0.1:8000 --query-id Q01
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Importar dataset sin arrancar FastAPI
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.eval_cases import EVAL_CASES  # noqa: E402


def _parse_sse(text: str) -> list[dict]:
    """Mismo criterio que tests/test_api.py (_parse_sse)."""
    events: list[dict] = []
    current: dict = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                events.append(current)
                current = {}
        elif stripped.startswith("event:"):
            current["event"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("data:"):
            raw = stripped.split(":", 1)[1].strip()
            try:
                current["data"] = json.loads(raw)
            except json.JSONDecodeError:
                current["data"] = raw
    if current:
        events.append(current)
    return events


def smoke_stream(api_base: str, message: str, timeout: int = 120) -> dict:
    url = f"{api_base.rstrip('/')}/chat/stream"
    body = json.dumps({"message": message}).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    pages: list[int] = []
    tokens: list[str] = []
    saw_done = False

    try:
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}")
            raw = resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {e.code}: {detail}") from e
    except URLError as e:
        raise RuntimeError(f"No se pudo conectar a {url}: {e}") from e

    events = _parse_sse(raw)
    if not events:
        raise RuntimeError("Respuesta SSE vacía")

    for ev in events:
        name = ev.get("event")
        data = ev.get("data")
        if name == "sources":
            if not isinstance(data, list):
                raise ValueError("sources: data debe ser lista")
            pages = [int(p) for p in data]
        elif name == "token":
            if not isinstance(data, str):
                raise ValueError("token: data debe ser string")
            tokens.append(data)
        elif name == "done":
            saw_done = True

    answer = "".join(tokens)
    return {
        "pages": pages,
        "token_count": len(tokens),
        "answer_len": len(answer),
        "answer_preview": answer[:200],
        "saw_done": saw_done,
        "event_types": [e.get("event") for e in events],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke E2E fase 3e")
    parser.add_argument(
        "--api",
        default="http://127.0.0.1:8000",
        help="Base URL del backend (default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--query-id",
        default="Q01",
        choices=[c.id for c in EVAL_CASES],
        help="ID de query en EVAL.md (default: Q01)",
    )
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    case = next(c for c in EVAL_CASES if c.id == args.query_id)
    print(f"[smoke-3e] API={args.api} query={case.id}")
    print(f"  message: {case.query!r}")
    print(f"  expected_pages (eval A): {case.expected_pages}")

    # Health primero
    try:
        with urlopen(f"{args.api.rstrip('/')}/health", timeout=10) as h:
            health = json.loads(h.read().decode())
    except URLError as e:
        print(f"FAIL: /health no responde — {e}")
        return 1
    if not health.get("index_loaded"):
        print("FAIL: index_loaded=false — construí el índice Fase 1 primero.")
        return 1

    try:
        result = smoke_stream(args.api, case.query, timeout=args.timeout)
    except Exception as e:
        print(f"FAIL: stream — {e}")
        return 1

    ok = True
    if not result["pages"]:
        print("FAIL: evento sources sin páginas")
        ok = False
    if result["token_count"] < 1:
        print("FAIL: ningún evento token")
        ok = False
    if not result["saw_done"]:
        print("FAIL: stream sin evento done")
        ok = False
    if result["answer_len"] < 20:
        print(f"FAIL: respuesta demasiado corta ({result['answer_len']} chars)")
        ok = False

    if ok:
        print("PASS: sources -> tokens -> done")
        print(f"  pages={result['pages']}")
        print(f"  tokens={result['token_count']} chars={result['answer_len']}")
        print(f"  preview: {result['answer_preview']!r}...")
        # Retrieval hint (no falla el smoke si el eval A falla)
        expected = set(case.expected_pages)
        hit = expected.intersection(result["pages"])
        if hit:
            print(f"  eval-hint: overlap páginas esperadas {sorted(hit)}")
        else:
            print(
                f"  eval-hint: ninguna página esperada en sources "
                f"(got {result['pages']}, want {case.expected_pages}) — revisar en Fase 5"
            )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
