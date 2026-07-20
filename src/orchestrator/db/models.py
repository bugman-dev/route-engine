"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from orchestrator.db import Base

# SQLite requires INTEGER PK for AUTOINCREMENT; MySQL keeps BIGINT.
_PK = BigInteger().with_variant(Integer, "sqlite")


class WaypointRow(Base):
    __tablename__ = "waypoints"
    __table_args__ = (UniqueConstraint("external_id", name="uq_waypoints_external_id"),)

    id: Mapped[int] = mapped_column(_PK, primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    demand: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_depot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class VehicleRow(Base):
    __tablename__ = "vehicles"
    __table_args__ = (UniqueConstraint("external_id", name="uq_vehicles_external_id"),)

    id: Mapped[int] = mapped_column(_PK, primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    number: Mapped[str] = mapped_column(String(64), nullable=False)
    operator: Mapped[str] = mapped_column(String(128), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class RouteGenerationRow(Base):
    __tablename__ = "route_generations"
    __table_args__ = (
        Index("ix_route_generations_service_date_generated", "service_date", "generated_at"),
    )

    id: Mapped[int] = mapped_column(_PK, primary_key=True, autoincrement=True)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    cost_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    was_regenerated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    engine_request_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    engine_response_json: Mapped[dict] = mapped_column(JSON, nullable=False)
