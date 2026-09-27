# ctxpack-demo

A small FastAPI service ("hello-service", v0.3.1) used to demonstrate what
[ctxpack](https://github.com/la2278647-arch/ctxpack) produces on a real
project.

Get the tool from the main repository:

```sh
go install github.com/la2278647-arch/ctxpack@latest
# or download a release binary: https://github.com/la2278647-arch/ctxpack/releases
```

## The project

One table, five endpoints, cursor pagination, pydantic validation, and a test
per behaviour. Deliberately small so that every part is visible in under a
minute:

```text
hello_service/
  app.py              application factory, health and readiness probes
  config.py           pydantic-settings, cached
  db.py               lazy engine, session lifetime, commit and rollback
  models.py           the Item table
  routes/items.py     the five /items endpoints
  schemas/            JSON Schema for the response shape
tests/                one test per behaviour, in-memory SQLite
docs/                 architecture and API reference
proto/                the same shape for a future gRPC service
data/seed.json        220-row synthetic catalog, 58 KB
scripts/              developer helpers for the Makefile targets
```

Why the 58 KB catalog matters: a single generated data file dominates the tree,
which is exactly the situation a context budget has to handle.

## ctxpack on this repo

Output captured from this project with ctxpack v0.1.11, and reproduced
here from a fresh clone of this commit.

Line endings matter: the numbers below hold for an LF checkout -
macOS, Linux, or Windows with `core.autocrlf=false`. On a Windows CRLF
checkout every line gains a byte, which the counter counts, so the tree
reads larger and the 5000-token budget keeps one fewer file. This was
checked by cloning the commit both ways and comparing.

### tokens

```console
$ ctxpack tokens .
Path:       ctxpack-demo
Tokens:     ~51835
Bytes:      116.3 KB

Per-model fit (est. tokens / context window):
  [fits] claude-3-haiku         51.8k / 195.9k (26%)
  [fits] claude-3-opus          51.8k / 195.9k (26%)
  [fits] claude-3-sonnet        51.8k / 195.9k (26%)
  [fits] claude-3.5-haiku       51.8k / 195.9k (26%)
  [fits] claude-3.5-sonnet      51.8k / 195.9k (26%)
  [fits] claude-3.7-sonnet      51.8k / 195.9k (26%)
  [fits] claude-4-opus          51.8k / 195.9k (26%)
  [fits] claude-4-sonnet        51.8k / 195.9k (26%)
  [fits] deepseek-r1            51.8k / 123.9k (42%)
  [fits] deepseek-v3            51.8k / 123.9k (42%)
  [fits] gemini-1.5-flash       51.8k / 995.9k (5%)
  [fits] gemini-1.5-pro         51.8k / 2.0M (3%)
  [fits] gemini-2.0-flash       51.8k / 1.0M (5%)
  [fits] gemini-2.5-flash       51.8k / 995.9k (5%)
  [fits] gemini-2.5-pro         51.8k / 2.0M (3%)
  [OVERFLOW] gpt-3.5-turbo          51.8k / 12.3k (422%)
  [OVERFLOW] gpt-4                  51.8k / 4.1k (1266%)
  [fits] gpt-4-turbo            51.8k / 123.9k (42%)
  [fits] gpt-4.1                51.8k / 123.9k (42%)
  [fits] gpt-4o                 51.8k / 123.9k (42%)
  [fits] gpt-4o-mini            51.8k / 123.9k (42%)
  [fits] gpt-5                  51.8k / 195.9k (26%)
  [fits] llama-3.1-405b         51.8k / 123.9k (42%)
  [fits] llama-3.3-70b          51.8k / 123.9k (42%)
  [fits] mistral-large          51.8k / 123.9k (42%)
  [fits] mistral-large-2        51.8k / 123.9k (42%)
  [fits] o1                     51.8k / 195.9k (26%)
  [fits] o3                     51.8k / 195.9k (26%)
  [fits] o4-mini                51.8k / 195.9k (26%)
  [fits] qwen-2.5-72b           51.8k / 123.9k (42%)
```

Two small-window models overflow. Token counts are estimates, not real BPE
output.

### map

```console
$ ctxpack map .
Repository: ctxpack-demo
Files: ~51835 tokens, 116.3 KB

ctxpack-demo/  [51835t, 116.3KB]
  data/  [26178t, 56.9KB]
    seed.json  [26178t, 56.9KB]
  docs/  [1537t, 3.6KB]
    API.md  [847t, 1.9KB]
    ARCHITECTURE.md  [690t, 1.7KB]
  hello_service/  [3826t, 9.0KB]
    routes/  [1620t, 3.7KB]
      __init__.py  [9t, 22B]
      items.py  [1611t, 3.6KB]
    schemas/  [292t, 677B]
      item.schema.json  [292t, 677B]
    __init__.py  [37t, 82B]
    app.py  [643t, 1.6KB]
    config.py  [338t, 834B]
    db.py  [514t, 1.3KB]
    models.py  [382t, 900B]
  proto/  [327t, 804B]
    item.proto  [327t, 804B]
  scripts/  [1204t, 2.8KB]
    __init__.py  [24t, 60B]
    export.py  [579t, 1.3KB]
    seed.py  [601t, 1.4KB]
  tests/  [1482t, 3.4KB]
    __init__.py  [0t, 0B]
    conftest.py  [372t, 946B]
    test_app.py  [1110t, 2.5KB]
  CHANGELOG.md  [445t, 1008B]
  Dockerfile  [124t, 281B]
  LICENSE  [314t, 812B]
  Makefile  [121t, 286B]
  README.md  [15111t, 34.7KB]
  openapi.yaml  [1110t, 2.7KB]
  requirements.txt  [56t, 104B]
```

The data file alone is 62.1% of the tokens. `data/` would be the first thing to
cut.

### pack with a budget

This is the demo that matters. `gpt-4o` has a 123.9k-token context, and a
5000-token budget is a deliberate over-constraint - enough room for the
service core and the docs, not for the data:

```console
$ ctxpack pack . --model gpt-4o --format text --budget 5000 --exclude README.md
<!-- fit: FITS model=gpt-4o used=4.9k/123.9k (4%) FITS -->
Repository: ctxpack-demo
Files: 15 | Tokens: ~4934 | Bytes: 11.7 KB

==== CHANGELOG.md (445 tokens) ====
# Changelog

## [Unreleased]

### Changed
- **README's ctxpack captures refreshed for v0.1.11.**
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

==== LICENSE (314 tokens) ====
MIT License

Copyright (c) 2026 la2278647-arch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

==== docs/API.md (847 tokens) ====
# API

Base URL: `http://localhost:8000`

## GET /items

List items, newest first, with cursor pagination.

| Query   | Type   | Default | Notes                              |
| ------- | ------ | ------- | ---------------------------------- |
| limit   | int    | 50      | 1-200. Higher values raise 422.    |
| cursor  | string | -       | An item id; returns ids below it.  |

Response:

```json
{
  "items": [
    {
      "id": 3,
      "sku": "SKU-3",
      "name": "Gizmo",
      "price_cents": 1,
      "quantity": 0,
      "updated_at": "2026-09-22T12:18:03"
    }
  ],
  "next_cursor": "3"
}
```

`next_cursor` is null when the page is shorter than `limit`.

## POST /items

Create an item. Returns 201.

- `sku` is required, 1-64 characters, uppercase letters, digits and hyphens.
- `name` is required, 1-200 characters.
- `price_cents` is required, non-negative integer. Use cents, never floats.
- `quantity` defaults to 0 and must be non-negative.

A duplicate `sku` returns 409, not 500. Validation failures return 422.

## GET /items/{item_id}

Returns the item, or 404 if the id is unknown.

## PATCH /items/{item_id}

Partial update. Only keys present in the request body are written; absent keys
are left untouched. 404 for an unknown id.

## DELETE /items/{item_id}

Returns 204. Idempotent: deleting an unknown id also returns 204 so a retry is
safe.

## GET /healthz

Returns `{"status": "ok"}` with 200. Use for liveness probes only.

## GET /readyz

Returns `{"status": "ready"}` with 200, or `{"status": "not ready"}` with 503
if the database engine cannot be built.

## Errors

All errors use the shape `{"detail": "..."}`. Status codes:

| Code | Meaning                            |
| ---- | ---------------------------------- |
| 400  | A route raised ValueError          |
| 404  | The item does not exist            |
| 409  | A different item has the same sku  |
| 422  | Request body failed validation     |
| 503  | Readiness probe failed             |

==== docs/ARCHITECTURE.md (690 tokens) ====
# Architecture

## Shape

Three layers, each with one job:

- `hello_service.routes` owns HTTP: parsing requests, returning responses, and
  turning database errors into status codes. It never opens a database handle
  itself; it takes a session as a dependency.
- `hello_service.models` owns the schema: the `Item` table and its columns.
  Nothing else imports this module except the routes and the tests.
- `hello_service.db` owns connections: engine creation, session lifetimes, and
  commit and rollback behaviour. The engine is built lazily so that importing
  the package has no filesystem side effects.

Settings live in `hello_service.config`. They are cached because the database
engine is built once from them, and rebuilding the settings per request would
rebuild the engine per request.

## Request flow

A request for GET /items/{id} goes through FastAPI routing, which calls
`get_item` with a session yielded by `get_session`. The route issues one
`session.get`, serialises the row, and returns it. `get_session` commits on
success, rolls back on any exception, and always closes the session.

## Why this size

The service is deliberately small. It has one table, five endpoints, and no
background jobs, so a change to any part is visible in under a minute. The
points that are usually hard to reason about in a real service - dependency
injection, session lifetime, lazy engine creation, validation errors - are all
present and each has a test.

## Not solved here

- Authentication. There is none. Do not put this behind a public load balancer.
- Migrations. `Base.metadata.create_all` is a test aid; use Alembic for real
  databases.
- Rate limiting and caching. Both are deployment concerns.

==== hello_service/__init__.py (37 tokens) ====
"""hello_service: a tiny JSON API for inventory items."""

__version__ = "0.3.1"

==== hello_service/config.py (338 tokens) ====
"""Application settings, loaded from environment variables.

Values come from the process environment first, then a local .env file. The
.env file is never committed - see .env.example for the shape.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HELLO_SERVICE_", env_file=".env", extra="ignore")

    env: Literal["local", "staging", "production"] = "local"
    database_url: str = "sqlite:///./data/hello.sqlite3"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_page_size: int = 100


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings. Cached because the DB engine is built once."""
    return Settings()

==== hello_service/db.py (514 tokens) ====
"""Database session handling.

The engine is created lazily so importing the package never touches the
filesystem - tests can swap in an in-memory engine before the first request.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hello_service.config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_Session = None


def get_engine():
    """Build the engine on first use. Module-level so tests can reset it."""
    global _engine, _Session
    if _engine is None:
        _engine = create_engine(get_settings().database_url, echo=False)
        _Session = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def reset_engine() -> None:
    """Drop the cached engine. Used by tests between cases."""
    global _engine, _Session
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _Session = None


def get_session() -> Iterator[Session]:
    """Yield a session and close it, even if the request raised."""
    factory = _Session or sessionmaker(bind=get_engine())
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

==== hello_service/models.py (382 tokens) ====
"""SQLAlchemy models."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from hello_service.db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Item {self.sku} {self.price_cents}c x{self.quantity}>"

==== hello_service/routes/__init__.py (9 tokens) ====
"""Route modules."""

==== proto/item.proto (327 tokens) ====
syntax = "proto3";

package helloservice.v1;

option go_package = "hello-service/proto/helloservice/v1;v1";

// Item is the wire form of an inventory item. The JSON API and the gRPC
// service share this shape so clients do not need two models.
message Item {
  int32 id = 1;
  string sku = 2;
  string name = 3;
  int32 price_cents = 4;
  int32 quantity = 5;
}

// ListItemsRequest pages through items. cursor is the id of the last item
// returned by the previous page.
message ListItemsRequest {
  int32 limit = 1;
  string cursor = 2;
}

message ListItemsResponse {
  repeated Item items = 1;
  string next_cursor = 2;
}

message GetItemRequest {
  int32 id = 1;
}

service ItemService {
  rpc ListItems(ListItemsRequest) returns (ListItemsResponse);
  rpc GetItem(GetItemRequest) returns (Item);
}

==== requirements.txt (56 tokens) ====
fastapi==0.115.6
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
pydantic==2.10.4
pydantic-settings==2.7.0

==== scripts/__init__.py (24 tokens) ====
"""Package marker so `python -m scripts.seed` resolves."""

==== scripts/export.py (579 tokens) ====
"""Export every item to a JSON file.

Usage:
    python -m scripts.export --out data/exported.json
"""

import argparse
import json
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from hello_service.config import get_settings
from hello_service.models import Item


def export(out_path: Path) -> int:
    """Write all items as JSON and return the row count."""
    engine = create_engine(get_settings().database_url)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        rows = [
            {
                "id": i.id,
                "sku": i.sku,
                "name": i.name,
                "price_cents": i.price_cents,
                "quantity": i.quantity,
            }
            for i in session.scalars(select(Item)).all()
        ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return len(rows)


def main() -> None:
    """Parse flags and export."""
    parser = argparse.ArgumentParser(description="Export all items to JSON.")
    parser.add_argument("--out", default="data/exported.json", help="output path")
    args = parser.parse_args()
    n = export(Path(args.out))
    print(f"wrote {n} items to {args.out}")


if __name__ == "__main__":
    main()

==== tests/__init__.py (0 tokens) ====


==== tests/conftest.py (372 tokens) ====
"""Shared fixtures.

Everything points at an in-memory SQLite database so the suite never writes to
disk and runs in any order.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hello_service.app import create_app
from hello_service.db import Base, get_session


@pytest.fixture()
def client():
    """A client bound to a fresh in-memory database per test."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        s = TestSession()
        try:
            yield s
            s.commit()
        finally:
            s.close()

    app = create_app()
    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

==== omitted by budget (9 files, ~31790 tokens) ====
Dockerfile
Makefile
data/seed.json
hello_service/app.py
hello_service/routes/items.py
hello_service/schemas/item.schema.json
openapi.yaml
scripts/seed.py
tests/test_app.py

```

`next_cursor` is null when the page is shorter than `limit`.

## POST /items

Create an item. Returns 201.

- `sku` is required, 1-64 characters, uppercase letters, digits and hyphens.
- `name` is required, 1-200 characters.
- `price_cents` is required, non-negative integer. Use cents, never floats.
- `quantity` defaults to 0 and must be non-negative.

A duplicate `sku` returns 409, not 500. Validation failures return 422.

## GET /items/{item_id}

Returns the item, or 404 if the id is unknown.

## PATCH /items/{item_id}

Partial update. Only keys present in the request body are written; absent keys
are left untouched. 404 for an unknown id.

## DELETE /items/{item_id}

Returns 204. Idempotent: deleting an unknown id also returns 204 so a retry is
safe.

## GET /healthz

Returns `{"status": "ok"}` with 200. Use for liveness probes only.

## GET /readyz

Returns `{"status": "ready"}` with 200, or `{"status": "not ready"}` with 503
if the database engine cannot be built.

## Errors

All errors use the shape `{"detail": "..."}`. Status codes:

| Code | Meaning                            |
| ---- | ---------------------------------- |
| 400  | A route raised ValueError          |
| 404  | The item does not exist            |
| 409  | A different item has the same sku  |
| 422  | Request body failed validation     |
| 503  | Readiness probe failed             |

==== docs/ARCHITECTURE.md (690 tokens) ====
# Architecture

## Shape

Three layers, each with one job:

- `hello_service.routes` owns HTTP: parsing requests, returning responses, and
  turning database errors into status codes. It never opens a database handle
  itself; it takes a session as a dependency.
- `hello_service.models` owns the schema: the `Item` table and its columns.
  Nothing else imports this module except the routes and the tests.
- `hello_service.db` owns connections: engine creation, session lifetimes, and
  commit and rollback behaviour. The engine is built lazily so that importing
  the package has no filesystem side effects.

Settings live in `hello_service.config`. They are cached because the database
engine is built once from them, and rebuilding the settings per request would
rebuild the engine per request.

## Request flow

A request for GET /items/{id} goes through FastAPI routing, which calls
`get_item` with a session yielded by `get_session`. The route issues one
`session.get`, serialises the row, and returns it. `get_session` commits on
success, rolls back on any exception, and always closes the session.

## Why this size

The service is deliberately small. It has one table, five endpoints, and no
background jobs, so a change to any part is visible in under a minute. The
points that are usually hard to reason about in a real service - dependency
injection, session lifetime, lazy engine creation, validation errors - are all
present and each has a test.

## Not solved here

- Authentication. There is none. Do not put this behind a public load balancer.
- Migrations. `Base.metadata.create_all` is a test aid; use Alembic for real
  databases.
- Rate limiting and caching. Both are deployment concerns.

==== hello_service/__init__.py (37 tokens) ====
"""hello_service: a tiny JSON API for inventory items."""

__version__ = "0.3.1"

==== hello_service/config.py (338 tokens) ====
"""Application settings, loaded from environment variables.

Values come from the process environment first, then a local .env file. The
.env file is never committed - see .env.example for the shape.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HELLO_SERVICE_", env_file=".env", extra="ignore")

    env: Literal["local", "staging", "production"] = "local"
    database_url: str = "sqlite:///./data/hello.sqlite3"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_page_size: int = 100


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings. Cached because the DB engine is built once."""
    return Settings()

==== hello_service/db.py (514 tokens) ====
"""Database session handling.

The engine is created lazily so importing the package never touches the
filesystem - tests can swap in an in-memory engine before the first request.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hello_service.config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_Session = None


def get_engine():
    """Build the engine on first use. Module-level so tests can reset it."""
    global _engine, _Session
    if _engine is None:
        _engine = create_engine(get_settings().database_url, echo=False)
        _Session = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def reset_engine() -> None:
    """Drop the cached engine. Used by tests between cases."""
    global _engine, _Session
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _Session = None


def get_session() -> Iterator[Session]:
    """Yield a session and close it, even if the request raised."""
    factory = _Session or sessionmaker(bind=get_engine())
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

==== hello_service/models.py (382 tokens) ====
"""SQLAlchemy models."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from hello_service.db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Item {self.sku} {self.price_cents}c x{self.quantity}>"

==== hello_service/routes/__init__.py (9 tokens) ====
"""Route modules."""

==== proto/item.proto (327 tokens) ====
syntax = "proto3";

package helloservice.v1;

option go_package = "hello-service/proto/helloservice/v1;v1";

// Item is the wire form of an inventory item. The JSON API and the gRPC
// service share this shape so clients do not need two models.
message Item {
  int32 id = 1;
  string sku = 2;
  string name = 3;
  int32 price_cents = 4;
  int32 quantity = 5;
}

// ListItemsRequest pages through items. cursor is the id of the last item
// returned by the previous page.
message ListItemsRequest {
  int32 limit = 1;
  string cursor = 2;
}

message ListItemsResponse {
  repeated Item items = 1;
  string next_cursor = 2;
}

message GetItemRequest {
  int32 id = 1;
}

service ItemService {
  rpc ListItems(ListItemsRequest) returns (ListItemsResponse);
  rpc GetItem(GetItemRequest) returns (Item);
}

==== requirements.txt (56 tokens) ====
fastapi==0.115.6
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
pydantic==2.10.4
pydantic-settings==2.7.0

==== scripts/__init__.py (24 tokens) ====
"""Package marker so `python -m scripts.seed` resolves."""

==== scripts/export.py (579 tokens) ====
"""Export every item to a JSON file.

Usage:
    python -m scripts.export --out data/exported.json
"""

import argparse
import json
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from hello_service.config import get_settings
from hello_service.models import Item


def export(out_path: Path) -> int:
    """Write all items as JSON and return the row count."""
    engine = create_engine(get_settings().database_url)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        rows = [
            {
                "id": i.id,
                "sku": i.sku,
                "name": i.name,
                "price_cents": i.price_cents,
                "quantity": i.quantity,
            }
            for i in session.scalars(select(Item)).all()
        ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return len(rows)


def main() -> None:
    """Parse flags and export."""
    parser = argparse.ArgumentParser(description="Export all items to JSON.")
    parser.add_argument("--out", default="data/exported.json", help="output path")
    args = parser.parse_args()
    n = export(Path(args.out))
    print(f"wrote {n} items to {args.out}")


if __name__ == "__main__":
    main()

==== tests/__init__.py (0 tokens) ====


==== tests/conftest.py (372 tokens) ====
"""Shared fixtures.

Everything points at an in-memory SQLite database so the suite never writes to
disk and runs in any order.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hello_service.app import create_app
from hello_service.db import Base, get_session


@pytest.fixture()
def client():
    """A client bound to a fresh in-memory database per test."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        s = TestSession()
        try:
            yield s
            s.commit()
        finally:
            s.close()

    app = create_app()
    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

==== omitted by budget (7 files, ~31545 tokens) ====
data/seed.json
hello_service/app.py
hello_service/routes/items.py
hello_service/schemas/item.schema.json
openapi.yaml
scripts/seed.py
tests/test_app.py

```

`next_cursor` is null when the page is shorter than `limit`.

## POST /items

Create an item. Returns 201.

- `sku` is required, 1-64 characters, uppercase letters, digits and hyphens.
- `name` is required, 1-200 characters.
- `price_cents` is required, non-negative integer. Use cents, never floats.
- `quantity` defaults to 0 and must be non-negative.

A duplicate `sku` returns 409, not 500. Validation failures return 422.

## GET /items/{item_id}

Returns the item, or 404 if the id is unknown.

## PATCH /items/{item_id}

Partial update. Only keys present in the request body are written; absent keys
are left untouched. 404 for an unknown id.

## DELETE /items/{item_id}

Returns 204. Idempotent: deleting an unknown id also returns 204 so a retry is
safe.

## GET /healthz

Returns `{"status": "ok"}` with 200. Use for liveness probes only.

## GET /readyz

Returns `{"status": "ready"}` with 200, or `{"status": "not ready"}` with 503
if the database engine cannot be built.

## Errors

All errors use the shape `{"detail": "..."}`. Status codes:

| Code | Meaning                            |
| ---- | ---------------------------------- |
| 400  | A route raised ValueError          |
| 404  | The item does not exist            |
| 409  | A different item has the same sku  |
| 422  | Request body failed validation     |
| 503  | Readiness probe failed             |

==== docs/ARCHITECTURE.md (690 tokens) ====
# Architecture

## Shape

Three layers, each with one job:

- `hello_service.routes` owns HTTP: parsing requests, returning responses, and
  turning database errors into status codes. It never opens a database handle
  itself; it takes a session as a dependency.
- `hello_service.models` owns the schema: the `Item` table and its columns.
  Nothing else imports this module except the routes and the tests.
- `hello_service.db` owns connections: engine creation, session lifetimes, and
  commit and rollback behaviour. The engine is built lazily so that importing
  the package has no filesystem side effects.

Settings live in `hello_service.config`. They are cached because the database
engine is built once from them, and rebuilding the settings per request would
rebuild the engine per request.

## Request flow

A request for GET /items/{id} goes through FastAPI routing, which calls
`get_item` with a session yielded by `get_session`. The route issues one
`session.get`, serialises the row, and returns it. `get_session` commits on
success, rolls back on any exception, and always closes the session.

## Why this size

The service is deliberately small. It has one table, five endpoints, and no
background jobs, so a change to any part is visible in under a minute. The
points that are usually hard to reason about in a real service - dependency
injection, session lifetime, lazy engine creation, validation errors - are all
present and each has a test.

## Not solved here

- Authentication. There is none. Do not put this behind a public load balancer.
- Migrations. `Base.metadata.create_all` is a test aid; use Alembic for real
  databases.
- Rate limiting and caching. Both are deployment concerns.

==== hello_service/__init__.py (37 tokens) ====
"""hello_service: a tiny JSON API for inventory items."""

__version__ = "0.3.1"

==== hello_service/config.py (338 tokens) ====
"""Application settings, loaded from environment variables.

Values come from the process environment first, then a local .env file. The
.env file is never committed - see .env.example for the shape.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HELLO_SERVICE_", env_file=".env", extra="ignore")

    env: Literal["local", "staging", "production"] = "local"
    database_url: str = "sqlite:///./data/hello.sqlite3"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_page_size: int = 100


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings. Cached because the DB engine is built once."""
    return Settings()

==== hello_service/db.py (514 tokens) ====
"""Database session handling.

The engine is created lazily so importing the package never touches the
filesystem - tests can swap in an in-memory engine before the first request.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hello_service.config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_Session = None


def get_engine():
    """Build the engine on first use. Module-level so tests can reset it."""
    global _engine, _Session
    if _engine is None:
        _engine = create_engine(get_settings().database_url, echo=False)
        _Session = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def reset_engine() -> None:
    """Drop the cached engine. Used by tests between cases."""
    global _engine, _Session
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _Session = None


def get_session() -> Iterator[Session]:
    """Yield a session and close it, even if the request raised."""
    factory = _Session or sessionmaker(bind=get_engine())
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

==== hello_service/models.py (382 tokens) ====
"""SQLAlchemy models."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from hello_service.db import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Item {self.sku} {self.price_cents}c x{self.quantity}>"

==== hello_service/routes/__init__.py (9 tokens) ====
"""Route modules."""

==== proto/item.proto (327 tokens) ====
syntax = "proto3";

package helloservice.v1;

option go_package = "hello-service/proto/helloservice/v1;v1";

// Item is the wire form of an inventory item. The JSON API and the gRPC
// service share this shape so clients do not need two models.
message Item {
  int32 id = 1;
  string sku = 2;
  string name = 3;
  int32 price_cents = 4;
  int32 quantity = 5;
}

// ListItemsRequest pages through items. cursor is the id of the last item
// returned by the previous page.
message ListItemsRequest {
  int32 limit = 1;
  string cursor = 2;
}

message ListItemsResponse {
  repeated Item items = 1;
  string next_cursor = 2;
}

message GetItemRequest {
  int32 id = 1;
}

service ItemService {
  rpc ListItems(ListItemsRequest) returns (ListItemsResponse);
  rpc GetItem(GetItemRequest) returns (Item);
}

==== requirements.txt (56 tokens) ====
fastapi==0.115.6
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
pydantic==2.10.4
pydantic-settings==2.7.0

==== scripts/__init__.py (24 tokens) ====
"""Package marker so `python -m scripts.seed` resolves."""

==== scripts/export.py (579 tokens) ====
"""Export every item to a JSON file.

Usage:
    python -m scripts.export --out data/exported.json
"""

import argparse
import json
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from hello_service.config import get_settings
from hello_service.models import Item


def export(out_path: Path) -> int:
    """Write all items as JSON and return the row count."""
    engine = create_engine(get_settings().database_url)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        rows = [
            {
                "id": i.id,
                "sku": i.sku,
                "name": i.name,
                "price_cents": i.price_cents,
                "quantity": i.quantity,
            }
            for i in session.scalars(select(Item)).all()
        ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return len(rows)


def main() -> None:
    """Parse flags and export."""
    parser = argparse.ArgumentParser(description="Export all items to JSON.")
    parser.add_argument("--out", default="data/exported.json", help="output path")
    args = parser.parse_args()
    n = export(Path(args.out))
    print(f"wrote {n} items to {args.out}")


if __name__ == "__main__":
    main()

==== tests/__init__.py (0 tokens) ====


==== tests/conftest.py (372 tokens) ====
"""Shared fixtures.

Everything points at an in-memory SQLite database so the suite never writes to
disk and runs in any order.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hello_service.app import create_app
from hello_service.db import Base, get_session


@pytest.fixture()
def client():
    """A client bound to a fresh in-memory database per test."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        s = TestSession()
        try:
            yield s
            s.commit()
        finally:
            s.close()

    app = create_app()
    app.dependency_overrides[get_session] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

==== omitted by budget (7 files, ~31545 tokens) ====
data/seed.json
hello_service/app.py
hello_service/routes/items.py
hello_service/schemas/item.schema.json
openapi.yaml
scripts/seed.py
tests/test_app.py

```

17 files make the cut: the policy and build files, both design
docs, the data layer (`config.py`, `db.py`, `models.py`), the
schema stub, and the test scaffolding. Seven go out, led by
`data/seed.json` at 26.2k tokens and then the three files above
a thousand - `hello_service/routes/items.py`, `tests/test_app.py`,
and the `openapi.yaml` that duplicates the proto.

The README is excluded because it is the document that holds this output.
Without the flag it would take more than three quarters of the 5000-token
budget on its own, and the capture would not reproduce: the more output it
shows, the larger the file, the fewer files fit.

`--format` switches between `text`, `xml`, `markdown` and `json`; `text` is
shown above and `xml` is the default. See [Limitations](#limitations) for
what the estimate is not.

### doctor

`doctor` prints what the binary is and what the host looks like. It is the one
place the build information surfaces, and the first thing to run when a `pack`
result looks wrong.

```console
$ ctxpack doctor
ctxpack diagnostics:
  Version:   ctxpack 0.1.10 (windows/amd64, go1.26.5, commit 8b8106d, built 2026-09-26T12:01:35Z)
  Go:        go1.26.5
  Platform:  windows/amd64
  Git:       C:\Program Files\Git\mingw64\bin\git.exe (git version 2.55.0.windows.3)
  Models:    31 models, 7 vendors
  Vendor breakdown:
    openai          10 model(s)
    anthropic       8 model(s)
    google          5 model(s)
    alibaba         2 model(s)
    deepseek        2 model(s)
    meta            2 model(s)
    mistral         2 model(s)
```

## diff

`ctxpack diff <path>` packs only what git reports as changed and leaves the rest
out, so you can ask a model about a working tree without sending the whole
repository. With no flags the base is the index, so uncommitted edits are what
get packed.

The run below came from two uncommitted edits - one setting and one column for a
low-stock feature - totalling 793 tokens out of this 42k-token tree:

```console
$ ctxpack diff . --dry-run
dry run vs "WORKTREE": 2 files, ~793 tokens, 1.9 KB
  hello_service/config.py (~370 tokens, 909 B)
  hello_service/models.py (~423 tokens, 996 B)

$ ctxpack diff . --model gpt-4o
<!-- ctxpack diff vs "WORKTREE": 2 files -->
<!-- fit: FITS model=gpt-4o used=793/123.9k (1%) FITS -->
<repository>
  <meta>
    <root>ctxpack-demo</root>
    <fileCount>2</fileCount>
    <totalTokens>793</totalTokens>
    <totalBytes>1905</totalBytes>
    <skipped>0</skipped>
  </meta>
  <files>
    <file path="hello_service/config.py" tokens="370" bytes="909">
      <content><![CDATA[...]]></content>
    </file>
    <file path="hello_service/models.py" tokens="423" bytes="996">
      <content><![CDATA[...]]></content>
    </file>
  </files>
</repository>
```

The output is XML, so it parses instead of needing to be scraped. `--list`
prints just the paths, which is what a pre-commit hook or a CI check wants:

```console
$ ctxpack diff . --list
hello_service/config.py
hello_service/models.py
```

`--ref` compares two revisions instead of the working tree - a range such
as `--ref HEAD~5..HEAD` reads history and never picks up uncommitted files:

```console
$ ctxpack diff . --ref HEAD~1..HEAD --list
README.md
```

Files removed from the side being packed are counted in a `<deleted>`
element and named there. Their content is gone, so there is nothing to show,
but a silent omission would make a deletion look like it never happened.
`--include`, `--exclude`, `--format` and `--output` behave as they do for
`pack`.

## Running the service

```sh
pip install -r requirements.txt
make seed      # create the schema and load starter rows
make run       # uvicorn on :8000
make test      # pytest against in-memory SQLite
```

## MCP server

ctxpack also runs as a Model Context Protocol server over stdio:

```sh
ctxpack mcp
```

It speaks JSON-RPC 2.0 with newline-delimited messages and advertises seven
tools on protocol `2024-11-05`, identifying itself as `ctxpack 0.1.11`:

| tool | required | optional |
| --- | --- | --- |
| `pack_repo` | `path` | `budget`, `exclude`, `format`, `hidden`, `include`, `max_depth`, `max_size`, `model`, `no_gitignore` |
| `repo_map` | `path` | `exclude`, `format`, `include`, `max_depth`, `max_size`, `sort`, `top` |
| `count_tokens` | `path` | `exclude`, `format`, `hidden`, `include`, `max_depth`, `max_size`, `model`, `no_gitignore`, `sort`, `top` |
| `list_models` | - | `format`, `sort`, `top`, `vendor` |
| `diff_repo` | `path` | `budget`, `exclude`, `format`, `hidden`, `include`, `list`, `max_depth`, `max_size`, `model`, `no_gitignore`, `ref` |
| `doctor` | - | `format`, `top` |
| `version` | - | `format` |

Every tool takes `format: "json"` for machine-readable output, and
`pack_repo`/`diff_repo` take `model` to annotate fit for a named model.
For Cursor or Claude Desktop:

```json
{
  "mcpServers": {
    "ctxpack": {
      "command": "ctxpack",
      "args": ["mcp"]
    }
  }
}
```

## Machine-readable output

Every command has a JSON mode, and the two lookup tables also have CSV
modes, so a script can consume them without parsing prose:

```console
$ ctxpack version --json
{"name":"ctxpack","version":"0.1.11","os":"windows","arch":"amd64","go":"go1.26.5","commit":"dev","built":"unknown"}
$ ctxpack models --csv | head -4
name,context_window,vendor
claude-3-haiku,200000,anthropic
claude-3-opus,200000,anthropic
claude-3-sonnet,200000,anthropic
```

`tokens --csv` emits `model,used,limit,fits,pct_used`, the same field names as
`tokens --json`, so a consumer can switch formats without changing its schema.

## Limitations

- Token counts are estimates - a tiktoken-style pre-tokenization plus a
  calibrated heuristic - not real BPE output. They are good for ranking and
  budget decisions, not for billing.
- `pack` is greedy in priority order, not an optimal knapsack. Policy and
  entry-point files are kept first, so a large low-priority file can be dropped
  while smaller files still fit: in the run above `docs/API.md` (847 tokens) is
  kept while `hello_service/routes/items.py` (1611 tokens) is not.
- A file is accepted before it is counted. `.gitignore` is respected, and a
  built-in denylist drops common generated and binary files outright -
  `node_modules`, `dist`, `*.png`, `*.zip`, `go.sum`, `package-lock.json`, and
  more. Files that survive the filters but smell binary, a NUL byte in the
  first 8 KiB, are still listed and packed as a marker with no content, costing
  only the tokens their path takes.
- `diff` reports what git reports. Untracked files count as changed, which is
  usually what you want; if you do not want them in the bundle, commit or
  ignore them first.
- The model table is a hand-maintained snapshot of public context windows -
  30 models across 7 vendors here. It can lag a vendor's release, and `--model`
  accepts any name, so a fit number for an unlisted model is only as good as the
  nearest entry.
- Nothing here reads a model or calls an API. ctxpack is offline: the numbers
  are a prediction of what a prompt would cost, not a measurement of one.

