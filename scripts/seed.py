"""Create the tables and load a few starter rows.

This is a developer convenience only. Real deployments use a migration tool
(Alembic) instead of metadata.create_all, and seed data is test-only.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hello_service.config import get_settings
from hello_service.db import Base
from hello_service.models import Item

STARTER = [
    {"sku": "SKU-0001", "name": "WIDGET 001", "price_cents": 1299, "quantity": 42},
    {"sku": "SKU-0002", "name": "GADGET 002", "price_cents": 899, "quantity": 0},
    {"sku": "SKU-0003", "name": "GIZMO 003", "price_cents": 2499, "quantity": 7},
    {"sku": "SKU-0004", "name": "SPROCKET 004", "price_cents": 349, "quantity": 300},
]


def main() -> None:
    """Create the schema and insert the starter rows, idempotently."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    added = 0
    with Session() as session:
        existing = {i.sku for i in session.scalars(Item.__table__.select()).all()}
        for row in STARTER:
            if row["sku"] in existing:
                continue
            session.add(Item(**row))
            added += 1
        session.commit()

    print(f"seeded {added} items into {settings.database_url}")


if __name__ == "__main__":
    main()
