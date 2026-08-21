"""Populate/refresh the emission_factors table from factors_data.py.

Usage:
    python -m app.seed.seed_db
"""
from sqlalchemy import select

from app.database import SessionLocal, init_db
from app.models import EmissionFactor
from app.seed.factors_data import ALL_FACTORS


def run() -> None:
    init_db()
    db = SessionLocal()
    try:
        inserted, updated = 0, 0
        for row in ALL_FACTORS:
            stmt = select(EmissionFactor).where(
                EmissionFactor.category == row["category"], EmissionFactor.key == row["key"]
            )
            existing = db.execute(stmt).scalar_one_or_none()
            if existing:
                for field in ("factor", "unit", "source", "source_year", "notes"):
                    setattr(existing, field, row[field])
                updated += 1
            else:
                db.add(EmissionFactor(**row))
                inserted += 1
        db.commit()
        print(f"Seed complete: {inserted} inserted, {updated} updated.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
