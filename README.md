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

Output captured from this project with ctxpack v0.1.7.

### tokens

```console
$ ctxpack tokens .
Path:       ctxpack-demo
Tokens:     ~39482
Bytes:      87.3 KB

Per-model fit (est. tokens / context window):
  [fits] claude-3-haiku         39.5k / 195.9k (20%)
  [fits] claude-3-opus          39.5k / 195.9k (20%)
  [fits] claude-3-sonnet        39.5k / 195.9k (20%)
  [fits] claude-3.5-haiku       39.5k / 195.9k (20%)
  [fits] claude-3.5-sonnet      39.5k / 195.9k (20%)
  [fits] claude-3.7-sonnet      39.5k / 195.9k (20%)
  [fits] claude-4-opus          39.5k / 195.9k (20%)
  [fits] claude-4-sonnet        39.5k / 195.9k (20%)
  [fits] deepseek-r1            39.5k / 123.9k (32%)
  [fits] deepseek-v3            39.5k / 123.9k (32%)
  [fits] gemini-1.5-flash       39.5k / 995.9k (4%)
  [fits] gemini-1.5-pro         39.5k / 2.0M (2%)
  [fits] gemini-2.0-flash       39.5k / 1.0M (4%)
  [fits] gemini-2.5-flash       39.5k / 995.9k (4%)
  [fits] gemini-2.5-pro         39.5k / 2.0M (2%)
  [OVERFLOW] gpt-3.5-turbo          39.5k / 12.3k (321%)
  [OVERFLOW] gpt-4                  39.5k / 4.1k (964%)
  [fits] gpt-4-turbo            39.5k / 123.9k (32%)
  [fits] gpt-4.1                39.5k / 123.9k (32%)
  [fits] gpt-4o                 39.5k / 123.9k (32%)
  [fits] gpt-4o-mini            39.5k / 123.9k (32%)
  [fits] gpt-5                  39.5k / 195.9k (20%)
  [fits] llama-3.1-405b         39.5k / 123.9k (32%)
  [fits] llama-3.3-70b          39.5k / 123.9k (32%)
  [fits] mistral-large          39.5k / 123.9k (32%)
  [fits] mistral-large-2        39.5k / 123.9k (32%)
  [fits] o1                     39.5k / 195.9k (20%)
  [fits] o3                     39.5k / 195.9k (20%)
  [fits] o4-mini                39.5k / 195.9k (20%)
  [fits] qwen-2.5-72b           39.5k / 123.9k (32%)
  [fits] qwen2.5                39.5k / 123.9k (32%)
```

Two small-window models overflow. Token counts are estimates, not real BPE
output.

### map

```console
$ ctxpack map .
Repository: ctxpack-demo
Files: ~39482 tokens, 87.3 KB

ctxpack-demo/  [39482t, 87.3KB]
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
  README.md  [2951t, 6.2KB]
  openapi.yaml  [1110t, 2.7KB]
  requirements.txt  [56t, 104B]
```

The data file alone is 66.3% of the tokens. `data/` would be the first thing to
cut.

### pack with a budget

This is the demo that matters. A 5000-token budget fits inside `gpt-4o`, and
the budget cuts the tree to 11 files:

```console
$ ctxpack pack . --model gpt-4o --format text --budget 5000
<!-- fit: FITS model=gpt-4o used=5.0k/123.9k (4%) FITS -->
Repository: ctxpack-demo
Files: 11 | Tokens: ~4998 | Bytes: 11.1 KB

==== CHANGELOG.md (252 tokens) ====
...
==== LICENSE (314 tokens) ====
...
==== README.md (2951 tokens) ====
...

==== omitted by budget (14 files, ~34484 tokens) ====
Dockerfile
Makefile
data/seed.json
docs/API.md
hello_service/app.py
hello_service/db.py
hello_service/models.py
hello_service/routes/items.py
hello_service/schemas/item.schema.json
openapi.yaml
scripts/export.py
scripts/seed.py
tests/conftest.py
tests/test_app.py
```

The omitted list is the point of a budget: you see exactly what was cut and how
much it cost, instead of silently truncating mid-file. See
[Limitations](#limitations) for what the estimate is not.

## diff

`ctxpack diff <path>` packs only what `git status` reports as changed and
omits everything else, so you can ask a model about a working tree without
sending the whole repository. Supports `--ref` to compare against a git ref —
including a range such as `--ref HEAD~5..HEAD`, which compares two revisions
as history and never picks up working-tree files — `--dry-run` to preview,
`--list` to print only the changed paths for scripting, `--model` for fit
annotation, and all the standard `--include`/`--exclude`/`--format`/
`--output` flags. Files removed from the side being packed are reported by
name in a `Deleted` section; their content is gone, so there is nothing to
show, but a silent omission would make a deletion look like it never happened.

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
