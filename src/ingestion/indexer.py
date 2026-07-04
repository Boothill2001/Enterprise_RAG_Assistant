from __future__ import annotations

import pickle
import re

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    PayloadSchemaType,
)
from rank_bm25 import BM25Okapi

from config import (
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_IN_MEMORY,
    QDRANT_PATH,
    COLLECTION_NAME,
    BM25_PICKLE,
)
from src.ingestion.chunking import Chunk
from src.ingestion.embeddings import embed_texts

TOKEN_RE = re.compile(r"[a-z0-9]+")

_qdrant_client = None


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        if QDRANT_IN_MEMORY:
            _qdrant_client = QdrantClient(path=QDRANT_PATH)
        else:
            _qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return _qdrant_client


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def build_qdrant_index(chunks: list[Chunk]) -> None:
    """Embed chunks and upsert into Qdrant with payload indexing."""
    client = get_qdrant_client()

    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    texts = [c.text for c in chunks]
    vectors = embed_texts(texts)
    dim = vectors.shape[1]

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="access_roles",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="department",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    points = [
        PointStruct(
            id=i,
            vector=vectors[i].tolist(),
            payload={
                "chunk_id": c.chunk_id,
                "text": c.text,
                "source": c.source,
                "section": c.section,
                "department": c.department,
                "access_roles": c.access_roles,
            },
        )
        for i, c in enumerate(chunks)
    ]

    batch_size = 100
    for start in range(0, len(points), batch_size):
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points[start : start + batch_size],
        )

    print(f"Qdrant: indexed {len(points)} chunks into '{COLLECTION_NAME}'")


def build_bm25_index(chunks: list[Chunk]) -> None:
    """Build BM25 index and save to pickle."""
    corpus = [_tokenize(c.text) for c in chunks]
    bm25 = BM25Okapi(corpus)

    chunk_data = [c.to_dict() for c in chunks]
    with open(BM25_PICKLE, "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunk_data}, f)

    print(f"BM25: indexed {len(chunks)} chunks, saved to {BM25_PICKLE}")


def build_all_indexes(chunks: list[Chunk]) -> None:
    build_qdrant_index(chunks)
    build_bm25_index(chunks)
