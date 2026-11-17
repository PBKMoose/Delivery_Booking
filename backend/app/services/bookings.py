"""Business rules for creating and listing bookings.

Routers stay thin (HTTP in, HTTP out); the actual rules live here so they can be
reused (e.g. by the admin portal) and tested without HTTP.
"""

import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, Company, Vehicle
from app.schemas.booking import BookingCreate
from app.services.slots import find_slot


class BookingRuleError(Exception):
    """A booking broke a business rule. `field` says which input to blame."""

    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field
        self.message = message


# No 0/O or 1/I so references are easy to read out over the phone.
REFERENCE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def _new_reference(db: Session) -> str:
    while True:
        ref = "BK-" + "".join(secrets.choice(REFERENCE_ALPHABET) for _ in range(6))
        if db.scalar(select(Booking.id).where(Booking.reference == ref)) is None:
            return ref


def _get_or_create_vehicle(db: Session, company: Company, data: BookingCreate) -> Vehicle:
    """Reuse the company's existing vehicle record for this registration, if any.

    Type and MGW are updated to the latest values entered, so a correction made
    on a new booking fixes the stored vehicle too.
    """
    vehicle = db.scalar(
        select(Vehicle).where(
            Vehicle.company_id == company.id,
            Vehicle.registration == data.registration,
            Vehicle.registration_country == data.registration_country,
        )
    )
    if vehicle is None:
        vehicle = Vehicle(
            company_id=company.id,
            registration=data.registration,
            registration_country=data.registration_country,
        )
        db.add(vehicle)
    vehicle.vehicle_type = data.vehicle_type
    vehicle.mgw_kg = data.mgw_kg
    return vehicle


def create_booking(
    db: Session, company: Company, data: BookingCreate, now: datetime | None = None
) -> Booking:
    slot = find_slot(data.slot_start, now)
    if slot is None:
        raise BookingRuleError("slot_start", "That isn't a valid time slot.")
    if not slot.available:
        raise BookingRuleError("slot_start", f"That slot can't be booked: {slot.reason}.")

    # TODO (capacity slice): check vehicle-type limits for this slot here.

    vehicle = _get_or_create_vehicle(db, company, data)
    booking = Booking(
        reference=_new_reference(db),
        company_id=company.id,
        vehicle=vehicle,
        movement_type=data.movement_type,
        slot_start=slot.start,
        slot_end=slot.end,
    )
    db.add(booking)
    db.commit()  # saves the vehicle and booking together, or neither
    db.refresh(booking)
    return booking


def list_bookings(db: Session, company: Company) -> list[Booking]:
    return list(
        db.scalars(
            select(Booking).where(Booking.company_id == company.id).order_by(Booking.slot_start)
        )
    )
