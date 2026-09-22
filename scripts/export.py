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
