"""45 — Dependency Analysis: DAGs, topological sort, and cycle detection.

Builds a small package/task dependency graph over the shared
``InMemoryGraphStore`` using a ``DEPENDS_ON`` relationship (``a DEPENDS_ON b``
means ``a`` requires ``b`` to run/build first). Implements Kahn's algorithm
for topological ordering and a DFS-based cycle detector, then demonstrates
both on a clean DAG and on a graph with a deliberately introduced cycle.
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

# Make `src.shared` importable when run as `python src/45_dependency_analysis/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryGraphStore, get_logger  # noqa: E402

logger = get_logger(__name__)

DEPENDS_ON = "DEPENDS_ON"


class GraphCycleError(RuntimeError):
    """Raised when a topological sort is requested on a graph with a cycle."""


def topological_order(store: InMemoryGraphStore, rel_type: str = DEPENDS_ON) -> list[str]:
    """Kahn's algorithm: return node ids in dependency-satisfying order.

    An edge ``a -[DEPENDS_ON]-> b`` means ``b`` must appear before ``a`` in
    the result (``b`` is a prerequisite of ``a``). Raises
    :class:`GraphCycleError` if the dependency graph is not a DAG.
    """
    in_degree = {node.id: 0 for node in store.nodes}
    dependents: dict[str, list[str]] = {node.id: [] for node in store.nodes}
    for rel in store.relationships:
        if rel.type != rel_type:
            continue
        dependents[rel.target].append(rel.source)
        in_degree[rel.source] += 1

    ready = deque(sorted(node_id for node_id, degree in in_degree.items() if degree == 0))
    order: list[str] = []
    while ready:
        node_id = ready.popleft()
        order.append(node_id)
        for dependent in sorted(dependents[node_id]):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                ready.append(dependent)

    if len(order) != len(in_degree):
        raise GraphCycleError(
            f"cycle detected: only {len(order)}/{len(in_degree)} nodes could be ordered"
        )
    return order


def find_cycle(store: InMemoryGraphStore, rel_type: str = DEPENDS_ON) -> list[str] | None:
    """DFS with node coloring: return the first cycle found, or ``None``.

    White = unvisited, gray = on the current DFS path, black = fully
    explored. Finding a gray node again means the path just closed a loop.
    """
    adjacency: dict[str, list[str]] = {node.id: [] for node in store.nodes}
    for rel in store.relationships:
        if rel.type == rel_type:
            adjacency[rel.source].append(rel.target)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node_id: WHITE for node_id in adjacency}
    path: list[str] = []

    def visit(node_id: str) -> list[str] | None:
        color[node_id] = GRAY
        path.append(node_id)
        for neighbor in sorted(adjacency[node_id]):
            if color[neighbor] == GRAY:
                start = path.index(neighbor)
                return [*path[start:], neighbor]
            if color[neighbor] == WHITE:
                found = visit(neighbor)
                if found is not None:
                    return found
        path.pop()
        color[node_id] = BLACK
        return None

    for node_id in sorted(adjacency):
        if color[node_id] == WHITE:
            cycle = visit(node_id)
            if cycle is not None:
                return cycle
    return None


def build_package_dag(store: InMemoryGraphStore) -> None:
    """A clean, acyclic package graph: webapp -> api -> {auth, db}."""
    for pkg in ("webapp", "api", "auth", "db"):
        store.upsert_node(pkg, "Package")
    store.add_relationship("webapp", DEPENDS_ON, "api")
    store.add_relationship("api", DEPENDS_ON, "auth")
    store.add_relationship("api", DEPENDS_ON, "db")
    store.add_relationship("auth", DEPENDS_ON, "db")


def build_cyclic_task_graph(store: InMemoryGraphStore) -> None:
    """A task graph with a deliberate cycle: task_a -> task_b -> task_c -> task_a."""
    for task in ("task_a", "task_b", "task_c"):
        store.upsert_node(task, "Task")
    store.add_relationship("task_a", DEPENDS_ON, "task_b")
    store.add_relationship("task_b", DEPENDS_ON, "task_c")
    store.add_relationship("task_c", DEPENDS_ON, "task_a")


def main() -> None:
    dag_store = InMemoryGraphStore()
    build_package_dag(dag_store)
    order = topological_order(dag_store)
    print(f"package_dag topological_order={order}")

    cyclic_store = InMemoryGraphStore()
    build_cyclic_task_graph(cyclic_store)
    try:
        topological_order(cyclic_store)
    except GraphCycleError as exc:
        logger.warning("topological_order failed as expected: %s", exc)
        print(f"task_graph topological_order failed: {exc}")

    cycle = find_cycle(cyclic_store)
    print(f"task_graph detected_cycle={cycle}")

    print("=== MODULE 45: DEPENDENCY ANALYSIS COMPLETE ===")


if __name__ == "__main__":
    main()
