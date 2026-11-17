from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.company import Company
from app.models.enums import VehicleType
from app.models.types import UTCDateTime, str_enum, utcnow


class Vehicle(Base):
    """A vehicle owned/used by a company. Reused across many bookings."""

    __tablename__ = "vehicles"
    # The same company can't have the same registration twice.
    __table_args__ = (UniqueConstraint("company_id", "registration", "registration_country"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    # Stored normalised: uppercase, no spaces (e.g. "AB12CDE").
    registration: Mapped[str] = mapped_column(String(15))
    registration_country: Mapped[str] = mapped_column(String(2))  # ISO code, e.g. "GB"
    vehicle_type: Mapped[VehicleType] = mapped_column(str_enum(VehicleType))
    mgw_kg: Mapped[int]  # maximum gross weight in kilograms
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    company: Mapped[Company] = relationship()
