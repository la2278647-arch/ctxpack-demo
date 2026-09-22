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
