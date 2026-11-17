"""Fixed lists of allowed values.

A StrEnum is a set of named constants that are also plain strings, so they
store in the database and travel as JSON as e.g. "artic".
"""

from enum import StrEnum


class VehicleType(StrEnum):
    CAR = "car"
    VAN = "van"
    RIGID = "rigid"
    ARTIC = "artic"


VEHICLE_TYPE_LABELS = {
    VehicleType.CAR: "Car",
    VehicleType.VAN: "Van",
    VehicleType.RIGID: "Rigid lorry",
    VehicleType.ARTIC: "Articulated lorry (artic)",
}


class MovementType(StrEnum):
    DROP_OFF = "drop_off"
    COLLECTION = "collection"


MOVEMENT_TYPE_LABELS = {
    MovementType.DROP_OFF: "Drop-off",
    MovementType.COLLECTION: "Collection",
}


class BookingStatus(StrEnum):
    PENDING = "pending"  # waiting for admin approval
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    NO_SHOW = "no_show"
