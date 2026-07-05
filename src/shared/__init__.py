"""Agent Lab shared library.

Reusable, offline-first building blocks for the advanced modules (11+). Import
from here to avoid duplicating infrastructure across exercises::

    from src.shared import get_chat_model, get_embeddings, InMemoryVectorStore

Everything degrades gracefully: with no API keys or services configured, the
deterministic fakes keep every exercise runnable and testable.
"""

from __future__ import annotations

from src.shared.config import Settings, get_settings
from src.shared.embeddings import get_embeddings
from src.shared.graphstore import InMemoryGraphStore, Node, Relationship
from src.shared.llm import FakeToolCallingModel, get_chat_model, is_offline
from src.shared.logging import get_logger
from src.shared.state import AgentState, State
from src.shared.tools import DEMO_TOOLS
from src.shared.vectorstore import Document, InMemoryVectorStore, SearchResult

__all__ = [
    "Settings",
    "get_settings",
    "get_embeddings",
    "InMemoryGraphStore",
    "Node",
    "Relationship",
    "FakeToolCallingModel",
    "get_chat_model",
    "is_offline",
    "get_logger",
    "AgentState",
    "State",
    "DEMO_TOOLS",
    "Document",
    "InMemoryVectorStore",
    "SearchResult",
]
