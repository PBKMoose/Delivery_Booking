"""The shapes of data the booking API accepts (requests) and returns (responses).

Pydantic checks every request against these classes *before* our code runs.
If anything is wrong, the API replies 422 with a message per field.
"""

from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field, ValidationInfo, field_validator

from app.models.enums import BookingStatus, MovementType, VehicleType
from app.services.registration import COUNTRIES, InvalidRegistration, normalise_registration

MIN_MGW_KG = 500
MAX_MGW_KG = 44_000  # UK legal maximum for an articulated lorry


# ---------- Requests -------------------------------------------------------


class BookingCreate(BaseModel):
    # NB: field order matters: registration_country is validated first so the
    # registration validator below can use it.
    registration_country: str = "GB"
    registration: str
    vehicle_type: VehicleType
    mgw_kg: int = Field(ge=MIN_MGW_KG, le=MAX_MGW_KG)
    movement_type: MovementType
    slot_start: AwareDatetime  # must include a timezone, e.g. 2026-11-20T09:00:00Z

    @field_validator("registration_country")
    @classmethod
    def country_supported(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in COUNTRIES:
            raise ValueError("Choose a UK or EU country.")
        return value

    @field_validator("registration")
    @classmethod
    def registration_valid(cls, value: str, info: ValidationInfo) -> str:
        country = info.data.get("registration_country")
        if country is None:  # country itself was invalid; that error is enough
            return value
        try:
            return normalise_registration(value, country)
        except InvalidRegistration as exc:
            raise ValueError(str(exc)) from None


# ---------- Responses ------------------------------------------------------


class VehicleOut(BaseModel):
    registration: str
    registration_country: str
    vehicle_type: VehicleType
    mgw_kg: int

    model_config = {"from_attributes": True}  # allow building from a DB object


class BookingOut(BaseModel):
    id: int
    reference: str
    status: BookingStatus
    movement_type: MovementType
    slot_start: datetime
    slot_end: datetime
    created_at: datetime
    vehicle: VehicleOut

    model_config = {"from_attributes": True}


class SlotOut(BaseModel):
    start: datetime
    end: datetime
    available: bool
    reason: str | None = None


class DaySlotsOut(BaseModel):
    timezone: str
    slots: list[SlotOut]


class Option(BaseModel):
    value: str
    label: str


class BookingOptionsOut(BaseModel):
    """Everything the booking form needs to draw its dropdowns."""

    vehicle_types: list[Option]
    movement_types: list[Option]
    countries: list[Option]
    mgw_min_kg: int
    mgw_max_kg: int
