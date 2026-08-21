"""API key authentication + monthly usage-quota enforcement.

Auth: `Authorization: Bearer <key>` header. Keys are stored hashed (SHA-256)
so the plaintext key is never persisted server-side after creation — see
app/scripts/create_api_key.py.
"""
import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.errors import QuotaExceededError, UnauthorizedError
from app.models import ApiKey

settings = get_settings()


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


def get_api_key(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> ApiKey:
    """Validate the Bearer API key and enforce the caller's monthly quota.

    Raises UnauthorizedError (401) for missing/invalid/inactive keys, and
    QuotaExceededError (429) once the plan's monthly call limit is reached.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or malformed Authorization header. Expected 'Bearer <api_key>'.")

    plaintext_key = authorization.split(" ", 1)[1].strip()
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
    return api_key
