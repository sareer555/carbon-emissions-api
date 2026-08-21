"""SQLAlchemy engine/session setup.

Works against SQLite out of the box (zero-cost local dev) and against
Postgres (Supabase/Neon free tier) when DATABASE_URL is set accordingly.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

# Render, Heroku, and some other hosts hand out `postgres://` connection
# strings, but SQLAlchemy's psycopg2 driver requires the `postgresql://`
# scheme. Normalize it so DATABASE_URL can be pasted in verbatim from those
# platforms' dashboards.
_database_url = settings.database_url
if _database_url.startswith("postgres://"):
    _database_url = _database_url.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if _database_url.startswith("sqlite") else {}

engine = create_engine(_database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they don't exist. Fine for v1; move to Alembic migrations
    once the schema needs to evolve without dropping data."""
    from app import models  # noqa: F401  (ensure models are registered)

    Base.metadata.create_all(bind=engine)
