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
