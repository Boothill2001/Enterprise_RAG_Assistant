from __future__ import annotations

from config import RETRIEVAL_GATE_THRESHOLD
from src.retrieval.hybrid import RetrievedChunk


def check_retrieval_gate(
    chunks: list[RetrievedChunk],
    threshold: float = RETRIEVAL_GATE_THRESHOLD,
) -> tuple[bool, float]:
    """Check if top retrieval score passes the gate threshold.

    Returns (passed, max_score).
    If passed is False, the query should be refused without calling the LLM.
    """
    if not chunks:
        return False, 0.0

    max_score = max(c.score for c in chunks)
    return max_score >= threshold, max_score
