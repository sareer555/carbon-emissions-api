"""Pydantic request/response models."""
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Scope1FuelType = Literal["natural_gas", "diesel", "gasoline", "propane"]


class Scope1Request(BaseModel):
    fuel_type: Scope1FuelType = Field(..., description="Type of fuel combusted directly by the business.")
    quantity: float = Field(..., gt=0, description="Amount of fuel consumed, in `unit`.")
    unit: str = Field(..., description="Unit of `quantity`, e.g. 'therms', 'gallons', 'liters'.")


class Scope2Request(BaseModel):
    kwh: float = Field(..., gt=0, description="Purchased electricity consumed, in kilowatt-hours.")
    region: str = Field(..., description="Grid region code, e.g. 'US-CAMX' or 'UK'. See GET /v1/factors.")


class CalculationResult(BaseModel):
    emissions_kg_co2e: float
    category: Literal["scope1_fuel", "scope2_grid"]
    key: str
    quantity: float
    unit: str
    factor_used: float
    factor_unit: str
    factor_source: str
    disclaimer: str


class BatchLineItem(BaseModel):
    scope: Literal["scope1", "scope2"]
    fuel_type: Optional[Scope1FuelType] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = None
    kwh: Optional[float] = Field(default=None, gt=0)
    region: Optional[str] = None
    label: Optional[str] = Field(default=None, description="Optional caller-supplied identifier, e.g. invoice #.")

    @field_validator("unit")
    @classmethod
    def _unit_lower(cls, v):
        return v.lower() if v else v


class BatchRequest(BaseModel):
    items: list[BatchLineItem] = Field(..., min_length=1, max_length=1000)


class BatchLineResult(BaseModel):
    label: Optional[str] = None
    scope: Literal["scope1", "scope2"]
    emissions_kg_co2e: float
    key: str
    factor_used: float
    factor_source: str


class BatchResponse(BaseModel):
    total_emissions_kg_co2e: float
    line_items: list[BatchLineResult]
    line_item_count: int
    disclaimer: str


class FactorOut(BaseModel):
    category: str
    key: str
    factor: float
    unit: str
    source: str
    source_year: int
    notes: Optional[str] = None


class FactorsResponse(BaseModel):
    scope1_fuels: list[FactorOut]
    scope2_grids: list[FactorOut]
    disclaimer: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
