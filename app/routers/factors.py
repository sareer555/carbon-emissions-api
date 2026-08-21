from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import Caller
from app.config import get_settings
from app.database import get_db
from app.models import EmissionFactor
from app.rate_limit import enforce_rate_limit
from app.schemas import FactorOut, FactorsResponse

router = APIRouter(tags=["factors"])
settings = get_settings()


@router.get(
    "/factors",
    response_model=FactorsResponse,
    summary="List all supported fuel types and grid regions with current factors",
)
def list_factors(
    db: Session = Depends(get_db),
    caller: Caller = Depends(enforce_rate_limit),
) -> FactorsResponse:
    rows = db.execute(select(EmissionFactor)).scalars().all()
    scope1 = [FactorOut.model_validate(r, from_attributes=True) for r in rows if r.category == "scope1_fuel"]
    scope2 = [FactorOut.model_validate(r, from_attributes=True) for r in rows if r.category == "scope2_grid"]
    return FactorsResponse(scope1_fuels=scope1, scope2_grids=scope2, disclaimer=settings.disclaimer)
