"""13 — Async Nodes: `await app.ainvoke(...)` and concurrent I/O.

Contrasts a synchronous graph (blocking ``time.sleep`` node, invoked
sequentially) against an asynchronous graph (``asyncio.sleep`` node, invoked
concurrently via ``asyncio.gather``) to show the wall-clock win when node
work is I/O-bound rather than CPU-bound.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

# Make `src.shared` importable when run as `python src/13_async_nodes/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph  # noqa: E402

from src.shared import AgentState, get_logger  # noqa: E402

logger = get_logger(__name__)

SIMULATED_DELAY_SECONDS = 0.05
TASK_COUNT = 5


def sync_fetch(state: AgentState) -> dict[str, object]:
    """A blocking node: simulates I/O with a synchronous sleep."""
    delay = state["context"]["delay"]
    time.sleep(delay)
    return {"context": {**state.get("context", {}), "label": f"sync-fetched-after-{delay}s"}}


async def async_fetch(state: AgentState) -> dict[str, object]:
    """A non-blocking node: simulates I/O with ``asyncio.sleep``."""
    delay = state["context"]["delay"]
    await asyncio.sleep(delay)
    return {"context": {**state.get("context", {}), "label": f"async-fetched-after-{delay}s"}}


def build_sync_graph():
    """Graph whose single node blocks the event loop for ``delay`` seconds."""
    graph = StateGraph(AgentState)
    graph.add_node("fetch", sync_fetch)
    graph.add_edge(START, "fetch")
    graph.add_edge("fetch", END)
    return graph.compile()


def build_async_graph():
    """Graph whose single node awaits ``asyncio.sleep`` instead of blocking."""
    graph = StateGraph(AgentState)
    graph.add_node("fetch", async_fetch)
    graph.add_edge(START, "fetch")
    graph.add_edge("fetch", END)
    return graph.compile()


def run_sequential(app, count: int, delay: float) -> float:
    """Invoke the sync graph ``count`` times back-to-back; total time accumulates."""
    start = time.perf_counter()
    for _ in range(count):
        app.invoke({"context": {"delay": delay}})
    return time.perf_counter() - start


async def run_concurrent(app, count: int, delay: float) -> float:
    """``await`` all ``count`` invocations concurrently via ``asyncio.gather``.

    Because each task spends its time in ``await asyncio.sleep(...)`` rather
    than blocking, the event loop interleaves them: wall-clock time stays
    close to a single delay instead of growing with ``count``.
    """
    start = time.perf_counter()
    await asyncio.gather(*(app.ainvoke({"context": {"delay": delay}}) for _ in range(count)))
    return time.perf_counter() - start


async def main_async() -> tuple[float, float]:
    sync_app = build_sync_graph()
    async_app = build_async_graph()

    sync_elapsed = run_sequential(sync_app, TASK_COUNT, SIMULATED_DELAY_SECONDS)
    logger.info("sequential sync run took %.3fs", sync_elapsed)

    async_elapsed = await run_concurrent(async_app, TASK_COUNT, SIMULATED_DELAY_SECONDS)
    logger.info("concurrent async run took %.3fs", async_elapsed)

    return sync_elapsed, async_elapsed


def main() -> None:
    sync_elapsed, async_elapsed = asyncio.run(main_async())

    print(f"tasks={TASK_COUNT} delay_per_task={SIMULATED_DELAY_SECONDS}s")
    print(f"sync sequential elapsed: {sync_elapsed:.3f}s")
    print(f"async concurrent elapsed: {async_elapsed:.3f}s")
    faster = sync_elapsed > async_elapsed
    print(f"speedup: async was faster than sync = {faster}")

    print("=== TRACK1 MODULE 13: ASYNC NODES COMPLETE ===")


if __name__ == "__main__":
    main()
