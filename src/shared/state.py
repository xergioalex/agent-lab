"""Shared graph state types.

``State`` is kept intact for the early modules (01, 02) and their smoke tests.
``AgentState`` is the richer, message-based state used by the advanced modules
(11+), built on LangGraph's ``add_messages`` reducer so that returning a partial
``{"messages": [...]}`` appends instead of overwriting.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class State(TypedDict):
    """Original minimal state — a single message string."""

    message: str


class AgentState(TypedDict, total=False):
    """Conversation-oriented state shared by advanced modules.

    - ``messages`` uses the ``add_messages`` reducer (append + de-dupe by id).
    - ``scratchpad`` accumulates intermediate strings (list concatenation).
    - ``context`` is free-form working memory for a single run.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    scratchpad: Annotated[list[str], operator.add]
    context: dict[str, Any]
