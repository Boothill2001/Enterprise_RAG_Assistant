from __future__ import annotations

import re
import sqlite3
import time

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import (
    DB_FILE,
    SQL_QUERY_TIMEOUT,
    SQL_ROW_LIMIT,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
)

DANGEROUS_RE = re.compile(
    r"\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|TRUNCATE|REPLACE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

DB_SCHEMA = """
Tables:
1. revenue (quarter TEXT, department TEXT, amount REAL, currency TEXT)
   - quarter format: 'Q1-2025', 'Q2-2025', etc.
   - amount is in VND (e.g., 28000000000 = 28 billion VND)
   - departments: 'engineering', 'consulting', 'support'

2. employees (id INTEGER, name TEXT, department TEXT, role TEXT, salary REAL, start_date TEXT)
   - salary is monthly in VND
   - departments: 'engineering', 'hr', 'finance', 'legal'
   - start_date format: 'YYYY-MM-DD'
"""

SQL_SYSTEM_PROMPT = f"""You are a SQL query generator. Given a user question and database schema, generate a single SQLite SELECT query.

{DB_SCHEMA}

Rules:
- Only generate SELECT queries, never DDL or DML.
- Return ONLY the SQL query, nothing else. No markdown, no explanation.
- Use proper aggregation functions (SUM, AVG, COUNT, etc.) when needed.
- Format large numbers readably in the query if possible.
"""

ANSWER_SYSTEM_PROMPT = """You are an internal enterprise assistant. Given a user question and database query results, provide a clear answer.

Rules:
1. Cite the data source as [Source: database query].
2. Format numbers with proper separators (e.g., 45,000,000,000 VND).
3. Be concise and direct.
"""


def _generate_sql(question: str) -> str:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("LLM not configured — cannot generate SQL")

    llm = ChatOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        model=DEEPSEEK_MODEL,
        temperature=0,
        max_tokens=256,
        timeout=LLM_TIMEOUT,
    )

    response = llm.invoke([
        SystemMessage(content=SQL_SYSTEM_PROMPT),
        HumanMessage(content=question),
    ])

    sql = response.content.strip()
    sql = sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()
    return sql


def _validate_sql(sql: str) -> None:
    if DANGEROUS_RE.search(sql):
        raise ValueError(f"Dangerous SQL detected: {sql}")
    if not sql.upper().lstrip().startswith("SELECT"):
        raise ValueError(f"Only SELECT queries are allowed: {sql}")


def _execute_sql(sql: str) -> tuple[list[str], list[tuple]]:
    uri = f"file:{DB_FILE}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=SQL_QUERY_TIMEOUT)
    try:
        cursor = conn.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchmany(SQL_ROW_LIMIT)
        return columns, rows
    finally:
        conn.close()


def _format_answer(question: str, sql: str, columns: list[str], rows: list[tuple]) -> str:
    if not DEEPSEEK_API_KEY:
        header = " | ".join(columns)
        lines = [header, "-" * len(header)]
        for row in rows:
            lines.append(" | ".join(str(v) for v in row))
        return f"Query: {sql}\n\n" + "\n".join(lines) + "\n\n[Source: database query]"

    result_text = f"SQL: {sql}\nColumns: {columns}\nRows: {rows}"

    llm = ChatOpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        model=DEEPSEEK_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=512,
        timeout=LLM_TIMEOUT,
    )

    response = llm.invoke([
        SystemMessage(content=ANSWER_SYSTEM_PROMPT),
        HumanMessage(content=f"Question: {question}\n\nDatabase result:\n{result_text}"),
    ])
    return response.content


def execute_sql_query(question: str) -> tuple[str, str, float]:
    """Generate SQL from question, execute, format answer.

    Returns (answer, sql_query, total_ms).
    """
    t0 = time.perf_counter()

    sql = _generate_sql(question)
    _validate_sql(sql)
    columns, rows = _execute_sql(sql)
    answer = _format_answer(question, sql, columns, rows)

    total_ms = (time.perf_counter() - t0) * 1000
    return answer, sql, total_ms
