from __future__ import annotations

import time
from functools import lru_cache

from sentence_transformers import CrossEncoder

from config import RERANKER_MODEL, RERANK_TOP_N, FINAL_TOP_K
from src.retrieval.hybrid import RetrievedChunk


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    return CrossEncoder(RERANKER_MODEL)


def rerank(
    query: str,
    candidates: list[RetrievedChunk],
    top_n: int = RERANK_TOP_N,
    final_k: int = FINAL_TOP_K,
    use_reranker: bool = True,
) -> tuple[list[RetrievedChunk], float]:
    """Rerank candidates with cross-encoder. Returns (top_k results, time_ms)."""
    if not use_reranker:
        return candidates[:final_k], 0.0

    to_rerank = candidates[:top_n]
    pairs = [(query, c.text) for c in to_rerank]

    t0 = time.perf_counter()
    reranker = _get_reranker()
    scores = reranker.predict(pairs)
    rerank_ms = (time.perf_counter() - t0) * 1000

    for chunk, score in zip(to_rerank, scores):
        chunk.score = float(score)

    to_rerank.sort(key=lambda c: c.score, reverse=True)
    return to_rerank[:final_k], rerank_ms
