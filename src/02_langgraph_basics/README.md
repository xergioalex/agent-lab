
# 02 - LangGraph Basics

## Concept

LangGraph is a **state machine for AI workflows**

## Key ideas

- Nodes = functions
- Edges = transitions
- State flows through graph

## Goal

Build your first execution graph

## Run

From the repository root:

```bash
python src/02_langgraph_basics/basic_graph.py
```

## Expected output

```
{'message': 'start -> A -> B'}
```

## What happens

1. A `StateGraph` is created with two nodes: `A` and `B`
2. Entry point is `A`; edge `A → B`; finish point is `B`
3. Graph is compiled and invoked with `{"message": "start"}`
4. Each node appends its label to the message

## Automated test

Covered by `pytest` — `test_langgraph_basics_runs` in `tests/test_smoke.py`.
