"""Offline indexing: chunk documents, embed, store in Qdrant + BM25."""

import sqlite3
import sys

from config import DB_FILE, SEED_SQL
from src.ingestion.metadata import load_and_chunk_all_docs
from src.ingestion.indexer import build_all_indexes


def seed_database() -> None:
    sql = SEED_SQL.read_text(encoding="utf-8")
    conn = sqlite3.connect(str(DB_FILE))
    conn.executescript(sql)
    conn.close()
    print(f"SQLite: seeded database at {DB_FILE}")


def main() -> None:
    print("=== Enterprise RAG Assistant — Build Index ===\n")

    print("[1/3] Loading and chunking documents...")
    chunks = load_and_chunk_all_docs()
    print(f"  -> {len(chunks)} chunks from {len(set(c.source for c in chunks))} documents\n")

    print("[2/3] Building indexes...")
    build_all_indexes(chunks)
    print()

    print("[3/3] Seeding SQLite database...")
    seed_database()

    print("\n=== Done! ===")


if __name__ == "__main__":
    main()
