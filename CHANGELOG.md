# Changelog

## [Unreleased]

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
