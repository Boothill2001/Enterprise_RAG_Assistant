from __future__ import annotations

import time

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT,
)
from src.retrieval.hybrid import RetrievedChunk

SYSTEM_PROMPT = """You are an internal enterprise assistant. Answer questions ONLY using the provided context documents.

Rules:
1. Cite every factual claim with [1], [2], etc. matching the source index below.
2. If the context does not contain enough information to answer, say exactly: "I don't have enough information in the available documents to answer this question."
3. Never use knowledge outside the provided context.
4. Keep answers concise — under 300 words unless the user asks for detail.
5. If the question asks about data from a different department that you don't have access to, say: "You don't have permission to access this information. Please contact your administrator."
"""


def _format_context(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(f"[{i}] (source: {c.source}, section: {c.section})\n{c.text}")
    return "\n\n---\n\n".join(parts)


def generate_answer(
    query: str,
    chunks: list[RetrievedChunk],
) -> tuple[str, str, float]:
    """Generate an answer using LLM with citation prompt.

    Returns (answer, mode, generation_ms).
    mode is 'llm' or 'extractive'.
    """
    context = _format_context(chunks)

    if not DEEPSEEK_API_KEY:
        snippets = []
        for i, c in enumerate(chunks[:3], 1):
            snippet = c.text[:500]
            snippets.append(f"[{i}] ({c.source}): {snippet}")
        answer = "⚠️ LLM not configured. Showing top passages:\n\n" + "\n\n".join(snippets)
        return answer, "extractive", 0.0

    llm = ChatOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        model=DEEPSEEK_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        timeout=LLM_TIMEOUT,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}"),
    ]

    try:
        t0 = time.perf_counter()
        response = llm.invoke(messages)
        gen_ms = (time.perf_counter() - t0) * 1000
        return response.content, "llm", gen_ms
    except Exception:
        snippets = []
        for i, c in enumerate(chunks[:3], 1):
            snippet = c.text[:500]
            snippets.append(f"[{i}] ({c.source}): {snippet}")
        answer = "⚠️ LLM unavailable. Showing top passages:\n\n" + "\n\n".join(snippets)
        return answer, "extractive", 0.0
