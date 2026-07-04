"""Enterprise RAG Assistant — Streamlit UI"""

import json
import streamlit as st

from src.auth.rbac import ROLES, get_allowed_departments, get_all_departments
from src.tools.router import classify_intent
from src.tools.calculator import safe_calculate
from src.tools.sql_executor import execute_sql_query
from src.retrieval.hybrid import hybrid_retrieve
from src.retrieval.reranker import rerank
from src.retrieval.gate import check_retrieval_gate
from src.generation.llm import generate_answer
from src.generation.citation_audit import audit_citations


st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="🏢",
    layout="wide",
)

HEADER_CSS = """
<style>
.main-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #1a4a6e 100%);
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
}
.main-header h1 {
    color: white;
    font-size: 28px;
    margin: 0 0 4px 0;
}
.main-header p {
    color: #b8d4e8;
    font-size: 14px;
    margin: 0;
}
.role-badge {
    display: inline-block;
    background: #2d5a87;
    color: white;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    margin: 2px;
}
.gate-blocked {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
}
.tool-indicator {
    background: #e8f4f8;
    border-left: 4px solid #17a2b8;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin: 8px 0;
}
.citation-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
}
.citation-good { background: #d4edda; color: #155724; }
.citation-warn { background: #fff3cd; color: #856404; }
.citation-bad { background: #f8d7da; color: #721c24; }
</style>
"""


def _render_header():
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Enterprise AI Assistant</h1>
        <p>RAG + RBAC + Tool Calling + Citation Audit — Internal Document Q&A</p>
    </div>
    """, unsafe_allow_html=True)


def _render_sidebar():
    with st.sidebar:
        st.header("🔐 Access Control")
        role = st.selectbox(
            "Select your role:",
            options=list(ROLES.keys()),
            format_func=lambda r: ROLES[r],
            key="role_select",
        )

        if "current_role" not in st.session_state or st.session_state.current_role != role:
            st.session_state.current_role = role
            st.session_state.messages = []

        allowed = get_allowed_departments(role)
        all_depts = get_all_departments()

        st.markdown("**Document access:**")
        for dept in all_depts:
            icon = "✅" if dept in allowed else "❌"
            st.markdown(f"{icon} {dept.capitalize()}")

        st.divider()
        st.header("⚙️ Pipeline Settings")
        use_hybrid = st.toggle("Hybrid search (dense + BM25)", value=True)
        use_reranker = st.toggle("Cross-encoder reranking", value=True)
        use_gate = st.toggle("Retrieval gate", value=True)

        st.divider()
        if st.button("🗑️ Clear chat"):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.caption("Built by Nguyen Minh Tri")
        st.caption("Senior AI Engineer")

    return role, allowed, use_hybrid, use_reranker, use_gate


def _process_query(query, role, allowed, use_hybrid, use_reranker, use_gate):
    """Process a query through the full pipeline."""
    result = {
        "answer": "",
        "intent": "",
        "sources": [],
        "timings": {},
        "tool_info": None,
        "citation_report": None,
        "gate_blocked": False,
        "gate_score": 0.0,
    }

    intent = classify_intent(query)
    result["intent"] = intent

    allowed_roles = [role]

    if intent == "calculator":
        import re
        nums = re.findall(r"[\d\.\+\-\*\/\(\)\%\s]+", query)
        expr = max(nums, key=len).strip() if nums else ""
        if expr:
            calc_result = safe_calculate(expr)
            result["answer"] = f"**Calculator result:** {calc_result}\n\n*Expression: `{expr}`*"
            result["tool_info"] = {"tool": "calculator", "expression": expr, "result": calc_result}
        else:
            result["answer"] = "I couldn't extract a mathematical expression from your question. Please provide a clearer expression."
        return result

    elif intent == "sql":
        try:
            answer, sql, sql_ms = execute_sql_query(query)
            result["answer"] = answer
            result["timings"]["sql_ms"] = sql_ms
            result["tool_info"] = {"tool": "sql", "query": sql}
        except Exception as e:
            result["answer"] = f"Database query failed: {e}"
        return result

    candidates, timings = hybrid_retrieve(query, allowed_roles, use_hybrid=use_hybrid)
    result["timings"].update(timings)

    reranked, rerank_ms = rerank(query, candidates, use_reranker=use_reranker)
    result["timings"]["rerank_ms"] = rerank_ms

    if use_gate:
        gate_passed, max_score = check_retrieval_gate(reranked)
        result["gate_score"] = max_score
        if not gate_passed:
            result["gate_blocked"] = True
            result["answer"] = "I don't have enough information in the available documents to answer this question."
            return result

    answer, mode, gen_ms = generate_answer(query, reranked)
    result["answer"] = answer
    result["timings"]["generation_ms"] = gen_ms

    audit = audit_citations(answer, len(reranked))
    result["citation_report"] = {
        "total": audit.total_citations,
        "valid": audit.valid_citations,
        "accuracy": audit.citation_accuracy,
        "invalid": audit.invalid_citations,
    }

    result["sources"] = [
        {
            "index": i + 1,
            "source": c.source,
            "section": c.section,
            "score": round(c.score, 4),
            "retrievers": c.retrievers,
            "text_preview": c.text[:200] + "..." if len(c.text) > 200 else c.text,
        }
        for i, c in enumerate(reranked)
    ]

    return result


def _render_chat_tab(role, allowed, use_hybrid, use_reranker, use_gate):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)
            if "result" in msg and msg["result"]:
                _render_result_details(msg["result"])

    if query := st.chat_input("Ask a question about internal documents..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                result = _process_query(query, role, allowed, use_hybrid, use_reranker, use_gate)

            st.markdown(result["answer"], unsafe_allow_html=True)
            _render_result_details(result)

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "result": result,
        })


def _render_result_details(result):
    if result.get("tool_info"):
        tool = result["tool_info"]
        if tool["tool"] == "calculator":
            st.markdown(f"""<div class="tool-indicator">
                🧮 <strong>Tool: Calculator</strong> — <code>{tool['expression']}</code> = {tool['result']}
            </div>""", unsafe_allow_html=True)
        elif tool["tool"] == "sql":
            st.markdown(f"""<div class="tool-indicator">
                🗄️ <strong>Tool: SQL Query</strong>
            </div>""", unsafe_allow_html=True)
            with st.expander("View SQL query"):
                st.code(tool["query"], language="sql")

    if result.get("gate_blocked"):
        st.markdown(f"""<div class="gate-blocked">
            🚫 <strong>Retrieval Gate Blocked</strong> — Max score: {result['gate_score']:.4f} (threshold: 0.35).
            LLM was not called to prevent hallucination.
        </div>""", unsafe_allow_html=True)

    if result.get("citation_report"):
        cr = result["citation_report"]
        if cr["accuracy"] >= 0.9:
            badge_class = "citation-good"
        elif cr["accuracy"] >= 0.5:
            badge_class = "citation-warn"
        else:
            badge_class = "citation-bad"

        st.markdown(
            f'<span class="citation-badge {badge_class}">📝 Citations: {cr["valid"]}/{cr["total"]} valid ({cr["accuracy"]:.0%})</span>',
            unsafe_allow_html=True,
        )

    if result.get("sources"):
        with st.expander(f"📚 Sources ({len(result['sources'])}) & Latency"):
            for src in result["sources"]:
                retrievers = ", ".join(src["retrievers"])
                st.markdown(
                    f"**[{src['index']}]** `{src['source']}` — *{src['section']}* "
                    f"(score: {src['score']}, found by: {retrievers})"
                )
                st.caption(src["text_preview"])
                st.divider()

            if result.get("timings"):
                st.markdown("**⏱️ Latency breakdown:**")
                for stage, ms in result["timings"].items():
                    st.markdown(f"- {stage}: {ms:.0f}ms")
                total = sum(result["timings"].values())
                st.markdown(f"- **Total: {total:.0f}ms**")


def _render_eval_tab():
    st.subheader("📊 Evaluation Dashboard")
    st.info("Run `python run_eval.py` to generate evaluation results, then view them here.")

    eval_report_path = "data/eval/eval_report.json"
    try:
        with open(eval_report_path) as f:
            report = json.load(f)
    except FileNotFoundError:
        st.warning("No evaluation report found. Run `python run_eval.py --save` first.")

        if st.button("▶️ Run evaluation now"):
            with st.spinner("Running evaluation (this may take a few minutes)..."):
                from src.eval.harness import run_evaluation
                summary = run_evaluation()

                report_data = {
                    "total": summary.total,
                    "passed": summary.passed,
                    "failed": summary.failed,
                    "pass_rate": summary.pass_rate,
                    "hit_rate": summary.hit_rate,
                    "avg_citation_accuracy": summary.avg_citation_accuracy,
                    "refusal_accuracy": summary.refusal_accuracy,
                    "rbac_leak_rate": summary.rbac_leak_rate,
                    "tool_routing_accuracy": summary.tool_routing_accuracy,
                    "results": [
                        {
                            "question": r.question,
                            "expected": r.expected_answer,
                            "actual": r.actual_answer[:300],
                            "intent": r.intent,
                            "predicted_intent": r.predicted_intent,
                            "role": r.required_role,
                            "passed": r.passed,
                            "hit": r.hit,
                            "citation_accuracy": r.citation_accuracy,
                            "failure_reason": r.failure_reason,
                        }
                        for r in summary.results
                    ],
                }
                with open(eval_report_path, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                st.rerun()
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pass Rate", f"{report['pass_rate']:.1%}", delta=None)
    col2.metric("Hit Rate @5", f"{report['hit_rate']:.1%}")
    col3.metric("RBAC Leak Rate", f"{report['rbac_leak_rate']:.1%}",
                delta="SAFE" if report['rbac_leak_rate'] == 0 else "LEAK!",
                delta_color="normal" if report['rbac_leak_rate'] == 0 else "inverse")
    col4.metric("Tool Routing", f"{report['tool_routing_accuracy']:.1%}")

    col5, col6 = st.columns(2)
    col5.metric("Citation Accuracy", f"{report['avg_citation_accuracy']:.1%}")
    col6.metric("Refusal Accuracy", f"{report['refusal_accuracy']:.1%}")

    st.divider()

    filter_intent = st.selectbox(
        "Filter by intent:",
        ["All", "rag", "sql", "calculator", "out_of_scope", "rbac_test"],
    )

    results = report["results"]
    if filter_intent != "All":
        results = [r for r in results if r["intent"] == filter_intent]

    for r in results:
        icon = "✅" if r["passed"] else "❌"
        with st.expander(f"{icon} {r['question'][:80]}... [{r['intent']}]"):
            st.markdown(f"**Role:** {r['role']}")
            st.markdown(f"**Intent:** {r['intent']} → Predicted: {r['predicted_intent']}")
            st.markdown(f"**Expected:** {r['expected']}")
            st.markdown(f"**Actual:** {r['actual'][:500]}")
            if not r["passed"]:
                st.error(f"Failure: {r['failure_reason']}")


def main():
    _render_header()
    role, allowed, use_hybrid, use_reranker, use_gate = _render_sidebar()

    tab_chat, tab_eval = st.tabs(["💬 Chat", "📊 Evaluation"])

    with tab_chat:
        _render_chat_tab(role, allowed, use_hybrid, use_reranker, use_gate)

    with tab_eval:
        _render_eval_tab()


if __name__ == "__main__":
    main()
