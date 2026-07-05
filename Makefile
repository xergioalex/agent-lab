# Agent Lab — developer task runner.
# The `test` target is the HARD GATE: it must pass OFFLINE (no API keys/services).
# lint/typecheck are advisory and print an install hint if the tool is missing.

.DEFAULT_GOAL := help
PY ?= python
MODULE ?=

.PHONY: help install install-dev test lint format typecheck run up down check

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Install core runtime dependencies (pip)
	$(PY) -m pip install -r requirements.txt

install-dev:  ## Install the developer toolchain (ruff, mypy, pytest, pre-commit)
	$(PY) -m pip install -e ".[dev]"

test:  ## Run the offline smoke suite (HARD GATE — no keys/services required)
	$(PY) -m pytest

lint:  ## Lint with ruff (advisory)
	@ruff check src tests || { echo ">> ruff not installed? run: pip install ruff"; exit 1; }

format:  ## Auto-format with ruff
	@ruff format src tests || { echo ">> ruff not installed? run: pip install ruff"; exit 1; }

typecheck:  ## Type-check the shared library with mypy (advisory)
	@mypy src/shared || { echo ">> mypy not installed? run: pip install mypy"; exit 1; }

run:  ## Run a module script, e.g. `make run MODULE=01_state_basics/hello_world.py`
	@test -n "$(MODULE)" || { echo "Usage: make run MODULE=<folder>/<script>.py"; exit 1; }
	$(PY) src/$(MODULE)

up:  ## Start optional backends (Qdrant + Neo4j) via docker compose
	docker compose up -d

down:  ## Stop optional backends
	docker compose down

check: test  ## Full check: tests (gate) + advisory lint + typecheck
	-@ruff check src tests
	-@mypy src/shared
