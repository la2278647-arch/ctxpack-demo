"""Route tests.

Each test starts from an empty database, so a failing test cannot mask a
failure in the next one.
"""


def test_healthz_always_ok(client):
    assert client.get("/healthz").json() == {"status": "ok"}


def test_readyz_reports_ready(client):
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_create_and_fetch_item(client):
    body = {"sku": "SKU-1", "name": "Widget", "price_cents": 1999, "quantity": 3}
    r = client.post("/items", json=body)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["sku"] == "SKU-1"
    assert created["id"] == 1

    got = client.get(f"/items/{created['id']}").json()
    assert got == created


def test_duplicate_sku_is_a_conflict(client):
    body = {"sku": "SKU-1", "name": "Widget", "price_cents": 1}
    assert client.post("/items", json=body).status_code == 201
    assert client.post("/items", json=body).status_code == 409


def test_patch_updates_only_named_fields(client):
    r = client.post("/items", json={"sku": "SKU-2", "name": "Gadget", "price_cents": 500}).json()
    r = client.patch(f"/items/{r['id']}", json={"quantity": 7})
    assert r.status_code == 200, r.text
    assert r.json()["quantity"] == 7
    assert r.json()["price_cents"] == 500


def test_delete_is_idempotent(client):
    r = client.post("/items", json={"sku": "SKU-3", "name": "Gizmo", "price_cents": 1}).json()
    assert client.delete(f"/items/{r['id']}").status_code == 204
    assert client.delete(f"/items/{r['id']}").status_code == 204
    assert client.get(f"/items/{r['id']}").status_code == 404


def test_missing_item_is_a_404(client):
    assert client.get("/items/9999").status_code == 404


def test_empty_sku_is_rejected(client):
    assert (
        client.post("/items", json={"sku": "", "name": "X", "price_cents": 1}).status_code == 422
    )


def test_lowercase_sku_is_rejected(client):
    assert (
        client.post("/items", json={"sku": "bad-sku", "name": "X", "price_cents": 1}).status_code
        == 422
    )


def test_negative_price_is_rejected(client):
    assert (
        client.post("/items", json={"sku": "SKU-4", "name": "X", "price_cents": -1}).status_code
        == 422
    )


def test_pagination_returns_next_cursor(client):
    for i in range(5):
        client.post("/items", json={"sku": f"SKU-{i}", "name": f"n{i}", "price_cents": i})
    page = client.get("/items?limit=2").json()
    assert len(page["items"]) == 2
    assert page["next_cursor"] is not None
