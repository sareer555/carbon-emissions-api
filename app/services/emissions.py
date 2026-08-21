"""Core emissions calculation logic (Scope 1 + Scope 2)."""
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import InvalidFuelTypeError, InvalidRegionError
from app.models import EmissionFactor
from app.services.units import to_canonical


@dataclass
class CalcResult:
    emissions_kg_co2e: float
    category: str
    key: str
    quantity: float
    unit: str
    factor_used: float
    factor_unit: str
    factor_source: str


def _get_factor(db: Session, category: str, key: str) -> EmissionFactor:
    stmt = select(EmissionFactor).where(EmissionFactor.category == category, EmissionFactor.key == key)
    factor = db.execute(stmt).scalar_one_or_none()
    if factor is None:
        if category == "scope1_fuel":
            raise InvalidFuelTypeError(
                f"Unsupported fuel_type '{key}'. See GET /v1/factors for supported fuel types."
            )
        raise InvalidRegionError(f"Unsupported region '{key}'. See GET /v1/factors for supported regions.")
    return factor


def calculate_scope1(db: Session, fuel_type: str, quantity: float, unit: str) -> CalcResult:
    factor = _get_factor(db, "scope1_fuel", fuel_type)
    canonical_qty = to_canonical(quantity, unit, factor.unit)
    emissions = round(canonical_qty * float(factor.factor), 4)
    return CalcResult(
        emissions_kg_co2e=emissions,
        category="scope1_fuel",
        key=fuel_type,
        quantity=quantity,
        unit=unit,
        factor_used=float(factor.factor),
        factor_unit=factor.unit,
        factor_source=f"{factor.source}",
    )


def calculate_scope2(db: Session, kwh: float, region: str) -> CalcResult:
    factor = _get_factor(db, "scope2_grid", region)
    emissions = round(kwh * float(factor.factor), 4)
    return CalcResult(
        emissions_kg_co2e=emissions,
        category="scope2_grid",
        key=region,
        quantity=kwh,
        unit="kwh",
        factor_used=float(factor.factor),
        factor_unit=factor.unit,
        factor_source=f"{factor.source}",
    )
