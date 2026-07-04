from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, asdict

from config import MAX_CHUNK_TOKENS, CHUNK_OVERLAP_RATIO


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
APPROX_CHARS_PER_TOKEN = 4
MAX_CHUNK_CHARS = MAX_CHUNK_TOKENS * APPROX_CHARS_PER_TOKEN
OVERLAP_CHARS = int(MAX_CHUNK_CHARS * CHUNK_OVERLAP_RATIO)


@dataclass
class Chunk:
    text: str
    source: str
    section: str
    department: str
    access_roles: list[str] = field(default_factory=list)
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return asdict(self)


def _split_sections(content: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) pairs."""
    matches = list(HEADING_RE.finditer(content))
    if not matches:
        return [("", content.strip())]

    sections = []
    preamble = content[: matches[0].start()].strip()
    if preamble:
        sections.append(("", preamble))

    for i, m in enumerate(matches):
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end].strip()
        if body:
            sections.append((title, body))

    return sections


def _split_long_text(text: str, title: str) -> list[str]:
    """Split text exceeding MAX_CHUNK_CHARS on paragraph boundaries with overlap."""
    if len(text) <= MAX_CHUNK_CHARS:
        prefix = f"{title}\n{text}" if title else text
        return [prefix]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= MAX_CHUNK_CHARS:
            current = candidate
        else:
            if current:
                prefix = f"{title}\n{current}" if title else current
                chunks.append(prefix)
                overlap = current[-OVERLAP_CHARS:] if len(current) > OVERLAP_CHARS else current
                current = f"{overlap}\n\n{para}".strip()
            else:
                for j in range(0, len(para), MAX_CHUNK_CHARS):
                    piece = para[j : j + MAX_CHUNK_CHARS]
                    prefix = f"{title}\n{piece}" if title else piece
                    chunks.append(prefix)
                current = ""

    if current:
        prefix = f"{title}\n{current}" if title else current
        chunks.append(prefix)

    return chunks


def chunk_document(content: str, source: str, department: str, access_roles: list[str]) -> list[Chunk]:
    """Chunk a markdown document into Chunk objects with metadata."""
    sections = _split_sections(content)
    chunks: list[Chunk] = []

    for title, body in sections:
        pieces = _split_long_text(body, title)
        for piece in pieces:
            chunks.append(Chunk(
                text=piece,
                source=source,
                section=title,
                department=department,
                access_roles=access_roles,
            ))

    return chunks
