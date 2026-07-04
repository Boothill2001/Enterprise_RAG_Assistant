from __future__ import annotations

import pickle
import re
import time
from dataclasses import dataclass

from qdrant_client.models import FieldCondition, Filter, MatchAny

from config import (
    COLLECTION_NAME,
    CANDIDATES_PER_RETRIEVER,
    RRF_K,
    BM25_PICKLE,
)
from src.ingestion.embeddings import embed_query
from src.ingestion.indexer import get_qdrant_client

TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    source: str
    section: str
    department: str
    score: float
    retrievers: list[str]


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _dense_search(query: str, allowed_roles: list[str], top_k: int) -> list[tuple[dict, float]]:
    client = get_qdrant_client()
    vector = embed_query(query).tolist()

    role_filter = Filter(
        must=[FieldCondition(key="access_roles", match=MatchAny(any=allowed_roles))]
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        query_filter=role_filter,
        limit=top_k,
    )

    return [(hit.payload, hit.score) for hit in results.points]


def _sparse_search(query: str, allowed_roles: list[str], top_k: int) -> list[tuple[dict, float]]:
    with open(BM25_PICKLE, "rb") as f:
        data = pickle.load(f)

    bm25 = data["bm25"]
    chunks = data["chunks"]

    tokens = _tokenize(query)
    scores = bm25.get_scores(tokens)

    scored = []
    for i, score in enumerate(scores):
        chunk = chunks[i]
        if any(role in allowed_roles for role in chunk["access_roles"]):
            scored.append((chunk, float(score)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def _rrf_fuse(
    dense_results: list[tuple[dict, float]],
    sparse_results: list[tuple[dict, float]],
    k: int = RRF_K,
) -> list[RetrievedChunk]:
    scores: dict[str, float] = {}
    chunk_map: dict[str, dict] = {}
    retriever_map: dict[str, list[str]] = {}

    for rank, (chunk, _) in enumerate(dense_results):
        cid = chunk["chunk_id"]
        scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)
        chunk_map[cid] = chunk
        retriever_map.setdefault(cid, []).append("dense")

    for rank, (chunk, _) in enumerate(sparse_results):
        cid = chunk["chunk_id"]
        scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)
        chunk_map[cid] = chunk
        retriever_map.setdefault(cid, []).append("bm25")

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)

    results = []
    for cid in sorted_ids:
        c = chunk_map[cid]
        results.append(RetrievedChunk(
            chunk_id=cid,
            text=c["text"],
            source=c["source"],
            section=c["section"],
            department=c["department"],
            score=scores[cid],
            retrievers=retriever_map[cid],
        ))

    return results


def hybrid_retrieve(
    query: str,
    allowed_roles: list[str],
    top_k: int = CANDIDATES_PER_RETRIEVER,
    use_hybrid: bool = True,
) -> tuple[list[RetrievedChunk], dict[str, float]]:
    """Retrieve chunks using hybrid (dense + BM25 + RRF) or dense-only."""
    timings: dict[str, float] = {}

    t0 = time.perf_counter()
    dense_results = _dense_search(query, allowed_roles, top_k)
    timings["dense_ms"] = (time.perf_counter() - t0) * 1000

    if use_hybrid:
        t0 = time.perf_counter()
        sparse_results = _sparse_search(query, allowed_roles, top_k)
        timings["bm25_ms"] = (time.perf_counter() - t0) * 1000

        fused = _rrf_fuse(dense_results, sparse_results)
    else:
        fused = [
            RetrievedChunk(
                chunk_id=c["chunk_id"],
                text=c["text"],
                source=c["source"],
                section=c["section"],
                department=c["department"],
                score=score,
                retrievers=["dense"],
            )
            for c, score in dense_results
        ]

    return fused, timings
