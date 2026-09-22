"""Item routes.

The router owns request and response models; db.py owns persistence. Keeping
the two apart means the routes stay testable with a stub session.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from hello_service.db import get_session

router = APIRouter(prefix="/items", tags=["items"])


class ItemIn(BaseModel):
    sku: str = Field(min_length=1, max_length=64, pattern=r"^[A-Z0-9-]+$")
    name: str = Field(min_length=1, max_length=200)
    price_cents: int = Field(ge=0)
    quantity: int = Field(ge=0, default=0)


class ItemOut(ItemIn):
    id: int
    updated_at: str | None


class Page(BaseModel):
    items: list[ItemOut]
    next_cursor: str | None


def _row_type():
    """Indirection so the tests can patch one name, not three."""
    from hello_service.models import Item

    return Item


def _serialize(row) -> dict:
    """Map a row to the response shape. One place to change field names."""
    return {
        "id": row.id,
        "sku": row.sku,
        "name": row.name,
        "price_cents": row.price_cents,
        "quantity": row.quantity,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@router.get("", response_model=Page)
def list_items(
    session: Annotated[Session, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    cursor: str | None = None,
) -> Page:
    """Return one page of items, newest first. Cursor is an item id."""
    model = _row_type()
    stmt = select(model).order_by(model.id.desc()).limit(limit)
    if cursor:
        stmt = stmt.where(model.id < int(cursor))
    rows = session.scalars(stmt).all()
    out = [_serialize(r) for r in rows]
    return Page(items=out, next_cursor=str(out[-1]["id"]) if len(out) == limit else None)


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemIn, session: Annotated[Session, Depends(get_session)]) -> dict:
    """Insert a new item. SKU collisions raise 409, not a generic 500."""
    model = _row_type()
    existing = session.scalar(select(model).where(model.sku == item.sku))
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"sku {item.sku!r} already exists")
    row = model(**item.model_dump())
    session.add(row)
    session.flush()
    return _serialize(row)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, session: Annotated[Session, Depends(get_session)]) -> dict:
    """Fetch one item by id. Missing items are a 404, not an empty response."""
    row = session.get(_row_type(), item_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"item {item_id} not found")
    return _serialize(row)


@router.patch("/{item_id}", response_model=ItemOut)
def patch_item(item_id: int, body: dict, session: Annotated[Session, Depends(get_session)]) -> dict:
    """Partial update. Only keys present in the body are written."""
    row = session.get(_row_type(), item_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"item {item_id} not found")
    for key, value in body.items():
        if hasattr(row, key):
            setattr(row, key, value)
    session.flush()
    return _serialize(row)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: Annotated[Session, Depends(get_session)]) -> None:
    """Delete an item. Idempotent: a second delete is a no-op."""
    row = session.get(_row_type(), item_id)
    if row is None:
        return
    session.delete(row)
