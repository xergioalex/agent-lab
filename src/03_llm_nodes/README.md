
# 03 - LLM Nodes

## Concept

Add intelligence using LLMs inside graph nodes.

## Key idea

LLM is just another node in the graph.

## Goal

Call OpenAI from a node.

## Prerequisites

Set your OpenAI API key (never commit this value):

```bash
export OPENAI_API_KEY=sk-your-key
```

See [docs/SECURITY.md](../../docs/SECURITY.md) for safe handling.

## Run

From the repository root:

```bash
export OPENAI_API_KEY=sk-your-key
python src/03_llm_nodes/llm_node.py
```

## Expected output

A dict with an LLM-generated response (exact text varies per call):

```
{'response': 'Hello! How can I assist you today?'}
```

## Without API key

The script exits with an OpenAI credentials error. This is expected — `pytest`
validates this behavior via `test_llm_nodes_requires_api_key`.

## What happens

1. `ChatOpenAI` is initialized with model `gpt-4o-mini`
2. `call_llm` invokes the model with `state["message"]`
3. Returns `{"response": <model content>}`

## Automated test

`test_llm_nodes_requires_api_key` confirms the script fails cleanly when
`OPENAI_API_KEY` is unset. Live API validation is manual.
