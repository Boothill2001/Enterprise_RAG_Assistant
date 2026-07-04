from __future__ import annotations

import json
from pathlib import Path

from config import DOCS_DIR, PERMISSIONS_FILE
from src.ingestion.chunking import Chunk, chunk_document


def _load_permissions() -> dict[str, list[str]]:
    with open(PERMISSIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _roles_for_department(department: str, permissions: dict[str, list[str]]) -> list[str]:
    """Return all roles that have access to a given department."""
    roles = []
    for role, departments in permissions.items():
        if department in departments:
            roles.append(role)
    return roles


def load_and_chunk_all_docs() -> list[Chunk]:
    """Load all markdown documents, enrich with metadata, and chunk."""
    permissions = _load_permissions()
    all_chunks: list[Chunk] = []

    for dept_dir in sorted(DOCS_DIR.iterdir()):
        if not dept_dir.is_dir():
            continue
        department = dept_dir.name
        access_roles = _roles_for_department(department, permissions)

        for md_file in sorted(dept_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            source = f"{department}/{md_file.name}"
            chunks = chunk_document(content, source, department, access_roles)
            all_chunks.extend(chunks)

    return all_chunks
