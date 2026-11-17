"""Time slot generation.

Slots are generated on the fly from settings (start/end of day, slot length)
rather than stored, so changing the settings changes the slots immediately.

All times are handled as timezone-aware datetimes. Slots are laid out in the
site's local time (07:00, 07:30, ...) and converted to UTC for storage.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import settings


@dataclass(frozen=True)
class Slot:
    start: datetime  # UTC
    end: datetime  # UTC
    available: bool
    reason: str | None = None  # why it's unavailable, if it is


def site_tz() -> ZoneInfo:
    return ZoneInfo(settings.site_timezone)


def slots_for_day(day: date, now: datetime | None = None) -> list[Slot]:
    """Every slot on `day` (a date in the site's local timezone)."""
    now = now or datetime.now(UTC)
    tz = site_tz()
    length = timedelta(minutes=settings.slot_minutes)

    start = datetime.combine(day, settings.day_start, tzinfo=tz)
    day_end = datetime.combine(day, settings.day_end, tzinfo=tz)

    slots: list[Slot] = []
    while start + length <= day_end:
        end = start + length
        in_past = start <= now
        slots.append(
            Slot(
                start=start.astimezone(UTC),
                end=end.astimezone(UTC),
                available=not in_past,
                reason="In the past" if in_past else None,
            )
        )
        start = end
    return slots


def find_slot(slot_start: datetime, now: datetime | None = None) -> Slot | None:
    """Return the slot that begins exactly at `slot_start`, or None if there isn't one."""
    local_day = slot_start.astimezone(site_tz()).date()
    for slot in slots_for_day(local_day, now):
        if slot.start == slot_start:
            return slot
    return None
