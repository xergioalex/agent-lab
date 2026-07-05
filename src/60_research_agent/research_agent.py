"""60 — Research Agent: planner + RAG + reflection/revision loop.

Capstone that integrates **Track 2** LLM composition (module `03_llm_nodes`),
**Track 5** retrieval-augmented generation over `InMemoryVectorStore`, and the
reflection/critique loop pattern (Tracks 7/8): the agent plans sub-questions,
retrieves supporting passages for each, drafts an answer, then critiques its
own draft for source coverage and revises (deepening retrieval) until the
critique passes.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/60_research_agent/research_agent.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, InMemoryVectorStore, get_logger  # noqa: E402

logger = get_logger(__name__)

# A small, fixed corpus so retrieval results are deterministic across runs.
_CORPUS: tuple[tuple[str, str], ...] = (
    (
        "vector-db",
        "A vector database stores embeddings and supports fast similarity "
        "search over them, unlike a relational store built for exact matches.",
    ),
    (
        "vector-db-2",
        "Vector databases like Qdrant index high-dimensional vectors so a "
        "query embedding can find its nearest neighbors efficiently.",
    ),
    (
        "embeddings",
        "Embeddings are numeric vectors that place semantically similar text "
        "close together in vector space, produced by an embedding model.",
    ),
    (
        "embeddings-2",
        "Text embeddings turn words and sentences into fixed-length float "
        "vectors so semantic similarity becomes a geometric distance.",
    ),
    (
        "similarity",
        "Cosine similarity measures the angle between two vectors, giving a "
        "score between -1 and 1 that vector search uses to rank results.",
    ),
    (
        "similarity-2",
        "Nearest-neighbor search ranks candidate vectors by similarity score "
        "so the most relevant passages surface first for a query.",
    ),
)

_QUESTION = "How do vector databases use embeddings for retrieval?"
_SUB_QUESTIONS: tuple[str, ...] = (
    "What is a vector database?",
    "What are embeddings?",
    "How is similarity measured?",
)
_REQUIRED_SOURCES = 2


def _build_store() -> InMemoryVectorStore:
    store = InMemoryVectorStore()
    ids, texts = zip(*_CORPUS)
    store.add_texts(list(texts), ids=list(ids))
    return store


_STORE = _build_store()


def plan(state: AgentState) -> dict[str, Any]:
    """Break the research question into fixed sub-questions (planner step)."""
    logger.info("planned %d sub-questions", len(_SUB_QUESTIONS))
    return {
        "context": {
            **state.get("context", {}),
            "sub_questions": list(_SUB_QUESTIONS),
            "k": 1,
            "revisions": 0,
        }
    }


def retrieve(state: AgentState) -> dict[str, Any]:
    """RAG step: retrieve top-k passages per sub-question from the vector store."""
    context = state["context"]
    k = context["k"]
    retrieved: dict[str, list[str]] = {}
    for sub_question in context["sub_questions"]:
        hits = _STORE.similarity_search(sub_question, k=k)
        retrieved[sub_question] = [hit.document.text for hit in hits]
    logger.info("retrieved passages with k=%d", k)
    return {"context": {**context, "retrieved": retrieved}}


def synthesize(state: AgentState) -> dict[str, Any]:
    """Draft an answer by concatenating retrieved passages per sub-question."""
    context = state["context"]
    lines = [f"Q: {_QUESTION}"]
    for sub_question, passages in context["retrieved"].items():
        lines.append(f"- {sub_question} -> {' '.join(passages)}")
    draft = "\n".join(lines)
    return {"context": {**context, "draft": draft}}


def reflect(state: AgentState) -> dict[str, Any]:
    """Critique the draft: does every sub-question have enough sources?"""
    context = state["context"]
    min_sources = min(len(v) for v in context["retrieved"].values())
    passed = min_sources >= _REQUIRED_SOURCES
    critique = (
        "coverage sufficient"
        if passed
        else f"coverage insufficient (min_sources={min_sources}), deepen retrieval"
    )
    logger.info("reflection: %s", critique)
    return {"context": {**context, "critique": critique, "passed": passed}}


def route_after_reflect(state: AgentState) -> str:
    """Revise (loop back to retrieve with more sources) or finalize."""
    return "finalize" if state["context"]["passed"] else "revise"


def revise(state: AgentState) -> dict[str, Any]:
    """Increase retrieval depth and try again (bounded by _REQUIRED_SOURCES)."""
    context = state["context"]
    return {
        "context": {
            **context,
            "k": _REQUIRED_SOURCES,
            "revisions": context["revisions"] + 1,
        }
    }


def finalize(state: AgentState) -> dict[str, Any]:
    """Report the final, reflection-approved answer."""
    return {"context": {**state["context"]}}


def build_graph():
    """Compile the plan -> retrieve -> synthesize -> reflect(-> revise) graph."""
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("retrieve", retrieve)
    graph.add_node("synthesize", synthesize)
    graph.add_node("reflect", reflect)
    graph.add_node("revise", revise)
    graph.add_node("finalize", finalize)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "retrieve")
    graph.add_edge("retrieve", "synthesize")
    graph.add_edge("synthesize", "reflect")
    graph.add_conditional_edges(
        "reflect", route_after_reflect, {"revise": "revise", "finalize": "finalize"}
    )
    graph.add_edge("revise", "retrieve")
    graph.add_edge("finalize", END)
    return graph.compile()


def main() -> None:
    app = build_graph()
    result = app.invoke({"context": {}})
    context = result["context"]

    print(f"question={_QUESTION!r}")
    print(f"sub_questions={context['sub_questions']}")
    print(f"revisions={context['revisions']} critique={context['critique']!r}")
    print(context["draft"])
    print("=== TRACK9 MODULE 60: RESEARCH AGENT COMPLETE ===")


if __name__ == "__main__":
    main()
