"""08 — Graph Memory (Neo4j): property-graph traversal in a StateGraph.

Builds a small org chart, walks relationships, and answers a leadership query.
Uses ``InMemoryGraphStore`` offline; connects to Neo4j when ``NEO4J_URI`` is set.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import InMemoryGraphStore, Node, get_logger, get_settings  # noqa: E402

logger = get_logger(__name__)


class Neo4jGraphBackend:
    def __init__(self, uri: str, user: str, password: str | None) -> None:
        from neo4j import GraphDatabase  # noqa: PLC0415

        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def upsert_node(self, node_id: str, label: str, **properties: Any) -> None:
        query = f"MERGE (n:{label} {{id: $id}}) SET n += $props"
        with self._driver.session() as session:
            session.run(query, id=node_id, props=properties)

    def add_relationship(
        self, source: str, rel_type: str, target: str, **properties: Any
    ) -> None:
        query = (
            "MATCH (a {id: $source}), (b {id: $target}) "
            f"MERGE (a)-[r:{rel_type}]->(b) SET r += $props"
        )
        with self._driver.session() as session:
            session.run(query, source=source, target=target, props=properties)

    def neighbors(self, node_id: str, rel_type: str | None = None) -> list[Node]:
        rel_filter = f":{rel_type}" if rel_type else ""
        query = (
            f"MATCH (a {{id: $id}})-[r{rel_filter}]->(b) "
            "RETURN b.id AS id, labels(b) AS labels, properties(b) AS props"
        )
        with self._driver.session() as session:
            rows = session.run(query, id=node_id)
            return [
                Node(
                    id=row["id"],
                    label=row["labels"][0] if row["labels"] else "Node",
                    properties=dict(row["props"]),
                )
                for row in rows
            ]


def build_graph_store() -> InMemoryGraphStore | Neo4jGraphBackend:
    settings = get_settings()
    if settings.has_neo4j():
        logger.info("connecting to Neo4j at %s", settings.neo4j_uri)
        return Neo4jGraphBackend(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    logger.info("using InMemoryGraphStore (offline)")
    return InMemoryGraphStore()


class GraphState(TypedDict, total=False):
    store: Any
    backend: str
    finding: str


def seed_graph(state: GraphState) -> dict[str, object]:
    store = build_graph_store()
    if isinstance(store, InMemoryGraphStore):
        store.upsert_node("alice", "Person", name="Alice")
        store.upsert_node("bob", "Person", name="Bob")
        store.upsert_node("engineering", "Department", name="Engineering")
        store.add_relationship("alice", "REPORTS_TO", "bob")
        store.add_relationship("engineering", "LED_BY", "bob")
    else:
        store.upsert_node("alice", "Person", name="Alice")
        store.upsert_node("bob", "Person", name="Bob")
        store.upsert_node("engineering", "Department", name="Engineering")
        store.add_relationship("alice", "REPORTS_TO", "bob")
        store.add_relationship("engineering", "LED_BY", "bob")
    backend = type(store).__name__
    return {"store": store, "backend": backend}


def traverse(state: GraphState) -> dict[str, object]:
    store = state["store"]
    lead = store.neighbors("engineering", "LED_BY")
    manager = store.neighbors("alice", "REPORTS_TO")
    finding = (
        f"Engineering led by {lead[0].properties['name']}; "
        f"Alice reports to {manager[0].properties['name']}"
    )
    return {"finding": finding}


def answer(state: GraphState) -> dict[str, object]:
    print(f"backend={state['backend']} finding={state['finding']!r}")
    return {}


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("seed", seed_graph)
    graph.add_node("traverse", traverse)
    graph.add_node("answer", answer)
    graph.add_edge(START, "seed")
    graph.add_edge("seed", "traverse")
    graph.add_edge("traverse", "answer")
    graph.add_edge("answer", END)
    return graph.compile()


def main() -> None:
    build_graph().invoke({})
    print("=== MODULE 08: GRAPH MEMORY NEO4J COMPLETE ===")


if __name__ == "__main__":
    main()
