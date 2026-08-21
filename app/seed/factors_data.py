"""Seed data for the `emission_factors` table.

Sources (verified against the primary spreadsheets on 2026-08-21):

- US fuel factors (Scope 1): EPA "Emission Factors for Greenhouse Gas Inventories"
  (GHG Emission Factors Hub), 2025 edition, Table 1 (Stationary Combustion).
  GWPs used to combine CO2 + CH4 + N2O into CO2e are the Hub's own IPCC AR5
  100-year values: CH4 = 28, N2O = 265 (see the Hub's "Gas / 100-Year GWP" table).
- US grid factors (Scope 2): EPA eGRID Summary Tables 2023 (eGRID2023 data),
  Table 1 "Subregion Output Emission Rates" (lb/MWh), converted to kg CO2e/kWh
  using the same AR5 GWPs and 1 lb = 0.45359237 kg. All 27 eGRID subregions plus
  the U.S. national average are included, each with an explicit year-keyed row
  (e.g. 'US-CAMX-2023', matching the eGRID *dataset* year, since eGRID for a
  given year is published roughly two years later) plus a bare-key alias (e.g.
  'US-CAMX') that tracks the latest eGRID dataset verified in this file -- same
  pattern as the UK rows below.
- UK grid factor (Scope 2): UK Government (DEFRA/DESNZ) "Greenhouse gas reporting:
  conversion factors" full sets, "UK electricity" tab, "Electricity generated"
  location-based factor. Both the 2025 and 2026 editions' reporting-year factors
  are included ('UK-2025', 'UK-2026'), since DEFRA's own guidance is to apply the
  factor matching the year the activity occurred, not the publication year. 'UK'
  is a convenience alias for the latest edition.

Units:
- scope1_fuel factors are kg CO2e per canonical unit (see app/services/units.py
  for accepted input-unit conversions).
- scope2_grid factors are kg CO2e per kWh.
"""

SCOPE1_FUEL_FACTORS = [
    {
        "category": "scope1_fuel",
        "key": "natural_gas",
        "factor": 5.3115,
        "unit": "therms",
        "source": "EPA GHG Emission Factors Hub (2025 edition), Table 1: Stationary Combustion - Natural Gas",
        "source_year": 2025,
        "notes": (
            "53.06 kg CO2/mmBtu + 1 g CH4/mmBtu (GWP 28) + 0.1 g N2O/mmBtu (GWP 265) "
            "= 53.1145 kg CO2e/mmBtu; 1 therm = 0.1 mmBtu -> 5.3115 kg CO2e/therm."
        ),
    },
    {
        "category": "scope1_fuel",
        "key": "diesel",
        "factor": 10.2427,
        "unit": "gallons",
        "source": "EPA GHG Emission Factors Hub (2025 edition), Table 1: Stationary Combustion - Distillate Fuel Oil No. 2",
        "source_year": 2025,
        "notes": (
            "10.21 kg CO2/gal + 0.41 g CH4/gal (GWP 28) + 0.08 g N2O/gal (GWP 265) "
            "= 10.2427 kg CO2e/gallon."
        ),
    },
    {
        "category": "scope1_fuel",
        "key": "gasoline",
        "factor": 8.8118,
        "unit": "gallons",
        "source": "EPA GHG Emission Factors Hub (2025 edition), Table 1: Stationary Combustion - Motor Gasoline",
        "source_year": 2025,
        "notes": (
            "8.78 kg CO2/gal + 0.38 g CH4/gal (GWP 28) + 0.08 g N2O/gal (GWP 265) "
            "= 8.8118 kg CO2e/gallon."
        ),
    },
    {
        "category": "scope1_fuel",
        "key": "propane",
        "factor": 5.7037,
        "unit": "gallons",
        "source": "EPA GHG Emission Factors Hub (2025 edition), Table 1: Stationary Combustion - Liquefied Petroleum Gases (LPG)",
        "source_year": 2025,
        "notes": (
            "5.68 kg CO2/gal + 0.28 g CH4/gal (GWP 28) + 0.06 g N2O/gal (GWP 265) "
            "= 5.7037 kg CO2e/gallon."
        ),
    },
]

SCOPE2_GRID_FACTORS = [
    # --- United States (EPA eGRID Summary Tables 2023 / eGRID2023 data) ---
    # Each subregion has an explicit year-keyed row (e.g. 'US-CAMX-2023', matching
    # the eGRID dataset year, not the publication date) plus a bare-key alias
    # ('US-CAMX') that always tracks the latest eGRID dataset available. When a
    # newer eGRID release is verified, add its '-YYYY' rows alongside these and
    # repoint the aliases -- exactly the pattern used for the UK grid factors.
    {
        "category": "scope2_grid",
        "key": "US-AKGD-2023",
        "factor": 0.4106,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "ASCC Alaska Grid (AKGD). 899.633 lb CO2/MWh + 0.086 lb CH4/MWh + 0.012 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.4106 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-AKGD",
        "factor": 0.4106,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-AKGD-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-AKMS-2023",
        "factor": 0.2369,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "ASCC Miscellaneous (AKMS). 520.483 lb CO2/MWh + 0.026 lb CH4/MWh + 0.004 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.2369 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-AKMS",
        "factor": 0.2369,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-AKMS-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-AZNM-2023",
        "factor": 0.3203,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "WECC Southwest (AZNM). 703.703 lb CO2/MWh + 0.039 lb CH4/MWh + 0.005 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3203 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-AZNM",
        "factor": 0.3203,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-AZNM-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-CAMX-2023",
        "factor": 0.195,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "WECC California (CAMX). 428.464 lb CO2/MWh + 0.025 lb CH4/MWh + 0.003 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.195 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-CAMX",
        "factor": 0.195,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-CAMX-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-ERCT-2023",
        "factor": 0.3341,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "ERCOT All (ERCT). 733.862 lb CO2/MWh + 0.043 lb CH4/MWh + 0.006 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3341 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-ERCT",
        "factor": 0.3341,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-ERCT-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-FRCC-2023",
        "factor": 0.3559,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "FRCC All (FRCC). 782.262 lb CO2/MWh + 0.041 lb CH4/MWh + 0.005 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3559 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-FRCC",
        "factor": 0.3559,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-FRCC-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-HIMS-2023",
        "factor": 0.5141,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "HICC Miscellaneous (HIMS). 1123.371 lb CO2/MWh + 0.146 lb CH4/MWh + 0.022 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.5141 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-HIMS",
        "factor": 0.5141,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-HIMS-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-HIOA-2023",
        "factor": 0.6799,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "HICC Oahu (HIOA). 1489.548 lb CO2/MWh + 0.134 lb CH4/MWh + 0.021 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.6799 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-HIOA",
        "factor": 0.6799,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-HIOA-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-MROE-2023",
        "factor": 0.6373,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "MRO East (MROE). 1397.313 lb CO2/MWh + 0.116 lb CH4/MWh + 0.017 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.6373 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-MROE",
        "factor": 0.6373,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-MROE-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-MROW-2023",
        "factor": 0.4203,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "MRO West (MROW). 920.13 lb CO2/MWh + 0.097 lb CH4/MWh + 0.014 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.4203 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-MROW",
        "factor": 0.4203,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-MROW-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-NEWE-2023",
        "factor": 0.2464,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "NPCC New England (NEWE). 539.275 lb CO2/MWh + 0.063 lb CH4/MWh + 0.008 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.2464 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-NEWE",
        "factor": 0.2464,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-NEWE-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-NWPP-2023",
        "factor": 0.2882,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "WECC Northwest (NWPP). 631.735 lb CO2/MWh + 0.054 lb CH4/MWh + 0.008 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.2882 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-NWPP",
        "factor": 0.2882,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-NWPP-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-NYCW-2023",
        "factor": 0.3926,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "NPCC NYC/Westchester (NYCW). 864.469 lb CO2/MWh + 0.022 lb CH4/MWh + 0.002 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3926 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-NYCW",
        "factor": 0.3926,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-NYCW-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-NYLI-2023",
        "factor": 0.5395,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "NPCC Long Island (NYLI). 1180.672 lb CO2/MWh + 0.14 lb CH4/MWh + 0.018 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.5395 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-NYLI",
        "factor": 0.5395,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-NYLI-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-NYUP-2023",
        "factor": 0.1101,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "NPCC Upstate NY (NYUP). 242.089 lb CO2/MWh + 0.011 lb CH4/MWh + 0.001 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.1101 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-NYUP",
        "factor": 0.1101,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-NYUP-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-PRMS-2023",
        "factor": 0.7023,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Puerto Rico Miscellaneous (PRMS). 1543.073 lb CO2/MWh + 0.077 lb CH4/MWh + 0.012 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.7023 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-PRMS",
        "factor": 0.7023,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-PRMS-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-RFCE-2023",
        "factor": 0.2718,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "RFC East (RFCE). 596.904 lb CO2/MWh + 0.036 lb CH4/MWh + 0.005 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.2718 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-RFCE",
        "factor": 0.2718,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-RFCE-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-RFCM-2023",
        "factor": 0.4427,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "RFC Michigan (RFCM). 970.617 lb CO2/MWh + 0.082 lb CH4/MWh + 0.012 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.4427 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-RFCM",
        "factor": 0.4427,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-RFCM-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-RFCW-2023",
        "factor": 0.4155,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "RFC West (RFCW). 911.424 lb CO2/MWh + 0.071 lb CH4/MWh + 0.01 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.4155 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-RFCW",
        "factor": 0.4155,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-RFCW-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-RMPA-2023",
        "factor": 0.4729,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "WECC Rockies (RMPA). 1036.601 lb CO2/MWh + 0.09 lb CH4/MWh + 0.013 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.4729 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-RMPA",
        "factor": 0.4729,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-RMPA-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-SPNO-2023",
        "factor": 0.3935,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "SPP North (SPNO). 861.999 lb CO2/MWh + 0.087 lb CH4/MWh + 0.012 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3935 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-SPNO",
        "factor": 0.3935,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-SPNO-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-SPSO-2023",
        "factor": 0.3972,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "SPP South (SPSO). 872.042 lb CO2/MWh + 0.054 lb CH4/MWh + 0.008 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3972 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-SPSO",
        "factor": 0.3972,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-SPSO-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRMV-2023",
        "factor": 0.3364,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "SERC Mississippi Valley (SRMV). 739.72 lb CO2/MWh + 0.032 lb CH4/MWh + 0.004 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3364 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRMV",
        "factor": 0.3364,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-SRMV-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRMW-2023",
        "factor": 0.5663,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "SERC Midwest (SRMW). 1239.839 lb CO2/MWh + 0.132 lb CH4/MWh + 0.019 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.5663 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRMW",
        "factor": 0.5663,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-SRMW-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRSO-2023",
        "factor": 0.3837,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "SERC South (SRSO). 842.329 lb CO2/MWh + 0.056 lb CH4/MWh + 0.008 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3837 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRSO",
        "factor": 0.3837,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-SRSO-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRTV-2023",
        "factor": 0.4097,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "SERC Tennessee Valley (SRTV). 898.079 lb CO2/MWh + 0.079 lb CH4/MWh + 0.011 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.4097 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRTV",
        "factor": 0.4097,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-SRTV-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRVC-2023",
        "factor": 0.2705,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "SERC Virginia/Carolina (SRVC). 593.419 lb CO2/MWh + 0.045 lb CH4/MWh + 0.006 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.2705 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-SRVC",
        "factor": 0.2705,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-SRVC-2023').",
    },
    {
        "category": "scope2_grid",
        "key": "US-AVG-2023",
        "factor": 0.3497,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "U.S. national average (all subregions). 767.209 lb CO2/MWh + 0.057 lb CH4/MWh + 0.008 lb N2O/MWh, CO2e via IPCC AR5 GWPs (CH4=28, N2O=265) -> 0.3497 kg CO2e/kWh.",
    },
    {
        "category": "scope2_grid",
        "key": "US-AVG",
        "factor": 0.3497,
        "unit": "kwh",
        "source": "EPA eGRID Summary Tables 2023 (eGRID2023 data), Table 1: Subregion Output Emission Rates",
        "source_year": 2023,
        "notes": "Alias for the latest available eGRID dataset (currently 2023 -> same value as 'US-AVG-2023').",
    },
    # --- United Kingdom (DEFRA/DESNZ GHG Conversion Factors) ---
    {
        "category": "scope2_grid",
        "key": "UK",
        "factor": 0.13096,
        "unit": "kwh",
        "source": "UK Government (DEFRA/DESNZ) GHG Conversion Factors for Company Reporting, 2026 full set",
        "source_year": 2026,
        "notes": (
            "Alias for the latest available reporting year (currently 2026 -> same "
            "value as 'UK-2026'). UK electricity generation, location-based factor: "
            "0.12943 kg CO2 + 0.00067 kg CH4-as-CO2e + 0.00086 kg N2O-as-CO2e per kWh "
            "= 0.13096 kg CO2e/kWh. For emissions attributable to a specific reporting "
            "year, use the explicit 'UK-2025' / 'UK-2026' keys instead of this alias."
        ),
    },
    {
        "category": "scope2_grid",
        "key": "UK-2026",
        "factor": 0.13096,
        "unit": "kwh",
        "source": "UK Government (DEFRA/DESNZ) GHG Conversion Factors for Company Reporting, 2026 full set",
        "source_year": 2026,
        "notes": (
            "UK electricity generation, location-based factor, reporting year 2026: "
            "0.12943 kg CO2 + 0.00067 kg CH4-as-CO2e + 0.00086 kg N2O-as-CO2e per kWh "
            "= 0.13096 kg CO2e/kWh. Down from 0.177 kg CO2e/kWh in the 2025 edition "
            "(DEFRA's 2026 update cites a methodology improvement plus continued grid "
            "decarbonization)."
        ),
    },
    {
        "category": "scope2_grid",
        "key": "UK-2025",
        "factor": 0.177,
        "unit": "kwh",
        "source": "UK Government (DEFRA/DESNZ) GHG Conversion Factors for Company Reporting, 2025 full set",
        "source_year": 2025,
        "notes": (
            "UK electricity generation, location-based factor, reporting year 2025: "
            "0.17489 kg CO2 + 0.0009 kg CH4-as-CO2e + 0.00122 kg N2O-as-CO2e per kWh "
            "= 0.177 kg CO2e/kWh. Kept available for organisations reporting on "
            "activity that occurred during the 2025 calendar year, per DEFRA's own "
            "guidance to apply the factor matching the reporting year, not the "
            "publication year."
        ),
    },
]

ALL_FACTORS = SCOPE1_FUEL_FACTORS + SCOPE2_GRID_FACTORS

