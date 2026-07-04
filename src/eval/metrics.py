from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalResult:
    question: str
    expected_answer: str
    actual_answer: str
    intent: str
    required_role: str
    predicted_intent: str
    hit: bool
    citation_accuracy: float
    is_refusal: bool
    passed: bool
    failure_reason: str = ""


@dataclass
class EvalSummary:
    total: int
    passed: int
    failed: int
    pass_rate: float
    hit_rate: float
    avg_citation_accuracy: float
    refusal_accuracy: float
    rbac_leak_rate: float
    tool_routing_accuracy: float
    results: list[EvalResult]
