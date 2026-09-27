# Changelog

## [Unreleased]

### Changed
- **README's ctxpack captures refreshed for v0.1.14.**
  The captured output no longer lists the removed `qwen2.5` model alias, the
  tokens/map/pack sections are regenerated with the current tree, and the
  "Machine-readable output" section documents `version --json` and
  `models --csv`. The MCP tool table is updated to the seven-tool surface:
  `repo_map` grew `top`, `list_models` grew `vendor`/`top`/`sort`, and a
  `version` tool was added.

### Added
- `scripts/seed.py` creates the schema and loads starter rows.
- `scripts/export.py` writes every item to a JSON file.
- Makefile targets `seed` and `export` for the two scripts.

## [0.3.1] - 2026-09-22

### Added
- Cursor-based pagination on GET /items.

### Fixed
- PUT /items/{id} no longer accepts an empty sku.

## [0.3.0] - 2026-07-11

### Added
- POST /items and PATCH /items/{id}.
- Health endpoints at /healthz and /readyz.

## [0.2.0] - 2026-04-02

### Changed
- Migrated from Flask to FastAPI.
