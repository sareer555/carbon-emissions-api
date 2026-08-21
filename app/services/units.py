"""Unit conversion so callers aren't forced to use each factor's exact stored unit.

Each fuel's emission factor is stored per one canonical unit (see
app/seed/factors_data.py). This module converts any *supported* input unit
into that canonical unit before the factor is applied. Electricity (kWh) has
no conversions — kWh is the only supported unit for Scope 2.
"""
from app.errors import InvalidUnitError

# multiplier to convert 1 <unit> -> 1 <canonical unit>
_CONVERSIONS: dict[str, dict[str, float]] = {
    "therms": {
        "therms": 1.0,
        "therm": 1.0,
        "mmbtu": 10.0,  # 1 mmBtu = 10 therms
        "ccf": 1.037,  # 1 CCF natural gas ≈ 1.037 therms (approx, varies by heat content)
    },
    "gallons": {
        "gallons": 1.0,
        "gallon": 1.0,
        "gal": 1.0,
        "liters": 0.264172,
        "litres": 0.264172,
        "l": 0.264172,
    },
    "kwh": {
        "kwh": 1.0,
    },
}


def to_canonical(quantity: float, input_unit: str, canonical_unit: str) -> float:
    """Convert `quantity` expressed in `input_unit` into `canonical_unit`.

    Raises InvalidUnitError if the unit isn't recognized for this canonical unit.
    """
    table = _CONVERSIONS.get(canonical_unit)
    if table is None:
        # Canonical unit has no conversion table registered -> only itself is accepted.
        if input_unit.lower() == canonical_unit.lower():
            return quantity
        raise InvalidUnitError(
            f"Unit '{input_unit}' is not supported for this factor. Expected '{canonical_unit}'."
        )

    multiplier = table.get(input_unit.lower())
    if multiplier is None:
        supported = ", ".join(sorted(table.keys()))
        raise InvalidUnitError(
            f"Unit '{input_unit}' is not supported. Supported units: {supported}."
        )
    return quantity * multiplier
