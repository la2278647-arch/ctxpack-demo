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

Output captured from this project with ctxpack v0.1.10.

### tokens

```console
$ ctxpack tokens .
Path:       ctxpack-demo
Tokens:     ~42028
Bytes:      93.1 KB

Per-model fit (est. tokens / context window):
  [fits] claude-3-haiku         42.0k / 195.9k (21%)
  [fits] claude-3-opus          42.0k / 195.9k (21%)
  [fits] claude-3-sonnet        42.0k / 195.9k (21%)
  [fits] claude-3.5-haiku       42.0k / 195.9k (21%)
  [fits] claude-3.5-sonnet      42.0k / 195.9k (21%)
  [fits] claude-3.7-sonnet      42.0k / 195.9k (21%)
  [fits] claude-4-opus          42.0k / 195.9k (21%)
  [fits] claude-4-sonnet        42.0k / 195.9k (21%)
  [fits] deepseek-r1            42.0k / 123.9k (34%)
  [fits] deepseek-v3            42.0k / 123.9k (34%)
  [fits] gemini-1.5-flash       42.0k / 995.9k (4%)
  [fits] gemini-1.5-pro         42.0k / 2.0M (2%)
  [fits] gemini-2.0-flash       42.0k / 1.0M (4%)
  [fits] gemini-2.5-flash       42.0k / 995.9k (4%)
  [fits] gemini-2.5-pro         42.0k / 2.0M (2%)
  [OVERFLOW] gpt-3.5-turbo          42.0k / 12.3k (342%)
  [OVERFLOW] gpt-4                  42.0k / 4.1k (1026%)
  [fits] gpt-4-turbo            42.0k / 123.9k (34%)
  [fits] gpt-4.1                42.0k / 123.9k (34%)
  [fits] gpt-4o                 42.0k / 123.9k (34%)
  [fits] gpt-4o-mini            42.0k / 123.9k (34%)
  [fits] gpt-5                  42.0k / 195.9k (21%)
  [fits] llama-3.1-405b         42.0k / 123.9k (34%)
  [fits] llama-3.3-70b          42.0k / 123.9k (34%)
  [fits] mistral-large          42.0k / 123.9k (34%)
  [fits] mistral-large-2        42.0k / 123.9k (34%)
  [fits] o1                     42.0k / 195.9k (21%)
  [fits] o3                     42.0k / 195.9k (21%)
  [fits] o4-mini                42.0k / 195.9k (21%)
  [fits] qwen-2.5-72b           42.0k / 123.9k (34%)
  [fits] qwen2.5                42.0k / 123.9k (34%)
```

Two small-window models overflow. Token counts are estimates, not real BPE
output.

### map

```console
$ ctxpack map .
Repository: ctxpack-demo
Files: ~42028 tokens, 93.1 KB

ctxpack-demo/  [42028t, 93.1KB]
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
  README.md  [5497t, 12.0KB]
  openapi.yaml  [1110t, 2.7KB]
  requirements.txt  [56t, 104B]
```

The data file alone is 62.3% of the tokens. `data/` would be the first thing to
cut.

### pack with a budget

This is the demo that matters. `gpt-4o` has a 123.9k-token context, and a
5000-token budget is a deliberate over-constraint - enough room for the
service core and the docs, not for the data:

```console
$ ctxpack pack . --model gpt-4o --format text --budget 5000 --exclude README.md
<!-- fit: FITS model=gpt-4o used=5.0k/123.9k (4%) FITS -->
Repository: ctxpack-demo
Files: 17 | Tokens: ~4986 | Bytes: 11.8 KB

==== CHANGELOG.md (252 tokens) ====
...
==== Dockerfile (124 tokens) ====
...
==== LICENSE (314 tokens) ====
...
==== Makefile (121 tokens) ====
...
==== docs/API.md (847 tokens) ====
...
==== docs/ARCHITECTURE.md (690 tokens) ====
...
==== hello_service/__init__.py (37 tokens) ====
...
==== hello_service/config.py (338 tokens) ====
...
==== hello_service/db.py (514 tokens) ====
...
==== hello_service/models.py (382 tokens) ====
...
==== hello_service/routes/__init__.py (9 tokens) ====
...
==== proto/item.proto (327 tokens) ====
...
==== requirements.txt (56 tokens) ====
...
==== scripts/__init__.py (24 tokens) ====
...
==== scripts/export.py (579 tokens) ====
...
==== tests/__init__.py (0 tokens) ====
...
==== tests/conftest.py (372 tokens) ====
...

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

It speaks JSON-RPC 2.0 with newline-delimited messages and advertises six
tools on protocol `2024-11-05`, identifying itself as `ctxpack 0.1.10`:

| tool | required | optional |
| --- | --- | --- |
| `pack_repo` | `path` | `budget`, `exclude`, `format`, `hidden`, `include`, `max_depth`, `max_size`, `model`, `no_gitignore` |
| `repo_map` | `path` | `exclude`, `format`, `include`, `max_depth`, `max_size`, `sort` |
| `count_tokens` | `path` | `exclude`, `format`, `hidden`, `include`, `max_depth`, `max_size`, `model`, `no_gitignore`, `sort`, `top` |
| `list_models` | - | `format` |
| `diff_repo` | `path` | `budget`, `exclude`, `format`, `hidden`, `include`, `list`, `max_depth`, `max_size`, `model`, `no_gitignore`, `ref` |
| `doctor` | - | `format`, `top` |

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
  31 models across 7 vendors here. It can lag a vendor's release, and `--model`
  accepts any name, so a fit number for an unlisted model is only as good as the
  nearest entry.
- Nothing here reads a model or calls an API. ctxpack is offline: the numbers
  are a prediction of what a prompt would cost, not a measurement of one.

