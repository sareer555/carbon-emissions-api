from fastapi import APIRouter

from app import __version__
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Uptime check (no auth required)")
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)
