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

Output captured from this project with ctxpack v0.1.4.

### tokens

```console
$ ctxpack tokens .
Path:       ctxpack-demo
Tokens:     ~39212
Bytes:      86.8 KB

Per-model fit (est. tokens / context window):
  [OVERFLOW] gpt-3.5-turbo          39.2k / 12.3k (319%)
  [OVERFLOW] gpt-4                  39.2k / 4.1k (957%)
  [fits] gpt-4-turbo            39.2k / 123.9k (32%)
  [fits] gpt-4o                 39.2k / 123.9k (32%)
  [fits] gpt-4o-mini            39.2k / 123.9k (32%)
  [fits] o1                     39.2k / 195.9k (20%)
  [fits] o3                     39.2k / 195.9k (20%)
  [fits] claude-3-haiku         39.2k / 195.9k (20%)
  [fits] claude-3-sonnet        39.2k / 195.9k (20%)
  [fits] claude-3-opus          39.2k / 195.9k (20%)
  [fits] claude-3.5-sonnet      39.2k / 195.9k (20%)
  [fits] claude-3.5-haiku       39.2k / 195.9k (20%)
  [fits] gemini-1.5-pro         39.2k / 2.0M (2%)
  [fits] gemini-1.5-flash       39.2k / 995.9k (4%)
  [fits] gemini-2.0-flash       39.2k / 1.0M (4%)
  [fits] llama-3.1-405b         39.2k / 123.9k (32%)
  [fits] mistral-large          39.2k / 123.9k (32%)
  [fits] deepseek-v3            39.2k / 123.9k (32%)
  [fits] qwen2.5                39.2k / 123.9k (32%)
```

Two small-window models overflow. Token counts are estimates, not real BPE
output.

### map

```console
$ ctxpack map .
Repository: ctxpack-demo
Files: ~39212 tokens, 86.8 KB

ctxpack-demo/  [39212t, 86.8KB]
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
  CHANGELOG.md  [252t, 546B]
  Dockerfile  [124t, 281B]
  LICENSE  [314t, 812B]
  Makefile  [121t, 286B]
  README.md  [2681t, 5.7KB]
  openapi.yaml  [1110t, 2.7KB]
  requirements.txt  [56t, 104B]
```

The data file alone is 66.8% of the tokens. `data/` would be the first thing to
cut.

### pack with a budget

This is the demo that matters. A 5000-token budget fits inside `gpt-4o`, and
the budget cuts the tree to 13 files:

```console
$ ctxpack pack . --model gpt-4o --format text --budget 5000
<!-- fit: FITS model=gpt-4o used=5.0k/123.9k (4%) FITS -->
Repository: ctxpack-demo
Files: 13 | Tokens: ~4973 | Bytes: 11.1 KB

==== CHANGELOG.md (252 tokens) ====
...
==== Dockerfile (124 tokens) ====
...
==== README.md (2681 tokens) ====
...

==== omitted by budget (12 files, ~34239 tokens) ====
- data/seed.json  (26178t)
- hello_service/routes/items.py  (1611t)
- tests/test_app.py  (1110t)
- openapi.yaml  (1110t)
- scripts/seed.py  (601t)
- hello_service/app.py  (643t)
- scripts/export.py  (579t)
- hello_service/db.py  (514t)
- tests/conftest.py  (372t)
- hello_service/models.py  (382t)
- hello_service/schemas/item.schema.json  (292t)
- docs/API.md  (847t)
```

The omitted list is the point of a budget: you see exactly what was cut and how
much it cost, instead of silently truncating mid-file. See
[Limitations](#limitations) for what the estimate is not.

## diff

`ctxpack diff <path>` packs only what `git status` reports as changed and
omits everything else, so you can ask a model about a working tree without
sending the whole repository. Supports `--ref` to compare against a git ref,
`--dry-run` to preview, `--model` for fit annotation, and all the standard
`--include`/`--exclude`/`--format`/`--output` flags.

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

It advertises `pack_repo`, `repo_map`, `count_tokens`, `list_models`, and
`diff_repo` on protocol `2024-11-05`. Since v0.1.6 every tool supports
`format: "json"` for machine-readable output, and `pack_repo`/`diff_repo`
accept a `model` argument to annotate fit for a named model. `diff_repo` also
accepts a `list` parameter to return changed file paths only. For Cursor or
Claude Desktop:

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

## Limitations

- Token counts are estimates (a tiktoken-style pre-tokenization plus a
  calibrated heuristic), not real BPE output. They are good for ranking and
  budget decisions, not for billing.
- Binary files are detected by null bytes and skipped with a token estimate
  from the file name only.
