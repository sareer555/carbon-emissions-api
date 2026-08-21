"""SQLAlchemy ORM models."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)  # 'scope1_fuel' | 'scope2_grid'
    key: Mapped[str] = mapped_column(String, nullable=False, index=True)  # e.g. 'natural_gas' or 'US-CAMX'
    factor: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)  # kg CO2e per unit
    unit: Mapped[str] = mapped_column(String, nullable=False)  # e.g. 'therms', 'kwh', 'gallons'
    source: Mapped[str] = mapped_column(String, nullable=False)
    source_year: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = ()


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(String, nullable=True)  # human-readable owner/customer name
    plan: Mapped[str] = mapped_column(String, nullable=False, default="free")
    calls_this_period: Mapped[int] = mapped_column(Integer, default=0)
    period_reset_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    request_logs: Mapped[list["RequestLog"]] = relationship(back_populates="api_key")


class RequestLog(Base):
    __tablename__ = "request_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_key_id: Mapped[int | None] = mapped_column(ForeignKey("api_keys.id"), nullable=True)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # scope1_fuel | scope2_grid
    factor_key: Mapped[str | None] = mapped_column(String, nullable=True)  # fuel_type or region
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    api_key: Mapped["ApiKey | None"] = relationship(back_populates="request_logs")
