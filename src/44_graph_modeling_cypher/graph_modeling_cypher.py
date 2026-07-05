"""44 — Graph Modeling & Cypher-Style Queries.

Contrasts relational modeling (rows, foreign keys, joins) with property-graph
modeling (nodes, typed directed relationships, no joins — just walk edges),
then implements a tiny Cypher-style query helper over the shared
``InMemoryGraphStore``:

    MATCH (a:Label)-[:REL_TYPE]->(b:Label {prop: value}) RETURN a, r, b

expressed as a plain Python function instead of a query string.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/44_graph_modeling_cypher/graph_modeling_cypher.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryGraphStore, Node, Relationship, get_logger  # noqa: E402

logger = get_logger(__name__)


def match(
    store: InMemoryGraphStore,
    start_label: str,
    rel_type: str,
    end_label: str | None = None,
    **end_filters: Any,
) -> list[tuple[Node, Relationship, Node]]:
    """Cypher-style pattern match: ``MATCH (a:start_label)-[:rel_type]->(b:end_label {filters})``.

    Returns every ``(start, relationship, end)`` triple satisfying the
    pattern, mirroring a Cypher ``RETURN a, r, b``. Filtering happens on the
    end node's properties, matching Cypher's ``WHERE b.prop = value`` idiom.
    """
    nodes_by_id = {node.id: node for node in store.nodes}
    matches: list[tuple[Node, Relationship, Node]] = []
    for start in store.find(label=start_label):
        for rel in store.relationships:
            if rel.source != start.id or rel.type != rel_type:
                continue
            end = nodes_by_id.get(rel.target)
            if end is None:
                continue
            if end_label is not None and end.label != end_label:
                continue
            if not all(end.properties.get(key) == value for key, value in end_filters.items()):
                continue
            matches.append((start, rel, end))
    matches.sort(key=lambda triple: (triple[0].id, triple[2].id))
    return matches


def seed_project_graph(store: InMemoryGraphStore) -> None:
    """A small engineering graph: people, teams, and the projects they own."""
    store.upsert_node("dana", "Person", name="Dana", seniority="senior")
    store.upsert_node("evan", "Person", name="Evan", seniority="junior")
    store.upsert_node("frida", "Person", name="Frida", seniority="senior")
    store.upsert_node("payments", "Project", name="Payments API", status="active")
    store.upsert_node("search", "Project", name="Search Service", status="active")
    store.upsert_node("legacy", "Project", name="Legacy Billing", status="deprecated")

    store.add_relationship("dana", "OWNS", "payments")
    store.add_relationship("evan", "OWNS", "search")
    store.add_relationship("frida", "OWNS", "legacy")
    store.add_relationship("dana", "OWNS", "legacy")


def main() -> None:
    store = InMemoryGraphStore()
    seed_project_graph(store)

    # Pattern 1: everyone who owns an *active* project — the graph analogue of
    # `SELECT p.* FROM person p JOIN owns o ON ... JOIN project pr ON ...
    #  WHERE pr.status = 'active'` with zero joins, just an edge walk.
    active_ownership = match(store, "Person", "OWNS", "Project", status="active")
    print("MATCH (p:Person)-[:OWNS]->(pr:Project {status: 'active'})")
    for owner, rel, project in active_ownership:
        print(f"  {owner.id} -[{rel.type}]-> {project.id} ({project.properties['name']})")

    # Pattern 2: every ownership edge regardless of project status — shows the
    # same helper generalizes by simply omitting the filter.
    all_ownership = match(store, "Person", "OWNS")
    print("MATCH (p:Person)-[:OWNS]->(pr) RETURN p, pr")
    for owner, rel, project in all_ownership:
        print(f"  {owner.id} -[{rel.type}]-> {project.id}")

    # Relational contrast: in SQL this pattern needs a `person` table, a
    # `project` table, and an `owns` join table plus two JOINs. In the graph
    # model the relationship *is* the join — no intermediate table required.
    print(f"total_people={len(store.find(label='Person'))} total_projects={len(store.find(label='Project'))}")

    print("=== MODULE 44: GRAPH MODELING & CYPHER COMPLETE ===")


if __name__ == "__main__":
    main()
