# hermes-persist-kanban-workspace

A [Hermes Agent](https://hermes-agent.nousresearch.com) plugin that prevents
kanban task outputs from being silently deleted.

## Problem

By default, Hermes kanban tasks use a **scratch** workspace. When the task
completes, the scratch directory and everything in it is **deleted**. Any
research reports, generated code, inventory scans, or analysis produced by
the worker is lost unless the worker explicitly copied it elsewhere first.

This catches everyone eventually. Most task output matters.

## Solution

Overrides the built-in ``kanban_create`` tool to default to a persistent
``dir:`` workspace. When a caller already provides explicit ``workspace_kind``
or ``workspace_path`` they are honoured; only the default changes from
``scratch`` to ``dir``.

The tool schema is cloned from the core tool at registration time, so it
always stays in sync — no drift, no manual updates.

## Installation

```bash
# Clone into your user plugins directory
git clone https://github.com/vforge-labs/hermes-persist-kanban-workspace.git \
    ~/.hermes/plugins/hermes-persist-kanban-workspace

# Enable the plugin
hermes plugins enable hermes-persist-kanban-workspace
```

Or install directly from the repo:

```bash
pip install git+https://github.com/vforge-labs/hermes-persist-kanban-workspace.git
```

**After enabling or updating the plugin, restart the Hermes dashboard and
gateway so the override is picked up:**

```bash
systemctl --user restart hermes-dashboard hermes-gateway
```

## Configuration

Set a board-level ``default_workdir`` so output lands somewhere predictable:

```bash
hermes kanban boards set-default-workdir default /home/me/data/kanban-output
```

Without this, the plugin falls back to ``~/.hermes/kanban/workspaces/persist/``.

## Usage

Once enabled and restarted, every call to ``kanban_create`` defaults to
a persistent workspace with no extra effort:

```python
kanban_create(
    title="Research: my topic",
    assignee="researcher",
    body="investigate from all angles...",
)
# → workspace_kind: "dir", workspace_path: <default_workdir>
```

Output survives task completion. When you need a throwaway scratch workspace,
pass it explicitly:

```python
kanban_create(
    title="Quick exploration",
    assignee="default",
    workspace_kind="scratch",
)
```

## How it works

1. On plugin load, the original ``kanban_create`` handler is captured
2. A new handler is registered under the same name with ``override=True``
3. The new handler checks if ``workspace_kind`` is unset — if so, injects
   ``"dir"`` and resolves a path from board metadata
4. Delegates to the original handler via the saved reference
5. The task is created with a ``dir:`` workspace — preserved on completion

No core Hermes code is patched. The plugin lives entirely in user space.

## Compatibility

Requires Hermes Agent 0.9+ (uses the ``override`` flag on
``ctx.register_tool``, introduced in 0.9.x).

## License

Apache 2.0
