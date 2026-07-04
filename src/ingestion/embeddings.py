from __future__ import annotations

import numpy as np
from functools import lru_cache
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts: list[str], batch_size: int = 64) -> np.ndarray:
    model = _get_model()
    vectors = model.encode(texts, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=True)
    return np.array(vectors, dtype=np.float32)


def embed_query(query: str) -> np.ndarray:
    model = _get_model()
    vector = model.encode(query, normalize_embeddings=True)
    return np.array(vector, dtype=np.float32)
