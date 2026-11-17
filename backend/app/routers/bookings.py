"""Contractor-facing booking endpoints.

Thin on purpose: each endpoint just unpacks the request, calls a service, and
returns the result. Rules live in app/services/.
"""

from datetime import date

from fastapi import APIRouter, status

from app.core.config import settings
from app.core.db import DbSession
from app.core.deps import CurrentCompany
from app.models.enums import MOVEMENT_TYPE_LABELS, VEHICLE_TYPE_LABELS
from app.schemas.booking import (
    MAX_MGW_KG,
    MIN_MGW_KG,
    BookingCreate,
    BookingOptionsOut,
    BookingOut,
    DaySlotsOut,
    Option,
    SlotOut,
)
from app.services import bookings as booking_service
from app.services.registration import COUNTRIES
from app.services.slots import slots_for_day

router = APIRouter(tags=["bookings"])


@router.get("/booking-options")
def booking_options() -> BookingOptionsOut:
    """Dropdown contents for the booking form, so the lists live in one place."""
    return BookingOptionsOut(
        vehicle_types=[Option(value=v, label=label) for v, label in VEHICLE_TYPE_LABELS.items()],
        movement_types=[Option(value=v, label=label) for v, label in MOVEMENT_TYPE_LABELS.items()],
        # UK first, then EU countries alphabetically.
        countries=[Option(value="GB", label=COUNTRIES["GB"].name)]
        + sorted(
            (Option(value=code, label=r.name) for code, r in COUNTRIES.items() if code != "GB"),
            key=lambda o: o.label,
        ),
        mgw_min_kg=MIN_MGW_KG,
        mgw_max_kg=MAX_MGW_KG,
    )


@router.get("/slots")
def get_slots(day: date) -> DaySlotsOut:
    """Time slots for one day. Example: GET /api/slots?day=2026-11-20"""
    return DaySlotsOut(
        timezone=settings.site_timezone,
        slots=[SlotOut(**vars(s)) for s in slots_for_day(day)],
    )


@router.post("/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingCreate, db: DbSession, company: CurrentCompany) -> BookingOut:
    booking = booking_service.create_booking(db, company, data)
    return BookingOut.model_validate(booking)


@router.get("/bookings")
def list_bookings(db: DbSession, company: CurrentCompany) -> list[BookingOut]:
    """The current company's bookings only, never anyone else's."""
    return [BookingOut.model_validate(b) for b in booking_service.list_bookings(db, company)]
