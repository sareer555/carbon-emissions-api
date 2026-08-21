"""Request authentication.

Two callers are trusted:

1. **Direct customers** — `Authorization: Bearer <cek_...>` against our own
   `api_keys` table (see app/scripts/create_api_key.py / POST /v1/admin/keys).
   Monthly quota is enforced here, per `plan_quotas`.
2. **RapidAPI customers** — RapidAPI proxies their request to us and adds an
   `X-RapidAPI-Proxy-Secret` header proving the request actually came through
   RapidAPI's platform (not a direct call bypassing their billing). RapidAPI
   itself enforces the buyer's plan/quota on their side, so we don't check
   `api_keys` or `plan_quotas` for this path — we trust the secret and log
   the caller by their `X-RapidAPI-User` header instead.

Keys are stored hashed (SHA-256) so the plaintext key is never persisted
server-side after creation.
"""
import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.errors import QuotaExceededError, UnauthorizedError
from app.models import ApiKey

settings = get_settings()

# A real FastAPI security scheme (rather than a raw Header() param) so
# Swagger UI renders a single global "Authorize" button that applies the
# bearer token to every protected endpoint, instead of a per-endpoint text
# field. auto_error=False so a missing header raises our own UnauthorizedError
# with our error shape, not FastAPI's default 403.
bearer_scheme = HTTPBearer(auto_error=False, description="Your API key, e.g. cek_...")


@dataclass
class Caller:
    """Whoever authenticated this request, direct customer or RapidAPI subscriber."""

    source: str  # "direct" | "rapidapi"
    rate_limit_key: str  # bucket identity for the burst limiter
    api_key_id: int | None  # api_keys.id for direct customers, None for RapidAPI (no local row)
    plan: str


def hash_key(plaintext_key: str) -> str:
    return hashlib.sha256(plaintext_key.encode("utf-8")).hexdigest()


def _maybe_reset_period(api_key: ApiKey, db: Session) -> None:
    now = datetime.now(timezone.utc)
    reset_at = api_key.period_reset_at
    if reset_at is not None and reset_at.tzinfo is None:
        reset_at = reset_at.replace(tzinfo=timezone.utc)
    if reset_at is None or now >= reset_at:
        api_key.calls_this_period = 0
        api_key.period_reset_at = now + timedelta(days=30)
        db.add(api_key)
        db.commit()


def _authenticate_direct_key(credentials: HTTPAuthorizationCredentials | None, db: Session) -> Caller:
    """Validate our own Bearer API key and enforce its monthly quota."""
    if credentials is None:
        raise UnauthorizedError("Missing or malformed Authorization header. Expected 'Bearer <api_key>'.")

    plaintext_key = credentials.credentials.strip()
    if not plaintext_key:
        raise UnauthorizedError("Missing API key.")

    key_hash = hash_key(plaintext_key)
    stmt = select(ApiKey).where(ApiKey.key_hash == key_hash)
    api_key = db.execute(stmt).scalar_one_or_none()

    if api_key is None or not api_key.active:
        raise UnauthorizedError("Invalid or inactive API key.")

    _maybe_reset_period(api_key, db)

    quota = settings.plan_quotas.get(api_key.plan, 0)
    if api_key.calls_this_period >= quota:
        raise QuotaExceededError(
            f"Monthly quota of {quota} calls exceeded for plan '{api_key.plan}'. "
            "Upgrade your plan or wait for the next billing period."
        )

    api_key.calls_this_period += 1
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return Caller(source="direct", rate_limit_key=f"direct:{api_key.id}", api_key_id=api_key.id, plan=api_key.plan)


def authenticate(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_rapidapi_proxy_secret: str | None = Header(default=None, alias="X-RapidAPI-Proxy-Secret"),
    x_rapidapi_user: str | None = Header(default=None, alias="X-RapidAPI-User"),
    db: Session = Depends(get_db),
) -> Caller:
    """Authenticate via RapidAPI's proxy header if configured and present,
    otherwise fall back to our own Bearer API key."""
    if settings.rapidapi_proxy_secret and x_rapidapi_proxy_secret:
        if not secrets.compare_digest(x_rapidapi_proxy_secret, settings.rapidapi_proxy_secret):
            raise UnauthorizedError("Invalid RapidAPI proxy secret.")
        identity = x_rapidapi_user or "unknown-rapidapi-user"
        return Caller(source="rapidapi", rate_limit_key=f"rapidapi:{identity}", api_key_id=None, plan="rapidapi")

    return _authenticate_direct_key(credentials, db)
