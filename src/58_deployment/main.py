"""58 — Deployment: reading and validating the compose + CI shapes from Task 1.

This module does not add new infrastructure — it **explains and validates**
what Task 1 already shipped: `docker-compose.yml` (optional Qdrant/Neo4j
backends for local dev) and `.github/workflows/ci.yml` (the offline test
pipeline). It parses both files as plain text (no new dependency — YAML
parsing is intentionally avoided so this module has zero extra requirements)
and prints a readiness report mapping local dev -> container -> pipeline.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Make `src.shared` importable when run as `python src/58_deployment/main.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import get_logger  # noqa: E402

logger = get_logger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"
CI_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"


@dataclass(frozen=True)
class ReadinessCheck:
    """One pass/fail fact about the deployment configuration."""

    name: str
    passed: bool
    detail: str


def _read_text(path: Path) -> str:
    """Read a config file's text, raising a clear error if it is missing.

    Never swallow a missing/misconfigured deployment file silently — a
    broken compose or CI file should fail loudly, here and in a real
    pipeline alike.
    """
    if not path.exists():
        raise FileNotFoundError(f"expected deployment file not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_compose_services(text: str) -> list[str]:
    """Extract top-level service names from a docker-compose YAML's `services:` block.

    Deliberately avoids a YAML parser: this is a light structural read, not a
    full config loader, so the module has zero extra dependencies.
    """
    lines = text.splitlines()
    services: list[str] = []
    in_services = False
    for line in lines:
        if re.match(r"^services:\s*$", line):
            in_services = True
            continue
        if in_services:
            if re.match(r"^\S", line):  # dedented back to top level -> block ended
                break
            match = re.match(r"^  (\w[\w-]*):\s*$", line)
            if match:
                services.append(match.group(1))
    return services


def extract_ci_python_versions(text: str) -> list[str]:
    """Extract the Python version matrix declared in the CI workflow."""
    match = re.search(r'python-version:\s*\[(.*?)\]', text)
    if not match:
        return []
    return [v.strip().strip('"') for v in match.group(1).split(",")]


def extract_ci_run_commands(text: str) -> list[str]:
    """Extract every `run:` command line from the CI workflow (in order)."""
    return [m.group(1).strip() for m in re.finditer(r"run:\s*(.+)", text)]


def build_readiness_report() -> list[ReadinessCheck]:
    """Validate the compose + CI shapes offline and describe local -> container -> pipeline."""
    checks: list[ReadinessCheck] = []

    compose_text = _read_text(COMPOSE_PATH)
    services = extract_compose_services(compose_text)
    checks.append(
        ReadinessCheck(
            "compose_defines_qdrant",
            "qdrant" in services,
            f"services found: {services}",
        )
    )
    checks.append(
        ReadinessCheck(
            "compose_defines_neo4j",
            "neo4j" in services,
            f"services found: {services}",
        )
    )

    ci_text = _read_text(CI_PATH)
    versions = extract_ci_python_versions(ci_text)
    checks.append(
        ReadinessCheck(
            "ci_declares_python_matrix",
            len(versions) >= 1,
            f"python-version matrix: {versions}",
        )
    )
    run_commands = extract_ci_run_commands(ci_text)
    checks.append(
        ReadinessCheck(
            "ci_runs_offline_pytest",
            any("pytest" in cmd for cmd in run_commands),
            f"run commands: {run_commands}",
        )
    )

    return checks


def print_deployment_map() -> None:
    """Print the local dev -> container -> pipeline mapping this module explains."""
    print("deployment map:")
    print("  local dev   -> `python src/NN_name/script.py` (offline, no services required)")
    print("  container   -> `docker compose up -d` starts optional Qdrant + Neo4j backends")
    print("  pipeline    -> `.github/workflows/ci.yml` runs `pytest` offline on every push/PR")


def main() -> None:
    print_deployment_map()

    checks = build_readiness_report()
    all_passed = True
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"[{status}] {check.name}: {check.detail}")
        logger.info("%s: %s (%s)", check.name, status, check.detail)
        all_passed = all_passed and check.passed

    if not all_passed:
        raise AssertionError("deployment readiness check failed — see FAIL lines above")

    print("=== MODULE 58: DEPLOYMENT COMPLETE ===")


if __name__ == "__main__":
    main()
