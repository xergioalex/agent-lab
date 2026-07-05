"""Central configuration for Agent Lab.

Settings are read lazily from environment variables so that:

- Offline exercises run with zero configuration (deterministic fakes kick in).
- Real integrations (OpenAI, Qdrant, Neo4j) activate automatically when the
  matching environment variables are present.

Nothing here is a secret. API keys live only in the environment — see
``docs/SECURITY.md``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Backwards-compatible constant used by the early modules (03_llm_nodes).
OPENAI_MODEL = "gpt-4o-mini"

# Default embedding dimensionality for the offline deterministic embedder.
DEFAULT_EMBEDDING_DIM = 256


@dataclass(frozen=True)
class Settings:
    """Immutable snapshot of the environment configuration.

    Build one with :func:`get_settings`. Feature-detection helpers
    (``has_openai`` …) let modules pick a real backend or an offline fake.
    """

    openai_api_key: str | None = None
    openai_model: str = OPENAI_MODEL
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = DEFAULT_EMBEDDING_DIM
    temperature: float = 0.0

    qdrant_url: str | None = None
    qdrant_api_key: str | None = None

    neo4j_uri: str | None = None
    neo4j_user: str = "neo4j"
    neo4j_password: str | None = None

    log_level: str = "INFO"

    def has_openai(self) -> bool:
        """True when a real OpenAI key is configured."""
        return bool(self.openai_api_key)

    def has_qdrant(self) -> bool:
        """True when a real Qdrant endpoint is configured."""
        return bool(self.qdrant_url)

    def has_neo4j(self) -> bool:
        """True when a real Neo4j endpoint is configured."""
        return bool(self.neo4j_uri and self.neo4j_password)


def get_settings() -> Settings:
    """Read the current environment into an immutable :class:`Settings`.

    Called at runtime (not import time) so tests can toggle env vars.
    """
    return Settings(
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        openai_model=os.environ.get("OPENAI_MODEL", OPENAI_MODEL),
        embedding_model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_dim=int(os.environ.get("EMBEDDING_DIM", DEFAULT_EMBEDDING_DIM)),
        temperature=float(os.environ.get("LLM_TEMPERATURE", "0.0")),
        qdrant_url=os.environ.get("QDRANT_URL"),
        qdrant_api_key=os.environ.get("QDRANT_API_KEY"),
        neo4j_uri=os.environ.get("NEO4J_URI"),
        neo4j_user=os.environ.get("NEO4J_USER", "neo4j"),
        neo4j_password=os.environ.get("NEO4J_PASSWORD"),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )
