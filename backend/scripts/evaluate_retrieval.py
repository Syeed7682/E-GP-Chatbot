"""Evaluate retrieval against a small curated set without provider calls by default."""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service
from app.services.qa_service import qa_service
from app.services.retrieval_service import RetrievalService


class KeywordOnlyEmbedding:
    semantic_search_available = False


def matches_expected(source: Dict[str, Any], case: Dict[str, Any]) -> bool:
    src_type = source.get("source_type", "manual")
    expected_type = case["source_type"]
    if src_type in ("manual", "pdf") and expected_type in ("manual", "pdf"):
        pass
    elif src_type != expected_type:
        return False
    if expected_type == "qa":
        return source.get("question_number") in case.get("question_numbers", [])
    return source.get("page") in case.get("pages", [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-file",
        type=Path,
        default=BACKEND_DIR / "data" / "retrieval_eval.json",
        help="JSON file containing curated questions and expected sources",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Use the configured embedding provider; this may make external API calls",
    )
    parser.add_argument(
        "--rag-version",
        type=str,
        default=None,
        help="Evaluate the upgraded EGP_RAG_Service against a specific index version (e.g. v001, v002)",
    )
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be at least 1")

    cases = json.loads(args.eval_file.read_text(encoding="utf-8"))
    if not cases:
        raise ValueError(f"No evaluation cases found in {args.eval_file}")

    if args.rag_version:
        from app.services.rag_service import load_rag_service
        from app.indexing.index_manager import IndexManager
        from app.config import INDEX_DIR

        mgr = IndexManager(INDEX_DIR)
        v_dir = mgr.get_version_dir(args.rag_version)
        rag = load_rag_service(index_dir=INDEX_DIR)
        if not rag:
            raise RuntimeError(f"Could not load RAG service for version {args.rag_version}")

        print(f"\n--- Evaluating Upgraded EGP_RAG_Service (Version: {args.rag_version}) ---")
        hits = 0
        reciuserl_rank_sum = 0.0
        for case in cases:
            _, sources, _ = rag.retrieve(case["question"], top_k=args.top_k)
            rank = next(
                (
                    index
                    for index, source in enumerate(sources, start=1)
                    if matches_expected(source, case)
                ),
                None,
            )
            if rank is not None:
                hits += 1
                reciuserl_rank_sum += 1.0 / rank
            observed = [
                f"{source.get('source_type', 'manual')}:"
                f"{source.get('question_number') if source.get('source_type') == 'qa' else source.get('page')}"
                for source in sources
            ]
            print(
                f"{case['id']}: {'HIT' if rank is not None else 'MISS'}"
                f"{f' rank={rank}' if rank is not None else ''}; retrieved={observed}"
            )

        count = len(cases)
        print(
            f"mode=RAG_Service version={args.rag_version} "
            f"top_k={args.top_k} cases={count} "
            f"hit_rate@{args.top_k}={hits / count:.3f} "
            f"mrr@{args.top_k}={reciuserl_rank_sum / count:.3f}\n"
        )
        return 0 if hits == count else 1
    if not faiss_service.load():
        raise RuntimeError("Could not load the current FAISS index and metadata")
    index = faiss_service.index
    if index is None:
        raise RuntimeError("FAISS index loader returned success without an index")
    if index.ntotal != len(faiss_service.metadata):
        raise RuntimeError(
            "FAISS vector count does not match metadata count: "
            f"{index.ntotal} != {len(faiss_service.metadata)}"
        )

    embedding = embedding_service if args.semantic else KeywordOnlyEmbedding()
    retrieval = RetrievalService(
        emb_service=embedding,
        f_service=faiss_service,
        q_service=qa_service,
    )

    hits = 0
    reciuserl_rank_sum = 0.0
    for case in cases:
        _, sources = retrieval.retrieve(case["question"], top_k=args.top_k)
        rank = next(
            (
                index
                for index, source in enumerate(sources, start=1)
                if matches_expected(source, case)
            ),
            None,
        )
        if rank is not None:
            hits += 1
            reciuserl_rank_sum += 1.0 / rank
        observed = [
            f"{source.get('source_type', 'manual')}:"
            f"{source.get('question_number') if source.get('source_type') == 'qa' else source.get('page')}"
            for source in sources
        ]
        print(
            f"{case['id']}: {'HIT' if rank is not None else 'MISS'}"
            f"{f' rank={rank}' if rank is not None else ''}; retrieved={observed}"
        )

    count = len(cases)
    print(
        f"mode={'semantic' if args.semantic else 'keyword-only'} "
        f"top_k={args.top_k} cases={count} "
        f"hit_rate@{args.top_k}={hits / count:.3f} "
        f"mrr@{args.top_k}={reciuserl_rank_sum / count:.3f}"
    )
    return 0 if hits == count else 1


if __name__ == "__main__":
    raise SystemExit(main())
