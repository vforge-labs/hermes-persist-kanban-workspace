"""
persist-workspace — Hermes plugin registration.

Overrides the built-in ``kanban_create`` tool so every new task defaults to
a persistent ``dir:`` workspace instead of the ephemeral ``scratch``
(which deletes output on completion).

The schema is derived from the core tool at registration time. Explicit
``workspace_kind="scratch"`` is still honoured for throwaway tasks.
"""

from __future__ import annotations

import copy
import logging

from tools.kanban_tools import KANBAN_CREATE_SCHEMA
from tools.registry import registry

logger = logging.getLogger(__name__)

__all__ = ["register"]

# Save a reference to the original built-in handler BEFORE we override it.
# This lets our handler delegate to the original without infinite recursion.
_ORIG_KANBAN_CREATE_HANDLER = None


def register(ctx) -> None:
    """Override ``kanban_create`` with a persistent default workspace.

    The schema is cloned from the built-in ``kanban_create`` — only the
    description changes to document the new default behaviour. The original
    handler is saved and called after injecting ``workspace_kind=dir``.
    """
    global _ORIG_KANBAN_CREATE_HANDLER

    # Capture original before override
    orig = registry.get_entry("kanban_create")
    if orig is None:
        logger.warning(
            "kanban_create not yet registered — cannot override. "
            "Will retry via post-init hook."
        )
        return
    _ORIG_KANBAN_CREATE_HANDLER = orig.handler

    # Deep-copy core schema, override description
    schema = copy.deepcopy(KANBAN_CREATE_SCHEMA)
    schema["description"] = (
        "Create a new kanban task (default: persistent dir: workspace). "
        "Same API as kanban_create but defaults to workspace_kind='dir' "
        "instead of 'scratch' (which deletes output on completion). "
        "Pass workspace_kind='scratch' explicitly for a throwaway task."
    )

    ctx.register_tool(
        name="kanban_create",
        toolset="kanban",
        schema=schema,
        handler=_wrapped_handler,
        override=True,
        description=(
            "Create a kanban task with a persistent workspace (dir:) by default. "
            "Explicit workspace_kind='scratch' is honoured."
        ),
    )
    logger.info(
        "hermes-persist-kanban-workspace: overrode kanban_create — "
        "dir: workspace by default, explicit scratch honoured"
    )


def _wrapped_handler(params: dict, **kwargs) -> str:
    """Wrap the original kanban_create handler with dir injection."""
    if _ORIG_KANBAN_CREATE_HANDLER is None:
        logger.error("Original kanban_create handler not captured — cannot dispatch.")
        return '{"error": "kanban_create override misconfigured: original handler lost"}'

    # Only inject dir when workspace_kind is unset — explicit "scratch" honoured
    if params.get("workspace_kind") is None:
        params["workspace_kind"] = "dir"

    # Resolve workspace_path from board metadata when not specified
    if params.get("workspace_kind") == "dir" and not params.get("workspace_path"):
        from .hermes_persist_kanban_workspace import get_default_workdir

        params["workspace_path"] = get_default_workdir()

    return _ORIG_KANBAN_CREATE_HANDLER(params, **kwargs)
