"""
persist-workspace plugin — board metadata resolution.

Provides ``get_default_workdir()`` used by the override handler in
``__init__.py`` to resolve a persistent workspace path.
"""

from __future__ import annotations

import json
from pathlib import Path

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
