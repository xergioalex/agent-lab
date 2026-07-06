"""46 — Root Cause Analysis: upstream traversal and blast-radius ranking.

Given a failing service in a ``DEPENDS_ON`` graph, walks *upstream* (the
things the failing node depends on, transitively) to collect root-cause
candidates, then ranks them by **blast radius** — how many nodes ultimately
depend on that candidate. A candidate with a larger blast radius is a more
central point of failure and a more likely true root cause when several
downstream services are failing at once.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/46_root_cause_analysis/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryGraphStore, get_logger  # noqa: E402

logger = get_logger(__name__)

DEPENDS_ON = "DEPENDS_ON"


def upstream_candidates(
    store: InMemoryGraphStore, failing_node: str, rel_type: str = DEPENDS_ON
) -> set[str]:
    """Collect every node ``failing_node`` depends on, directly or transitively.

    This is the "upstream" direction: following ``DEPENDS_ON`` edges forward
    from the failing node reaches everything that could have caused it to
    fail. ``store.neighbors`` already returns the targets of outgoing edges,
    so no reversal is needed here.
    """
    visited: set[str] = set()
    frontier = [failing_node]
    while frontier:
        current = frontier.pop()
        for neighbor in store.neighbors(current, rel_type):
            if neighbor.id not in visited:
                visited.add(neighbor.id)
                frontier.append(neighbor.id)
    return visited


def blast_radius(store: InMemoryGraphStore, node_id: str, rel_type: str = DEPENDS_ON) -> int:
    """Count nodes that transitively depend on ``node_id`` (downstream impact).

    This is the reverse direction: how many nodes would be affected if
    ``node_id`` were to fail. Since ``InMemoryGraphStore.neighbors`` only
    exposes outgoing edges, the reverse walk is done manually over
    ``store.relationships``.
    """
    visited: set[str] = set()
    frontier = [node_id]
    while frontier:
        current = frontier.pop()
        for rel in store.relationships:
            if rel.type == rel_type and rel.target == current and rel.source not in visited:
                visited.add(rel.source)
                frontier.append(rel.source)
    return len(visited)


def rank_root_causes(
    store: InMemoryGraphStore, failing_node: str, rel_type: str = DEPENDS_ON
) -> list[tuple[str, int]]:
    """Rank upstream candidates by blast radius, largest first (ties by id)."""
    candidates = upstream_candidates(store, failing_node, rel_type)
    ranked = [(node_id, blast_radius(store, node_id, rel_type)) for node_id in candidates]
    ranked.sort(key=lambda pair: (-pair[1], pair[0]))
    return ranked


def build_service_graph(store: InMemoryGraphStore) -> None:
    """A small service topology with one clear single point of failure (database)."""
    for service in ("web_app", "api_gateway", "auth_service", "cache", "database"):
        store.upsert_node(service, "Service")
    store.add_relationship("web_app", DEPENDS_ON, "api_gateway")
    store.add_relationship("api_gateway", DEPENDS_ON, "auth_service")
    store.add_relationship("api_gateway", DEPENDS_ON, "cache")
    store.add_relationship("auth_service", DEPENDS_ON, "database")
    store.add_relationship("cache", DEPENDS_ON, "database")


def main() -> None:
    store = InMemoryGraphStore()
    build_service_graph(store)

    failing_node = "web_app"
    ranked = rank_root_causes(store, failing_node)
    logger.info("ranked %d upstream candidates for %s", len(ranked), failing_node)

    print(f"failing_node={failing_node}")
    print("root_cause_candidates (ranked by blast_radius, most likely first):")
    for node_id, radius in ranked:
        print(f"  {node_id}: blast_radius={radius}")

    top_candidate, top_radius = ranked[0]
    print(f"most_likely_root={top_candidate} (impacts {top_radius} downstream service(s))")

    print("=== MODULE 46: ROOT CAUSE ANALYSIS COMPLETE ===")


if __name__ == "__main__":
    main()
