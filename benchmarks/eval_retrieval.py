"""Retrieval quality evaluation for the hybrid search engine.

Indexes the fixed corpus in benchmarks/eval/corpus into a temporary vault, runs
every query in benchmarks/eval/queries.json, and reports:

  hit@1 / hit@3  share of answerable queries whose expected note is in the top 1 / 3
  MRR            mean reciprocal rank of the expected note (0 when absent from top 5)
  abstain        share of unanswerable queries that correctly return no result

Usage:
    python benchmarks/eval_retrieval.py
    python benchmarks/eval_retrieval.py --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    python benchmarks/eval_retrieval.py --json results.json
"""

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "src"))

from devbrain.core.constants import DEFAULT_EMBEDDING_MODEL  # noqa: E402
from devbrain.engine.hybrid_search import HybridEngine  # noqa: E402

CORPUS_DIR = ROOT / "eval" / "corpus"
QUERIES_FILE = ROOT / "eval" / "queries.json"
MODES = ("hybrid", "dense", "bm25")
TOP_K = 5


def evaluate(engine: HybridEngine, queries: list[dict], mode: str) -> dict:
    """Score one search mode, broken down by query language."""
    groups: dict[str, dict] = {}
    for q in queries:
        bucket = groups.setdefault(
            q["lang"], {"n": 0, "hit1": 0, "hit3": 0, "rr": 0.0, "neg": 0, "abstain": 0}
        )
        results = engine.search(q["query"], limit=TOP_K, mode=mode)
        ranked_docs = list(dict.fromkeys(r.doc_id for r in results))

        if not q["expected"]:
            bucket["neg"] += 1
            bucket["abstain"] += 0 if results else 1
            continue

        bucket["n"] += 1
        rank = next((i for i, d in enumerate(ranked_docs, 1) if d in q["expected"]), None)
        if rank:
            bucket["hit1"] += rank == 1
            bucket["hit3"] += rank <= 3
            bucket["rr"] += 1.0 / rank

    total = {k: sum(g[k] for g in groups.values()) for k in ("n", "hit1", "hit3", "rr", "neg", "abstain")}
    groups["all"] = total

    return {
        lang: {
            "queries": g["n"],
            "hit@1": round(g["hit1"] / g["n"], 3) if g["n"] else None,
            "hit@3": round(g["hit3"] / g["n"], 3) if g["n"] else None,
            "mrr": round(g["rr"] / g["n"], 3) if g["n"] else None,
            "negatives": g["neg"],
            "abstain": round(g["abstain"] / g["neg"], 3) if g["neg"] else None,
        }
        for lang, g in groups.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default=DEFAULT_EMBEDDING_MODEL, help="FastEmbed model name")
    parser.add_argument("--json", dest="json_out", help="Write full results to this JSON file")
    args = parser.parse_args()

    queries = json.loads(QUERIES_FILE.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="devbrain-eval-") as tmp:
        vault = Path(tmp) / "vault"
        shutil.copytree(CORPUS_DIR, vault)
        engine = HybridEngine(vault_path=vault, embedding_model=args.model)
        stats = engine.index_vault(force_reindex=True)
        report = {mode: evaluate(engine, queries, mode) for mode in MODES}

    print(f"model: {args.model}")
    print(f"corpus: {stats['processed']} notes, {stats['total_chunks']} chunks, {len(queries)} queries\n")
    header = f"{'mode':<8}{'lang':<6}{'n':>4}{'hit@1':>8}{'hit@3':>8}{'mrr':>8}{'abstain':>9}"
    print(header)
    print("-" * len(header))
    for mode in MODES:
        for lang in ("id", "en", "all"):
            m = report[mode].get(lang)
            if not m:
                continue
            fmt = lambda v: f"{v:.3f}" if v is not None else "-"  # noqa: E731
            print(
                f"{mode:<8}{lang:<6}{m['queries']:>4}{fmt(m['hit@1']):>8}{fmt(m['hit@3']):>8}"
                f"{fmt(m['mrr']):>8}{fmt(m['abstain']):>9}"
            )
        print()

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({"model": args.model, "report": report}, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
