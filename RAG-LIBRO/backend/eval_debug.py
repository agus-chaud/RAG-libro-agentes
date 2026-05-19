"""
Debug: muestra la respuesta real del LLM para las queries que fallan en B.
Uso: python eval_debug.py
"""
from __future__ import annotations
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.eval_cases import EVAL_CASES
from app.eval_checks import retrieval_passes, answer_passes
from app.rag import answer_with_sources, build_or_load_vectorstore, set_vectorstore
from app.ingest import ingest_pdf
from app.vectorstore import create_embeddings

FAIL_QUERIES = {"Q03", "Q04", "Q06", "Q07", "Q09", "Q10"}

def main():
    print("Cargando índice FAISS...")
    _, chunks = ingest_pdf()
    embeddings = create_embeddings()
    vs = build_or_load_vectorstore(chunks, embeddings=embeddings)
    set_vectorstore(vs)
    print("Índice listo\n")

    for case in EVAL_CASES:
        if case.id not in FAIL_QUERIES:
            continue

        result = answer_with_sources(case.query, k=4)
        pages = result["pages"]
        answer = result["answer"]
        ret_ok = retrieval_passes(pages, list(case.expected_pages))
        ans_ok = answer_passes(answer, list(case.key_concepts))

        print(f"{'='*70}")
        print(f"{case.id} | A={'PASS' if ret_ok else 'FAIL'} | B={'PASS' if ans_ok else 'FAIL'}")
        print(f"Query:    {case.query}")
        print(f"Expected pages: {case.expected_pages} | Got: {pages}")
        print(f"Key concepts:   {case.key_concepts}")

        # Para B failures, mostrar cuál concepto falta
        if not ans_ok:
            missing = [c for c in case.key_concepts if c.lower() not in answer.lower()]
            print(f"Conceptos FALTANTES en respuesta: {missing}")

        print(f"\nRespuesta LLM:\n{answer[:600]}")
        print()

if __name__ == "__main__":
    main()
