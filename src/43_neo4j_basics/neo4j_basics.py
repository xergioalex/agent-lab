"""43 — Neo4j Basics: the property-graph model and online/offline backend gating.

Demonstrates the property-graph model (labelled nodes, typed directed
relationships, arbitrary properties on both) via the shared
``InMemoryGraphStore``, and the pattern every graph-backed module in this
track reuses: prefer the real ``neo4j`` driver when ``NEO4J_URI`` is
configured, otherwise fall back to the offline in-memory store. The ``neo4j``
package is imported lazily, *inside* the configured branch, so the module
never fails to import when the driver isn't installed — which is the default
in this environment.
"""

from __future__ import annotations

from typing import Any

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/43_neo4j_basics/neo4j_basics.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryGraphStore, get_logger, get_settings  # noqa: E402

logger = get_logger(__name__)


class Neo4jGraphBackend:
    """Adapter over the real ``neo4j`` driver with the same surface used here.

    Only constructed when :meth:`Settings.has_neo4j` is true. The ``neo4j``
    import lives inside ``__init__`` — never at module top level — so this
    class can be defined and referenced even when the package is not
    installed; it simply cannot be *instantiated* offline.
    """

    def __init__(self, uri: str, user: str, password: str | None) -> None:
        from neo4j import GraphDatabase  # lazy import: only reached when NEO4J_URI is set

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

    def close(self) -> None:
        self._driver.close()


def build_graph_store() -> InMemoryGraphStore | Neo4jGraphBackend:
    """Return a graph backend: the real driver when configured, else the fake.

    Every module in Track 6 that talks to a graph store can reuse this exact
    gating pattern: check settings first, import the heavy/optional
    dependency lazily on the real path only, and keep the offline fallback
    fully functional so exercises never require a running service.
    """
    settings = get_settings()
    if settings.has_neo4j():
        logger.info("NEO4J_URI configured -> connecting to real Neo4j at %s", settings.neo4j_uri)
        try:
            return Neo4jGraphBackend(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
        except Exception as exc:  # pragma: no cover - only reachable with a real service configured
            logger.error("failed to connect to Neo4j (%s); falling back to in-memory store", exc)
            return InMemoryGraphStore()
    logger.info("NEO4J_URI not set -> using offline InMemoryGraphStore")
    return InMemoryGraphStore()


def seed_property_graph(store: InMemoryGraphStore) -> None:
    """Populate a tiny property graph: two people, a company, and their ties."""
    store.upsert_node("alice", "Person", name="Alice", title="Engineer")
    store.upsert_node("bob", "Person", name="Bob", title="Manager")
    store.upsert_node("acme", "Company", name="Acme Corp")
    store.add_relationship("alice", "WORKS_AT", "acme", since=2021)
    store.add_relationship("bob", "WORKS_AT", "acme", since=2018)
    store.add_relationship("alice", "REPORTS_TO", "bob")


def describe(store: InMemoryGraphStore) -> None:
    """Print the property graph in a deterministic, human-readable form."""
    print(f"stats={store.stats()}")
    for node in sorted(store.nodes, key=lambda n: n.id):
        print(f"node id={node.id} label={node.label} properties={node.properties}")
    for rel in sorted(store.relationships, key=lambda r: (r.source, r.type, r.target)):
        print(f"rel {rel.source} -[{rel.type}]-> {rel.target} properties={rel.properties}")
    neighbors = sorted(n.id for n in store.neighbors("alice"))
    print(f"alice neighbors={neighbors}")


def main() -> None:
    store = build_graph_store()

    if isinstance(store, InMemoryGraphStore):
        seed_property_graph(store)
        describe(store)
        print("=== MODULE 43: NEO4J BASICS COMPLETE (offline fallback) ===")
    else:  # pragma: no cover - exercised only with a real NEO4J_URI configured
        store.close()
        print("=== MODULE 43: NEO4J BASICS COMPLETE (real neo4j backend) ===")


if __name__ == "__main__":
    main()
