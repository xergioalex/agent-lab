"""Deterministic demo tools shared by the tool-calling and agent modules.

Every tool is offline, side-effect-free, and returns a stable string so agent
loops produce reproducible transcripts. In a real system these would hit Slack,
a weather API, a task tracker, etc. — the *shape* (typed inputs, string result)
matches what an LLM tool call expects.
"""

from __future__ import annotations

import hashlib

from langchain_core.tools import tool

# A small canned knowledge base so RAG-style lookups return something meaningful.
_KNOWLEDGE_BASE = {
    "standup": "Daily standups happen at 9:30am in the #team channel.",
    "vacation": "Request vacation in the HR portal at least two weeks ahead.",
    "deploy": "Production deploys run through CI after two approvals.",
    "oncall": "The on-call engineer rotates weekly; check the #oncall channel.",
}


@tool
def get_weather(city: str) -> str:
    """Return a short weather report for a city."""
    return f"The weather in {city} is 21C and sunny."


@tool
def search_knowledge_base(query: str) -> str:
    """Look up an answer in the company knowledge base."""
    for keyword, answer in _KNOWLEDGE_BASE.items():
        if keyword in query.lower():
            return answer
    return "No matching knowledge-base article found."


@tool
def create_task(title: str) -> str:
    """Create a task in the tracker and return its id."""
    # hashlib (not built-in hash) keeps the id stable across processes/runs.
    task_id = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16) % 1000
    return f"Created task 'TASK-{task_id:03d}': {title}"


@tool
def add_numbers(a: int, b: int) -> str:
    """Add two integers and return the sum."""
    return f"The sum is {a + b}."


@tool
def send_slack(message: str) -> str:
    """Send a message to the team Slack channel."""
    return f"Slack sent: {message}"


DEMO_TOOLS = [
    get_weather,
    search_knowledge_base,
    create_task,
    add_numbers,
    send_slack,
]
"""Default tool belt reused across modules — import and slice as needed."""
