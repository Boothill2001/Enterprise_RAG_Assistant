from __future__ import annotations

import json

from config import EVAL_FILE
from src.auth.rbac import get_allowed_departments
from src.tools.router import classify_intent
from src.tools.calculator import safe_calculate
from src.tools.sql_executor import execute_sql_query
from src.retrieval.hybrid import hybrid_retrieve
from src.retrieval.reranker import rerank
from src.retrieval.gate import check_retrieval_gate
from src.generation.llm import generate_answer
from src.generation.citation_audit import audit_citations, _is_refusal
from src.eval.metrics import EvalResult, EvalSummary


def _run_single(qa: dict) -> EvalResult:
    question = qa["question"]
    expected = qa["expected_answer"]
    required_role = qa["required_role"]
    intent = qa["intent"]

    allowed_depts = get_allowed_departments(required_role)
    allowed_roles = [required_role]

    predicted_intent = classify_intent(question)
    actual_answer = ""
    hit = False
    citation_acc = 0.0
    is_refusal = False
    passed = False
    failure_reason = ""

    try:
        if predicted_intent == "calculator":
            nums = [c for c in question if c.isdigit() or c in "+-*/().% "]
            expr = "".join(nums).strip()
            if not expr:
                actual_answer = "Could not extract expression"
            else:
                actual_answer = f"Calculator result: {safe_calculate(expr)}"
            hit = True
            citation_acc = 1.0

        elif predicted_intent == "sql":
            answer, sql, _ = execute_sql_query(question)
            actual_answer = answer
            hit = True
            citation_acc = 1.0

        else:
            candidates, _ = hybrid_retrieve(question, allowed_roles)
            reranked, _ = rerank(question, candidates)
            gate_passed, max_score = check_retrieval_gate(reranked)

            if not gate_passed:
                actual_answer = "I don't have enough information in the available documents to answer this question."
                is_refusal = True
            else:
                actual_answer, mode, _ = generate_answer(question, reranked)
                audit = audit_citations(actual_answer, len(reranked))
                citation_acc = audit.citation_accuracy
                is_refusal = audit.has_refusal

            if qa.get("ground_truth_sources"):
                gt_sources = qa["ground_truth_sources"]
                hit = any(
                    any(gt in c.source for gt in gt_sources)
                    for c in reranked
                )
            else:
                hit = True

        if intent == "rbac_test":
            passed = _is_refusal(actual_answer)
            if not passed:
                failure_reason = "RBAC leak: answered a question the role should not access"
        elif intent == "out_of_scope":
            passed = _is_refusal(actual_answer)
            if not passed:
                failure_reason = "Should have refused out-of-scope question"
        elif intent == "calculator":
            passed = predicted_intent == "calculator"
            if not passed:
                failure_reason = f"Routed to '{predicted_intent}' instead of 'calculator'"
        elif intent == "sql":
            passed = predicted_intent == "sql"
            if not passed:
                failure_reason = f"Routed to '{predicted_intent}' instead of 'sql'"
        else:
            passed = hit and not is_refusal
            if not passed:
                failure_reason = "Missed ground-truth chunks" if not hit else "Unexpected refusal"

    except Exception as e:
        actual_answer = f"ERROR: {e}"
        failure_reason = str(e)

    return EvalResult(
        question=question,
        expected_answer=expected,
        actual_answer=actual_answer,
        intent=intent,
        required_role=required_role,
        predicted_intent=predicted_intent,
        hit=hit,
        citation_accuracy=citation_acc,
        is_refusal=is_refusal,
        passed=passed,
        failure_reason=failure_reason,
    )


def run_evaluation() -> EvalSummary:
    with open(EVAL_FILE, encoding="utf-8") as f:
        qa_pairs = json.load(f)

    results = [_run_single(qa) for qa in qa_pairs]

    total = len(results)
    passed = sum(1 for r in results if r.passed)

    rag_results = [r for r in results if r.intent == "rag"]
    hit_rate = sum(1 for r in rag_results if r.hit) / len(rag_results) if rag_results else 0.0

    cited = [r for r in rag_results if not r.is_refusal]
    avg_citation = sum(r.citation_accuracy for r in cited) / len(cited) if cited else 0.0

    oos = [r for r in results if r.intent == "out_of_scope"]
    refusal_acc = sum(1 for r in oos if r.is_refusal) / len(oos) if oos else 0.0

    rbac = [r for r in results if r.intent == "rbac_test"]
    rbac_leaks = sum(1 for r in rbac if not r.passed)
    rbac_leak_rate = rbac_leaks / len(rbac) if rbac else 0.0

    tool_qs = [r for r in results if r.intent in ("calculator", "sql")]
    tool_acc = sum(1 for r in tool_qs if r.predicted_intent == r.intent) / len(tool_qs) if tool_qs else 0.0

    return EvalSummary(
        total=total,
        passed=passed,
        failed=total - passed,
        pass_rate=passed / total if total else 0.0,
        hit_rate=hit_rate,
        avg_citation_accuracy=avg_citation,
        refusal_accuracy=refusal_acc,
        rbac_leak_rate=rbac_leak_rate,
        tool_routing_accuracy=tool_acc,
        results=results,
    )
