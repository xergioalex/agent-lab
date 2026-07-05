"""47 — Organizational Graph: multi-hop people/teams/projects queries.

Models a small org chart as a property graph — ``Person``, ``Team``, and
``Project`` nodes connected by ``REPORTS_TO``, ``MEMBER_OF``, ``OWNS``, and
``WORKS_ON`` relationships — and answers common organizational questions as
multi-hop graph traversals instead of SQL joins:

- "Who owns X?"            -> one-hop reverse lookup on ``OWNS``.
- "Who reports to Y?"      -> one-hop reverse lookup on ``REPORTS_TO``.
- "Which team touches Z?"  -> two-hop: ``WORKS_ON`` then ``MEMBER_OF``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src.shared` importable when run as `python src/47_organizational_graph/organizational_graph.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import InMemoryGraphStore, Node, get_logger  # noqa: E402

logger = get_logger(__name__)


def incoming(store: InMemoryGraphStore, target_id: str, rel_type: str) -> list[Node]:
    """Reverse neighbor lookup: nodes with a ``rel_type`` edge pointing at ``target_id``.

    ``InMemoryGraphStore.neighbors`` only walks outgoing edges, so answering
    "who points at this node" requires a manual scan over
    ``store.relationships`` — the graph equivalent of a reverse foreign-key
    lookup, but with no join table required.
    """
    source_ids = {
        rel.source for rel in store.relationships if rel.type == rel_type and rel.target == target_id
    }
    matches = [node for node in store.nodes if node.id in source_ids]
    return sorted(matches, key=lambda node: node.id)


def who_owns(store: InMemoryGraphStore, project_id: str) -> list[Node]:
    """One-hop query: who OWNS this project?"""
    return incoming(store, project_id, "OWNS")


def who_reports_to(store: InMemoryGraphStore, manager_id: str) -> list[Node]:
    """One-hop query: who REPORTS_TO this manager?"""
    return incoming(store, manager_id, "REPORTS_TO")


def which_teams_touch(store: InMemoryGraphStore, project_id: str) -> list[Node]:
    """Two-hop query: which teams have a member who WORKS_ON this project?

    Hop 1: reverse ``WORKS_ON`` to find the people working on the project.
    Hop 2: forward ``MEMBER_OF`` from each of those people to their team(s).
    """
    workers = incoming(store, project_id, "WORKS_ON")
    teams: dict[str, Node] = {}
    for person in workers:
        for team in store.neighbors(person.id, "MEMBER_OF"):
            teams[team.id] = team
    return sorted(teams.values(), key=lambda node: node.id)


def build_org_graph(store: InMemoryGraphStore) -> None:
    """A small org: two teams, a handful of people, and two shared projects."""
    store.upsert_node("platform", "Team", name="Platform Team")
    store.upsert_node("growth", "Team", name="Growth Team")

    store.upsert_node("grace", "Person", name="Grace", role="Director")
    store.upsert_node("hank", "Person", name="Hank", role="Engineering Manager")
    store.upsert_node("iris", "Person", name="Iris", role="Engineer")
    store.upsert_node("jamal", "Person", name="Jamal", role="Engineer")

    store.upsert_node("checkout", "Project", name="Checkout Revamp")
    store.upsert_node("onboarding", "Project", name="Onboarding Flow")

    store.add_relationship("hank", "REPORTS_TO", "grace")
    store.add_relationship("iris", "REPORTS_TO", "hank")
    store.add_relationship("jamal", "REPORTS_TO", "hank")

    store.add_relationship("iris", "MEMBER_OF", "platform")
    store.add_relationship("jamal", "MEMBER_OF", "growth")
    store.add_relationship("hank", "MEMBER_OF", "platform")

    store.add_relationship("hank", "OWNS", "checkout")
    store.add_relationship("iris", "WORKS_ON", "checkout")
    store.add_relationship("jamal", "WORKS_ON", "checkout")
    store.add_relationship("jamal", "WORKS_ON", "onboarding")


def main() -> None:
    store = InMemoryGraphStore()
    build_org_graph(store)

    owners = who_owns(store, "checkout")
    logger.info("who_owns(checkout) -> %s", [node.id for node in owners])
    print(f"who_owns(checkout)={[node.id for node in owners]}")

    reports = who_reports_to(store, "hank")
    print(f"who_reports_to(hank)={[node.id for node in reports]}")

    teams = which_teams_touch(store, "checkout")
    print(f"which_teams_touch(checkout)={[node.id for node in teams]}")

    teams_onboarding = which_teams_touch(store, "onboarding")
    print(f"which_teams_touch(onboarding)={[node.id for node in teams_onboarding]}")

    print("=== MODULE 47: ORGANIZATIONAL GRAPH COMPLETE ===")


if __name__ == "__main__":
    main()
