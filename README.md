# persist-workspace

A [Hermes Agent](https://hermes-agent.nousresearch.com) plugin that prevents
kanban task outputs from being silently deleted.

## Problem

By default, Hermes kanban tasks use a **scratch** workspace. When the task
completes, the scratch directory and everything in it is **deleted**. Any
research reports, generated code, inventory scans, or analysis produced by
the worker is lost unless the worker explicitly copied it elsewhere first.

This catches everyone eventually. Most task output matters.

## Solution

Registers a ``kanban_create_persist`` tool (in the ``kanban`` toolset) that
wraps the built-in ``kanban_create`` and injects:

- ``workspace_kind=dir`` — persistent on-completion
- ``workspace_path`` — resolved from the board's ``default_workdir``

The tool accepts all the same parameters as the built-in. When a caller
already provides explicit workspace values they are honoured; only the
default changes from ``scratch`` to ``dir``.

## Installation

```bash
# Clone into your user plugins directory
git clone https://github.com/vforge-labs/persist-workspace.git \
    ~/.hermes/plugins/persist-workspace

# Enable the plugin
hermes plugins enable persist-workspace
```

Or install directly from the repo:

```bash
pip install git+https://github.com/vforge-labs/persist-workspace.git
```

## Configuration

Set a board-level ``default_workdir`` so output lands somewhere predictable:

```bash
hermes kanban boards set-default-workdir default /home/me/data/kanban-output
```

Without this, the plugin falls back to ``~/.hermes/kanban/workspaces/persist/``.

## Usage

Once enabled, the model sees ``kanban_create_persist`` alongside the built-in
kanban tools. Use it the same way:

```python
kanban_create_persist(
    title="Research: my topic",
    assignee="researcher",
    body="investigate from all angles...",
)
```

The output survives task completion. When you need a throwaway scratch
workspace, use the built-in ``kanban_create`` with explicit
``workspace_kind="scratch"``.

## How it works

1. Tool handler checks if ``workspace_kind`` is unset or ``"scratch"``
2. If so, sets it to ``"dir"`` and resolves a workspace path from board
   metadata
3. Delegates to the built-in ``kanban_create`` via the tool registry
4. The task is created with a ``dir:`` workspace — preserved on completion

No core Hermes code is patched. The plugin lives entirely in user space.

## License

Apache 2.0
