"""Seed data for the `emission_factors` table.

⚠️ VERIFY BEFORE PRODUCTION / PAID USE ⚠️
--------------------------------------------------------------------------
These figures were compiled from the publicly published EPA GHG Emission
Factors Hub, EPA eGRID, and UK DEFRA/DESNZ GHG Conversion Factors, using
web research performed inside a sandboxed environment with no direct
network access to epa.gov or gov.uk. Every row below cites the document and
year it was drawn from and includes a `notes` field with the calculation
used to derive it. Before charging customers or presenting this data as
audit-grade, a human should re-derive each figure directly from the
primary spreadsheet (see README "Refreshing emission factors") and update
this file. This mirrors the project's own trust requirement in section 3
of the build brief: never present unverified numbers as certified.
--------------------------------------------------------------------------

Units:
- scope1_fuel factors are kg CO2e per canonical unit (see app/services/units.py
  for accepted input-unit conversions).
- scope2_grid factors are kg CO2e per kWh.
"""

SCOPE1_FUEL_FACTORS = [
    {
        "category": "scope1_fuel",
        "key": "natural_gas",
        "factor": 5.311,
        "unit": "therms",
        "source": "EPA GHG Emission Factors Hub (2025 edition)",
        "source_year": 2025,
        "notes": (
            "Derived from the Hub's stationary combustion natural gas factors: "
            "53.06 kg CO2/mmBtu + 1.0 g CH4/mmBtu (GWP 25) + 0.10 g N2O/mmBtu "
            "(GWP 298) = 53.115 kg CO2e/mmBtu; 1 therm = 0.1 mmBtu -> 5.311 kg CO2e/therm."
        ),
    },
    {
        "category": "scope1_fuel",
        "key": "diesel",
        "factor": 10.21,
        "unit": "gallons",
        "source": "EPA GHG Emission Factors Hub (2025 edition)",
        "source_year": 2025,
        "notes": "Distillate fuel oil no. 2, stationary combustion, CO2 factor per US gallon.",
    },
    {
        "category": "scope1_fuel",
        "key": "gasoline",
        "factor": 8.887,
        "unit": "gallons",
        "source": "EPA GHG Emission Factors Hub / EPA GHG Equivalencies Calculator methodology (2025)",
        "source_year": 2025,
        "notes": "Motor gasoline, widely-cited EPA figure of 8,887 g CO2 per US gallon combusted.",
    },
    {
        "category": "scope1_fuel",
        "key": "propane",
        "factor": 5.62,
        "unit": "gallons",
        "source": "EPA GHG Emission Factors Hub (2025 edition)",
        "source_year": 2025,
        "notes": (
            "Propane/LPG stationary combustion: 61.46 kg CO2/mmBtu x ~0.0915 mmBtu/gallon "
            "heat content -> 5.62 kg CO2/gallon; cross-checked against 236.0 kg CO2 per "
            "42-gallon barrel (5.62 kg/gallon)."
        ),
    },
]

SCOPE2_GRID_FACTORS = [
    # --- United States (EPA eGRID2023 data, published January 2025) ---
    {
        "category": "scope2_grid",
        "key": "US-CAMX",
        "factor": 0.1981,
        "unit": "kwh",
        "source": "EPA eGRID2023 (subregion output emission rates, released Jan 2025)",
        "source_year": 2025,
        "notes": "WECC California (CAMX). 436.655 lb CO2/MWh -> 0.1981 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-ERCT",
        "factor": 0.3348,
        "unit": "kwh",
        "source": "EPA eGRID2023 (subregion output emission rates, released Jan 2025)",
        "source_year": 2025,
        "notes": "ERCOT All (ERCT, Texas). 738.038 lb CO2/MWh -> 0.3348 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-FRCC",
        "factor": 0.3649,
        "unit": "kwh",
        "source": "EPA eGRID2023 (subregion output emission rates, released Jan 2025)",
        "source_year": 2025,
        "notes": "Florida Reliability Coordinating Council (FRCC). 804.477 lb CO2e/MWh -> 0.3649 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-MROW",
        "factor": 0.4202,
        "unit": "kwh",
        "source": "EPA eGRID2023 (subregion output emission rates, released Jan 2025)",
        "source_year": 2025,
        "notes": "MRO West (MROW, Upper Midwest). 926.443 lb CO2e/MWh -> 0.4202 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-AVG",
        "factor": 0.370,
        "unit": "kwh",
        "source": "EPA eGRID2023 national average (approximate)",
        "source_year": 2025,
        "notes": (
            "Fallback for US customers who don't know their eGRID subregion. "
            "Approximate national average (~370 g CO2/kWh); prefer a specific "
            "US-XXXX subregion factor when the customer's utility/region is known."
        ),
    },
    # --- United Kingdom (DEFRA / DESNZ GHG Conversion Factors) ---
    {
        "category": "scope2_grid",
        "key": "UK",
        "factor": 0.177,
        "unit": "kwh",
        "source": "UK Government (DEFRA/DESNZ) GHG Conversion Factors for Company Reporting, 2025",
        "source_year": 2025,
        "notes": (
            "UK electricity generation, location-based factor. Down from 0.207 kg "
            "CO2e/kWh in the 2024 edition, reflecting continued grid decarbonization."
        ),
    },
]

ALL_FACTORS = SCOPE1_FUEL_FACTORS + SCOPE2_GRID_FACTORS
