"""Small, consistent logging helper shared across modules.

Exercises print human-readable learning output, but the reusable library code
logs through here so behaviour is uniform and the level is controllable via the
``LOG_LEVEL`` environment variable.
"""

from __future__ import annotations

import logging

from src.shared.config import get_settings

_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger with a single, idempotent stream handler."""
    global _CONFIGURED
    if not _CONFIGURED:
        logging.basicConfig(
            level=get_settings().log_level,
            format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        _CONFIGURED = True
    return logging.getLogger(name)
