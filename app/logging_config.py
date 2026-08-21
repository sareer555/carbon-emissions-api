"""Request logging: writes one row per calculation request to `request_log`.

Deliberately does NOT log customer-identifying data (IP, raw API key,
request body contents) beyond the fuel/region key and which API key made
the call — that's enough to see which factors/regions are most requested
(see build brief section 6) without building a surveillance log.
"""
import logging

from sqlalchemy.orm import Session

from app.models import RequestLog

logger = logging.getLogger("carbon_api")
logging.basicConfig(level=logging.INFO)


def log_request(
    db: Session,
    endpoint: str,
    api_key_id: int | None,
    status_code: int,
    category: str | None = None,
    factor_key: str | None = None,
) -> None:
    try:
        db.add(
            RequestLog(
                api_key_id=api_key_id,
                endpoint=endpoint,
                category=category,
                factor_key=factor_key,
                status_code=status_code,
            )
        )
        db.commit()
    except Exception:  # never let logging break the actual request
        logger.exception("Failed to write request_log row for %s", endpoint)
        db.rollback()
