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

Output captured from this project with ctxpack v0.1.2.

### tokens

```console
$ ctxpack tokens .
Path:       ctxpack-demo
Tokens:     ~35545
Bytes:      78.7 KB

Per-model fit (est. tokens / context window):
  [OVERFLOW] gpt-3.5-turbo          35.5k / 12.3k (289%)
  [OVERFLOW] gpt-4                  35.5k / 4.1k (868%)
  [fits] gpt-4-turbo            35.5k / 123.9k (29%)
  [fits] gpt-4o                 35.5k / 123.9k (29%)
  [fits] gpt-4o-mini            35.5k / 123.9k (29%)
  [fits] o1                     35.5k / 195.9k (18%)
  [fits] o3                     35.5k / 195.9k (18%)
  [fits] claude-3-haiku         35.5k / 195.9k (18%)
  [fits] claude-3-sonnet        35.5k / 195.9k (18%)
  [fits] claude-3-opus          35.5k / 195.9k (18%)
  [fits] claude-3.5-sonnet      35.5k / 195.9k (18%)
  [fits] claude-3.5-haiku       35.5k / 195.9k (18%)
  [fits] gemini-1.5-pro         35.5k / 2.0M (2%)
  [fits] gemini-1.5-flash       35.5k / 995.9k (4%)
  [fits] gemini-2.0-flash       35.5k / 1.0M (3%)
  [fits] llama-3.1-405b         35.5k / 123.9k (29%)
  [fits] mistral-large          35.5k / 123.9k (29%)
  [fits] deepseek-v3            35.5k / 123.9k (29%)
  [fits] qwen2.5                35.5k / 123.9k (29%)
```

Two small-window models overflow. Token counts are estimates, not real BPE
output.

### map

```console
$ ctxpack map .
Repository: ctxpack-demo
Files: ~35545 tokens, 78.7 KB

ctxpack-demo/  [35545t, 78.7KB]
  data/  [26178t, 56.9KB]
    seed.json  [26178t, 56.9KB]
  docs/  [1540t, 3.6KB]
    API.md  [849t, 1.9KB]
    ARCHITECTURE.md  [691t, 1.7KB]
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
  proto/  [327t, 803B]
    item.proto  [327t, 803B]
  tests/  [1475t, 3.4KB]
    __init__.py  [0t, 0B]
    conftest.py  [372t, 946B]
    test_app.py  [1103t, 2.5KB]
  CHANGELOG.md  [161t, 340B]
  Dockerfile  [124t, 281B]
  LICENSE  [314t, 812B]
  Makefile  [121t, 287B]
  openapi.yaml  [1110t, 2.7KB]
  pyproject.toml  [313t, 670B]
  requirements.txt  [56t, 104B]
```

The data file alone is 73.6% of the tokens. `data/` would be the first thing to
cut.

### pack with a budget

This is the demo that matters. A 5000-token budget fits inside `gpt-4o`, and
the budget cuts the tree to 16 files:

```console
$ ctxpack pack . --model gpt-4o --format text --budget 5000
<!-- fit: FITS model=gpt-4o used=4.9k/123.9k (4%) FITS -->
Repository: ctxpack-demo
Files: 16 | Tokens: ~4938 | Bytes: 11.8 KB

==== CHANGELOG.md (161 tokens) ====
...
==== docs/API.md (849 tokens) ====
...
==== hello_service/app.py (643 tokens) ====
...

==== omitted by budget (6 files, ~30607 tokens) ====
- data/seed.json  (26178t)
- hello_service/routes/items.py  (1611t)
- openapi.yaml  (1110t)
- hello_service/schemas/item.schema.json  (292t)
- tests/test_app.py  (1103t)
- pyproject.toml  (313t)
```

The omitted list is the point of a budget: you see exactly what was cut and how
much it cost, instead of silently truncating mid-file. See
[Limitations](#limitations) for what the estimate is not.

## diff

`ctxpack diff <path>` packs only what `git status` reports as changed and
omits everything else, so you can ask a model about a working tree without
sending the whole repository. It is covered in the main repository's test
suite.

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

It advertises `pack_repo`, `repo_map`, and `count_tokens` on protocol
`2024-11-05`. For Cursor or Claude Desktop:

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
- The captured output above was generated before the `scripts/` directory was
  added, so the current tree is 4 files larger than the numbers shown.
