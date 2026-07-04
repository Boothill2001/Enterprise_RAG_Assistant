from __future__ import annotations

import re
from dataclasses import dataclass


CITATION_RE = re.compile(r"\[(\d+)\]")


@dataclass
class CitationReport:
    total_citations: int
    valid_citations: int
    invalid_citations: list[int]
    citation_accuracy: float
    has_refusal: bool


def audit_citations(answer: str, num_context_chunks: int) -> CitationReport:
    """Verify that all [N] citations in the answer map to actual context chunks."""
    cited = [int(m) for m in CITATION_RE.findall(answer)]
    if not cited:
        has_refusal = _is_refusal(answer)
        return CitationReport(
            total_citations=0,
            valid_citations=0,
            invalid_citations=[],
            citation_accuracy=1.0 if has_refusal else 0.0,
            has_refusal=has_refusal,
        )

    unique_cited = list(set(cited))
    valid = [c for c in unique_cited if 1 <= c <= num_context_chunks]
    invalid = [c for c in unique_cited if c not in valid]

    accuracy = len(valid) / len(unique_cited) if unique_cited else 0.0

    return CitationReport(
        total_citations=len(unique_cited),
        valid_citations=len(valid),
        invalid_citations=invalid,
        citation_accuracy=accuracy,
        has_refusal=_is_refusal(answer),
    )


def _is_refusal(answer: str) -> bool:
    refusal_phrases = [
        "don't have enough information",
        "don't have permission",
        "no relevant documents",
        "cannot answer",
        "not available in",
    ]
    lower = answer.lower()
    return any(phrase in lower for phrase in refusal_phrases)
