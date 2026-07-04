from __future__ import annotations

import re

CALC_PATTERNS = [
    re.compile(r"\b(tính|calculate|compute)\b", re.IGNORECASE),
    re.compile(r"\b(bao nhiêu|how much)\b.*\d", re.IGNORECASE),
    re.compile(r"\d+\s*[\+\-\*\/\%\^]\s*\d+"),
    re.compile(r"\b\d+\s*%\s*(of|trên|của)\b", re.IGNORECASE),
]

SQL_PATTERNS = [
    re.compile(r"\b(total revenue|tổng doanh thu|total salary|tổng lương)\b", re.IGNORECASE),
    re.compile(r"\b(how many employees|bao nhiêu nhân viên|số nhân viên)\b", re.IGNORECASE),
    re.compile(r"\b(average salary|lương trung bình|lương tb)\b", re.IGNORECASE),
    re.compile(r"\b(highest paid|lowest paid|lương cao nhất|lương thấp nhất)\b", re.IGNORECASE),
    re.compile(r"\b(revenue|doanh thu)\b.*\b(Q[1-4]|quarter|quý)\b", re.IGNORECASE),
    re.compile(r"\b(Q[1-4]|quarter|quý)\b.*\b(revenue|doanh thu)\b", re.IGNORECASE),
    re.compile(r"\b(list|danh sách)\b.*\b(employees|nhân viên)\b", re.IGNORECASE),
    re.compile(r"\b(sum|count|avg|average|tổng|đếm)\b.*\b(revenue|salary|doanh thu|lương)\b", re.IGNORECASE),
]


def classify_intent(query: str) -> str:
    """Classify query intent: 'calculator', 'sql', or 'rag'.

    Uses keyword + regex matching. Default fallback is 'rag' (safe).
    """
    for pattern in CALC_PATTERNS:
        if pattern.search(query):
            if any(p.search(query) for p in SQL_PATTERNS):
                return "sql"
            return "calculator"

    for pattern in SQL_PATTERNS:
        if pattern.search(query):
            return "sql"

    return "rag"
