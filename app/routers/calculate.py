from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import Caller
from app.config import get_settings
from app.database import get_db
from app.errors import InvalidRequestError
from app.logging_config import log_request
from app.rate_limit import enforce_rate_limit
from app.schemas import (
    BatchLineResult,
    BatchRequest,
    BatchResponse,
    CalculationResult,
    Scope1Request,
    Scope2Request,
)
from app.services.emissions import calculate_scope1, calculate_scope2

router = APIRouter(prefix="/calculate", tags=["calculate"])
settings = get_settings()


@router.post("/scope1", response_model=CalculationResult, summary="Calculate Scope 1 (direct fuel) emissions")
def scope1(
    body: Scope1Request,
    db: Session = Depends(get_db),
    caller: Caller = Depends(enforce_rate_limit),
) -> CalculationResult:
    result = calculate_scope1(db, body.fuel_type, body.quantity, body.unit)
    log_request(db, "/v1/calculate/scope1", caller.api_key_id, 200, result.category, result.key)
    return CalculationResult(
        emissions_kg_co2e=result.emissions_kg_co2e,
        category=result.category,
        key=result.key,
        quantity=result.quantity,
        unit=result.unit,
        factor_used=result.factor_used,
        factor_unit=result.factor_unit,
        factor_source=result.factor_source,
        disclaimer=settings.disclaimer,
    )


@router.post("/scope2", response_model=CalculationResult, summary="Calculate Scope 2 (purchased electricity) emissions")
def scope2(
    body: Scope2Request,
    db: Session = Depends(get_db),
    caller: Caller = Depends(enforce_rate_limit),
) -> CalculationResult:
    result = calculate_scope2(db, body.kwh, body.region)
    log_request(db, "/v1/calculate/scope2", caller.api_key_id, 200, result.category, result.key)
    return CalculationResult(
        emissions_kg_co2e=result.emissions_kg_co2e,
        category=result.category,
        key=result.key,
        quantity=result.quantity,
        unit=result.unit,
        factor_used=result.factor_used,
        factor_unit=result.factor_unit,
        factor_source=result.factor_source,
        disclaimer=settings.disclaimer,
    )


@router.post(
    "/batch",
    response_model=BatchResponse,
    summary="Calculate and sum Scope 1 + Scope 2 emissions for a batch of line items",
)
def batch(
    body: BatchRequest,
    db: Session = Depends(get_db),
    caller: Caller = Depends(enforce_rate_limit),
) -> BatchResponse:
    line_results: list[BatchLineResult] = []
    total = 0.0

    for i, item in enumerate(body.items):
        if item.scope == "scope1":
            if item.fuel_type is None or item.quantity is None or item.unit is None:
                raise InvalidRequestError(
                    f"items[{i}]: scope1 line items require fuel_type, quantity, and unit."
                )
            result = calculate_scope1(db, item.fuel_type, item.quantity, item.unit)
        else:
            if item.kwh is None or item.region is None:
                raise InvalidRequestError(f"items[{i}]: scope2 line items require kwh and region.")
            result = calculate_scope2(db, item.kwh, item.region)

        total += result.emissions_kg_co2e
        log_request(db, "/v1/calculate/batch", caller.api_key_id, 200, result.category, result.key)
        line_results.append(
            BatchLineResult(
                label=item.label,
                scope=item.scope,
                emissions_kg_co2e=result.emissions_kg_co2e,
                key=result.key,
                factor_used=result.factor_used,
                factor_source=result.factor_source,
            )
        )

    return BatchResponse(
        total_emissions_kg_co2e=round(total, 4),
        line_items=line_results,
        line_item_count=len(line_results),
        disclaimer=settings.disclaimer,
    )
