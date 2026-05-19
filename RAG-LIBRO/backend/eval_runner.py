"""
Fase 1-e — Eval runner standalone.

Construye (o carga) el índice FAISS, corre run_eval_suite con varios valores de k,
e imprime tabla A/B y resumen de tuning.

Uso:
    cd RAG-LIBRO/backend
    .venv\\Scripts\\Activate.ps1
    python eval_runner.py
    python eval_runner.py --k 6
    python eval_runner.py --k 4 6 8 --provider groq
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.ingest import ingest_pdf
from app.rag import answer_with_sources, build_or_load_vectorstore, set_vectorstore
from app.vectorstore import create_embeddings
from tests.test_eval import run_eval_suite


def build_index(verbose: bool = True) -> None:
    if verbose:
        print("Construyendo/cargando índice FAISS...")
    _, chunks = ingest_pdf()
    embeddings = create_embeddings()
    vs = build_or_load_vectorstore(chunks, embeddings=embeddings)
    set_vectorstore(vs)
    if verbose:
        print(f"  Índice listo — {vs.index.ntotal} vectores\n")


def make_runner(k: int, delay_s: float = 2.0):
    """Crea runner con delay entre queries para evitar rate-limit de Groq (free tier ~10 rpm)."""
    call_count = [0]

    def run(query: str, **_kw) -> tuple[str, list[int]]:
        if call_count[0] > 0:
            time.sleep(delay_s)
        call_count[0] += 1
        result = answer_with_sources(query, k=k)
        return result["answer"], result["pages"]

    return run


def _pass_symbol(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _set_utf8_stdout() -> None:
    """Fuerza UTF-8 en stdout (Windows cp1252 no soporta simbolos unicode)."""
    import sys, io
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


def print_table(results: list[dict], k: int) -> None:
    header = f"{'ID':<5} {'A-Ret':<7} {'B-Gen':<7} {'Global':<8}  Retrieved pages"
    sep = "-" * 65
    print(f"\n=== Eval k={k} ===")
    print(header)
    print(sep)
    for r in results:
        a = _pass_symbol(r["retrieval_ok"])
        b = _pass_symbol(r["answer_ok"])
        g = _pass_symbol(r["passed"])
        pages = str(r["retrieved_pages"])
        print(f"{r['id']:<5} {a:<7} {b:<7} {g:<8}  {pages}")
    print(sep)


def run_with_k(k: int) -> dict:
    runner = make_runner(k)
    report = run_eval_suite(runner, k=k)
    print_table(report["results"], k)
    rate_pct = report["pass_rate"] * 100
    status = "[OK] BASELINE ALCANZADO" if report["meets_baseline"] else "[--] bajo baseline"
    print(f"PASS rate: {report['passed']}/{report['total']} ({rate_pct:.0f}%)  [{status}]")
    return report


def diagnose(report: dict, k: int) -> None:
    results = report["results"]
    only_a_fail = [r for r in results if not r["retrieval_ok"] and r["answer_ok"]]
    only_b_fail = [r for r in results if r["retrieval_ok"] and not r["answer_ok"]]
    both_fail = [r for r in results if not r["retrieval_ok"] and not r["answer_ok"]]
    passed = [r for r in results if r["passed"]]

    print(f"\n--- Diagnóstico k={k} ---")
    print(f"  PASS total:        {len(passed)}/10")
    print(f"  FAIL solo A (ret): {[r['id'] for r in only_a_fail]}")
    print(f"  FAIL solo B (gen): {[r['id'] for r in only_b_fail]}")
    print(f"  FAIL ambos A+B:    {[r['id'] for r in both_fail]}")

    if only_a_fail or both_fail:
        print("\n  → Acción recomendada: tuning de RETRIEVAL (k, chunk_size, overlap)")
    if only_b_fail:
        print("  → Acción recomendada: tuning de GENERACIÓN (prompt, temperature, modelo)")


def main() -> None:
    _set_utf8_stdout()
    parser = argparse.ArgumentParser(description="Eval RAG — Fase 1-e")
    parser.add_argument("--k", nargs="+", type=int, default=[4], help="Valores de k a evaluar")
    parser.add_argument("--rebuild", action="store_true", help="Forzar reconstrucción del índice")
    args = parser.parse_args()

    build_index()

    best_report = None
    best_k = args.k[0]

    for k in args.k:
        report = run_with_k(k)
        diagnose(report, k)
        if best_report is None or report["pass_rate"] > best_report["pass_rate"]:
            best_report = report
            best_k = k

    if len(args.k) > 1:
        print(f"\n=== Mejor k={best_k} ({best_report['pass_rate']*100:.0f}% PASS) ===")


if __name__ == "__main__":
    main()
