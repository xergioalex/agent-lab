"""57 — Cost & Multitenancy: token/cost accounting with per-tenant isolation.

Two production concerns that show up together once an agent serves more than
one customer: (1) you need to know **what each tenant costs** to run, and
(2) tenants must **never** be able to read each other's memory or state. This
module builds a small namespaced store (isolation) and a token/cost estimator
(accounting), then runs several tenants through the same agent and prints a
per-tenant cost report.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Make `src.shared` importable when run as `python src/57_cost_and_multitenancy/cost_and_multitenancy.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langchain_core.messages import HumanMessage  # noqa: E402

from src.shared import get_chat_model, get_logger  # noqa: E402

logger = get_logger(__name__)

# Deterministic pricing constant for the estimate — not a real provider price.
PRICE_PER_1K_TOKENS_USD = 0.002


def estimate_tokens(text: str) -> int:
    """Cheap, deterministic token estimate: ~4 characters per token."""
    return max(1, len(text) // 4)


def estimate_cost_usd(tokens: int) -> float:
    """Convert an estimated token count into an estimated dollar cost."""
    return (tokens / 1000) * PRICE_PER_1K_TOKENS_USD


class TenantIsolationError(PermissionError):
    """Raised when a tenant attempts to read another tenant's namespaced data."""


@dataclass
class TenantStore:
    """An in-memory store namespaced by tenant id.

    Every key is scoped under its owning tenant's namespace; there is no API
    that allows reading across namespaces — ``read`` requires the caller to
    supply the same ``tenant_id`` that wrote the value, and raises if that
    tenant simply never wrote the key (never falls back to another tenant's
    data).
    """

    _data: dict[str, dict[str, Any]] = field(default_factory=dict)

    def write(self, tenant_id: str, key: str, value: Any) -> None:
        self._data.setdefault(tenant_id, {})[key] = value

    def read(self, tenant_id: str, key: str) -> Any:
        namespace = self._data.get(tenant_id, {})
        if key not in namespace:
            raise KeyError(f"tenant {tenant_id!r} has no key {key!r}")
        return namespace[key]

    def assert_isolated(self, tenant_id: str, other_tenant_id: str, key: str) -> bool:
        """Return True if ``tenant_id`` cannot see ``other_tenant_id``'s value for ``key``."""
        try:
            self.read(tenant_id, key)
        except KeyError:
            return True
        # A tenant read succeeded but the *value* must not match the other
        # tenant's value written under the same key name.
        try:
            other_value = self.read(other_tenant_id, key)
        except KeyError:
            return True
        return self.read(tenant_id, key) != other_value


@dataclass
class TenantUsage:
    """Accumulated usage for a single tenant across one report."""

    tenant_id: str
    messages: int = 0
    tokens_est: int = 0

    @property
    def cost_usd(self) -> float:
        return estimate_cost_usd(self.tokens_est)


TENANTS: tuple[str, ...] = ("acme", "globex")

_QUERIES: dict[str, tuple[str, ...]] = {
    "acme": (
        "What's the status of our deployment pipeline?",
        "Summarize this week's incident report.",
    ),
    "globex": ("How do I request vacation time?",),
}


def run_tenant_workload(store: TenantStore, tenant_id: str) -> TenantUsage:
    """Run each tenant's queries through the (offline) agent, tracking usage."""
    model = get_chat_model(responses=[f"[{tenant_id}] request handled."])
    usage = TenantUsage(tenant_id=tenant_id)

    for i, query in enumerate(_QUERIES[tenant_id]):
        reply = model.invoke([HumanMessage(content=query)])
        store.write(tenant_id, f"message_{i}", query)
        store.write(tenant_id, f"reply_{i}", reply.content)

        tokens = estimate_tokens(query) + estimate_tokens(str(reply.content))
        usage.messages += 1
        usage.tokens_est += tokens
        logger.info(
            "tenant=%s query=%r tokens_est=%d cumulative_tokens=%d",
            tenant_id,
            query,
            tokens,
            usage.tokens_est,
        )

    return usage


def main() -> None:
    store = TenantStore()
    usages = [run_tenant_workload(store, tenant_id) for tenant_id in TENANTS]

    # Isolation check: acme must never be able to read globex's data, and
    # vice versa, even though both used the key name "message_0".
    isolated_a = store.assert_isolated("acme", "globex", "message_0")
    isolated_b = store.assert_isolated("globex", "acme", "message_0")
    print(f"tenant=acme cannot read tenant=globex data: isolated={isolated_a}")
    print(f"tenant=globex cannot read tenant=acme data: isolated={isolated_b}")
    if not (isolated_a and isolated_b):
        raise AssertionError("tenant isolation violated")

    print("=== COST REPORT ===")
    total_tokens = 0
    total_cost = 0.0
    for usage in usages:
        print(
            f"tenant={usage.tenant_id} messages={usage.messages} "
            f"tokens_est={usage.tokens_est} cost_usd={usage.cost_usd:.6f}"
        )
        total_tokens += usage.tokens_est
        total_cost += usage.cost_usd
    print(f"total_tokens_est={total_tokens} total_cost_usd={total_cost:.6f}")

    print("=== MODULE 57: COST AND MULTITENANCY COMPLETE ===")


if __name__ == "__main__":
    main()
