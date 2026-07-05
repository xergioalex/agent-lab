"""Embedding factory with a deterministic, dependency-free offline fallback.

Returns real ``OpenAIEmbeddings`` when a key is configured. Otherwise it returns
:class:`HashingEmbeddings` — a pure-Python bag-of-words hashing embedder. Unlike a
random fake, its vectors carry real signal (documents sharing words score higher),
so offline RAG demos return genuinely relevant results and are reproducible across
runs (it uses ``hashlib``, not the salted built-in ``hash``).
"""

from __future__ import annotations

import hashlib
import re

from langchain_core.embeddings import Embeddings

from src.shared.config import get_settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class HashingEmbeddings(Embeddings):
    """Deterministic bag-of-words hashing embedder (no numpy required)."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for token in _tokenize(text):
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            index = int(digest, 16) % self.dim
            sign = 1.0 if int(digest[-1], 16) % 2 == 0 else -1.0
            vector[index] += sign
        return vector

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def get_embeddings() -> Embeddings:
    """Return an embeddings backend (real if ``OPENAI_API_KEY`` is set)."""
    settings = get_settings()
    if settings.has_openai():
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(model=settings.embedding_model)
    return HashingEmbeddings(dim=settings.embedding_dim)
