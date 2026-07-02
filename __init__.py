"""
persist-workspace — Hermes plugin registration.

``kanban_create_persist`` wraps the built-in ``kanban_create`` so every
new task defaults to a persistent ``dir:`` workspace instead of the
ephemeral ``scratch`` (which deletes output on completion).
"""

from __future__ import annotations

import logging

from .persist_workspace import (
    KANBAN_CREATE_PERSIST_SCHEMA,
    handle_kanban_create_persist,
)

logger = logging.getLogger(__name__)

__all__ = ["register"]


def register(ctx) -> None:
    """Register the persistent kanban_create tool in the kanban toolset."""
    ctx.register_tool(
        name="kanban_create_persist",
        toolset="kanban",
        schema=KANBAN_CREATE_PERSIST_SCHEMA,
        handler=handle_kanban_create_persist,
        description=(
            "Create a durable kanban task whose output is preserved "
            "on completion (dir: instead of scratch)."
        ),
    )
    logger.info("persist-workspace: registered kanban_create_persist tool")
