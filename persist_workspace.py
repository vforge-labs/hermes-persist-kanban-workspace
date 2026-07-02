"""
persist-workspace plugin — implementation.

Resolves the board's default workspace path and wires the
``kanban_create_persist`` tool to the built-in ``kanban_create``
with ``workspace_kind=dir`` injected.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Board metadata helpers
# ---------------------------------------------------------------------------

DEFAULT_BOARD_DIR = Path.home() / ".hermes" / "kanban"
DEFAULT_BOARD_JSON = DEFAULT_BOARD_DIR / "board.json"


def get_default_workdir() -> str:
    """Read the active board's ``default_workdir``.

    Tries, in order:
    1. ``~/.hermes/kanban/board.json`` (legacy layout)
    2. ``~/.hermes/kanban/boards/default/board.json`` (multi-board layout)
    3. ``~/.hermes/kanban/workspaces/persist/`` (fallback)
    """
    candidates = [
        DEFAULT_BOARD_JSON,
        DEFAULT_BOARD_DIR / "boards" / "default" / "board.json",
    ]
    for path in candidates:
        try:
            meta = json.loads(path.read_text())
            dw = meta.get("default_workdir")
            if dw:
                resolved = Path(dw).expanduser().resolve()
                resolved.mkdir(parents=True, exist_ok=True)
                return str(resolved)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            continue

    fallback = DEFAULT_BOARD_DIR / "workspaces" / "persist"
    fallback.mkdir(parents=True, exist_ok=True)
    return str(fallback)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

KANBAN_CREATE_PERSIST_SCHEMA: dict = {
    "name": "kanban_create_persist",
    "description": (
        "Create a durable kanban task whose output is preserved on completion. "
        "Same as kanban_create but defaults to a persistent workspace (dir:) "
        "instead of scratch (which deletes output when the task completes). "
        "Use this for any task whose output you want to keep."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short task title (required).",
            },
            "assignee": {
                "type": "string",
                "description": "Profile name to execute this task.",
            },
            "body": {
                "type": "string",
                "description": "Full spec, acceptance criteria, links.",
            },
            "parents": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Parent task ids. Child stays 'todo' until all parents done.",
            },
            "priority": {
                "type": "integer",
                "description": "Dispatcher tiebreaker. Higher = picked sooner.",
            },
            "tenant": {
                "type": "string",
                "description": "Optional namespace for multi-project isolation.",
            },
            "workspace_path": {
                "type": "string",
                "description": (
                    "Explicit workspace path. If omitted, uses the "
                    "board's default_workdir (configurable via "
                    "``hermes kanban boards set-default-workdir``)."
                ),
            },
            "triage": {
                "type": "boolean",
                "description": (
                    "If true, task lands in 'triage' for a specifier "
                    "to flesh out the body before work starts."
                ),
            },
            "idempotency_key": {
                "type": "string",
                "description": (
                    "Dedup key — if a non-archived task with this key "
                    "exists, return it instead of creating a duplicate."
                ),
            },
            "max_runtime_seconds": {
                "type": "integer",
                "description": "Per-task runtime cap in seconds. Exceeded = SIGTERM + re-queue.",
            },
            "project": {
                "type": "string",
                "description": (
                    "Project id or slug to link the task to. "
                    "Creates a git worktree under the project's repo."
                ),
            },
            "goal_mode": {
                "type": "boolean",
                "description": (
                    "Run in a goal loop — an auxiliary judge checks "
                    "completion after each turn."
                ),
            },
            "goal_max_turns": {
                "type": "integer",
                "description": "Turn budget for goal_mode workers (default 20).",
            },
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Skill names to force-load into the dispatched worker.",
            },
            "board": {
                "type": "string",
                "description": "Kanban board slug to target. Omit for active board.",
            },
        },
        "required": ["title", "assignee"],
    },
}


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------


def handle_kanban_create_persist(params: dict, **kwargs) -> str:
    """Inject dir workspace, then delegate to the built-in kanban_create."""

    # Default to dir workspace unless explicitly set to something else
    wk = params.get("workspace_kind")
    if wk is None or wk == "scratch":
        params["workspace_kind"] = "dir"

    # Resolve workspace_path from board metadata when not specified
    if params.get("workspace_kind") == "dir" and not params.get("workspace_path"):
        params["workspace_path"] = get_default_workdir()

    # Dispatch to the built-in tool via the registry
    from tools.registry import registry

    return registry.dispatch("kanban_create", params, **kwargs)
