from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.company import Company
from app.models.enums import BookingStatus, MovementType
from app.models.types import UTCDateTime, str_enum, utcnow
from app.models.vehicle import Vehicle


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Short human-friendly code, e.g. "BK-7F3K9Q". Will go on the QR code.
    reference: Mapped[str] = mapped_column(String(12), unique=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    movement_type: Mapped[MovementType] = mapped_column(str_enum(MovementType))
    slot_start: Mapped[datetime] = mapped_column(UTCDateTime(), index=True)
    slot_end: Mapped[datetime] = mapped_column(UTCDateTime())
    status: Mapped[BookingStatus] = mapped_column(
        str_enum(BookingStatus), default=BookingStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    company: Mapped[Company] = relationship()
    vehicle: Mapped[Vehicle] = relationship()
