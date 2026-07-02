"""
persist-workspace — Hermes plugin registration.

Derives its schema from the built-in ``kanban_create`` at registration time
so it stays in sync with the core tool automatically.
"""

from __future__ import annotations

import copy
import logging

from tools.kanban_tools import KANBAN_CREATE_SCHEMA
from .hermes_persist_kanban_workspace import handle_kanban_create_persist

logger = logging.getLogger(__name__)

__all__ = ["register"]


def register(ctx) -> None:
    """Register the persistent kanban_create tool in the kanban toolset.

    The schema is cloned from the built-in ``kanban_create`` and only the
    name/description are replaced — all parameters stay identical to core.
    """
    # Deep-copy the core schema so mutations don't leak
    schema = copy.deepcopy(KANBAN_CREATE_SCHEMA)

    # Override name and description to reflect the persistent variant
    schema["name"] = "kanban_create_persist"
    schema["description"] = (
        "Create a durable kanban task whose output is preserved on completion. "
        "Same as kanban_create but defaults to a persistent workspace (dir:) "
        "instead of scratch (which deletes output when the task completes). "
        "Use this for any task whose output you want to keep."
    )

    ctx.register_tool(
        name="kanban_create_persist",
        toolset="kanban",
        schema=schema,
        handler=handle_kanban_create_persist,
        description=(
            "Create a durable kanban task whose output is preserved "
            "on completion (dir: instead of scratch)."
        ),
    )
    logger.info("hermes-persist-kanban-workspace: registered kanban_create_persist tool")

