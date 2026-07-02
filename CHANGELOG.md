# Changelog

## [1.1.0] — 2026-07-02

### Changed
- **Override `kanban_create` directly** instead of providing a separate
  `kanban_create_persist` tool. The built-in `kanban_create` now defaults to
  a persistent `dir:` workspace; explicit `workspace_kind='scratch'` is still
  honoured for throwaway tasks.
- **Schema derived from core** — the tool schema is now cloned from the
  built-in `kanban_create` at registration time, eliminating schema drift.

### Fixed
- Stale `plugin.yaml` description updated to reflect the `kanban_create`
  override approach (was still describing the old `kanban_create_persist`
  separate-tool pattern).

## [1.0.0] — 2026-07-01

### Added
- Initial release — `kanban_create_persist` tool registered alongside the
  built-in `kanban_create`, defaulting workspaces to `dir:` instead of
  `scratch`.
