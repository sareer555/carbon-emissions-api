"""Admin-only key provisioning.

Exists because Render's free tier (and most $0 hosts) doesn't offer shell
access, so `python -m app.scripts.create_api_key` isn't reachable there.
This endpoint does the same thing over HTTP, gated by a separate shared
secret (ADMIN_BOOTSTRAP_TOKEN) -- never the api_keys table, never a
customer-issued key.

Disabled by default: if ADMIN_BOOTSTRAP_TOKEN is unset, this route 404s
for everyone, so a forgotten env var fails closed rather than open.
"""
import secrets

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth import bearer_scheme, hash_key
from app.config import get_settings
from app.database import get_db
from app.errors import UnauthorizedError
from app.models import ApiKey
from app.schemas import AdminCreateKeyRequest, AdminCreateKeyResponse

router = APIRouter(prefix="/admin", tags=["admin"])
settings = get_settings()


def require_admin_token(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> None:
    configured = settings.admin_bootstrap_token
    if not configured:
        # Fail closed: no token configured means this endpoint doesn't exist.
        raise UnauthorizedError("Admin endpoint is disabled (ADMIN_BOOTSTRAP_TOKEN not set).")

    if credentials is None:
        raise UnauthorizedError("Missing or malformed Authorization header. Expected 'Bearer <admin_token>'.")

    if not secrets.compare_digest(credentials.credentials, configured):
        raise UnauthorizedError("Invalid admin token.")


@router.post(
    "/keys",
    response_model=AdminCreateKeyResponse,
    summary="Issue a new customer API key (admin-only, requires ADMIN_BOOTSTRAP_TOKEN)",
)
def create_key(
    body: AdminCreateKeyRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_token),
) -> AdminCreateKeyResponse:
    plaintext_key = f"cek_{secrets.token_urlsafe(32)}"
    db.add(ApiKey(key_hash=hash_key(plaintext_key), plan=body.plan, label=body.label))
    db.commit()
    return AdminCreateKeyResponse(api_key=plaintext_key, plan=body.plan, label=body.label)
