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
