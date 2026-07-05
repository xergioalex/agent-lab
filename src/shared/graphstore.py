"""A tiny in-memory property graph used by the Neo4j and graph-memory modules.

Nodes carry labels and properties; relationships are typed and directed — the same
model Neo4j exposes via Cypher. Keeping an offline analogue lets learners reason
about graph memory before standing up a database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass
class Node:
    """A graph node: stable id, a label (e.g. ``Person``), and properties."""

    id: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    """A typed, directed edge between two node ids."""

    source: str
    type: str
    target: str
    properties: dict[str, Any] = field(default_factory=dict)


class InMemoryGraphStore:
    """Minimal property-graph store with a Neo4j-flavoured surface."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._rels: list[Relationship] = []

    def upsert_node(self, node_id: str, label: str, **properties: Any) -> Node:
        """Create or merge a node, updating its properties."""
        node = self._nodes.get(node_id)
        if node is None:
            node = Node(id=node_id, label=label, properties=dict(properties))
            self._nodes[node_id] = node
        else:
            node.properties.update(properties)
        return node

    def add_relationship(
        self, source: str, rel_type: str, target: str, **properties: Any
    ) -> Relationship:
        """Connect two existing nodes with a typed relationship."""
        rel = Relationship(source, rel_type, target, dict(properties))
        self._rels.append(rel)
        return rel

    def neighbors(self, node_id: str, rel_type: str | None = None) -> list[Node]:
        """Return nodes reachable from ``node_id`` (optionally filtered by type)."""
        out = []
        for rel in self._rels:
            if rel.source == node_id and (rel_type is None or rel.type == rel_type):
                target = self._nodes.get(rel.target)
                if target is not None:
                    out.append(target)
        return out

    def find(self, label: str | None = None, **properties: Any) -> list[Node]:
        """Find nodes matching a label and/or property values."""
        results = []
        for node in self._nodes.values():
            if label is not None and node.label != label:
                continue
            if all(node.properties.get(k) == v for k, v in properties.items()):
                results.append(node)
        return results

    @property
    def nodes(self) -> Iterator[Node]:
        return iter(self._nodes.values())

    @property
    def relationships(self) -> list[Relationship]:
        return list(self._rels)

    def stats(self) -> dict[str, int]:
        return {"nodes": len(self._nodes), "relationships": len(self._rels)}
