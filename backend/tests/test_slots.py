from datetime import UTC, date, datetime

from app.services.slots import find_slot, slots_for_day

WINTER_DAY = date(2026, 12, 1)  # GMT: UK time == UTC
SUMMER_DAY = date(2026, 7, 1)  # BST: UK time == UTC+1
LONG_AGO = datetime(2020, 1, 1, tzinfo=UTC)


def test_day_has_22_half_hour_slots_from_7_to_18():
    slots = slots_for_day(WINTER_DAY, now=LONG_AGO)
    assert len(slots) == 22  # 07:00 .. 17:30
    assert slots[0].start == datetime(2026, 12, 1, 7, 0, tzinfo=UTC)
    assert slots[-1].end == datetime(2026, 12, 1, 18, 0, tzinfo=UTC)


def test_summer_slots_respect_british_summer_time():
    first = slots_for_day(SUMMER_DAY, now=LONG_AGO)[0]
    assert first.start == datetime(2026, 7, 1, 6, 0, tzinfo=UTC)  # 07:00 BST


def test_past_slots_are_unavailable():
    now = datetime(2026, 12, 1, 9, 10, tzinfo=UTC)
    slots = slots_for_day(WINTER_DAY, now=now)
    by_start = {s.start.hour * 60 + s.start.minute: s for s in slots}
    assert by_start[9 * 60].available is False  # 09:00 already started
    assert by_start[9 * 60 + 30].available is True  # 09:30 still ahead
    assert by_start[9 * 60].reason == "In the past"


def test_find_slot_only_matches_real_slot_starts():
    assert find_slot(datetime(2026, 12, 1, 9, 30, tzinfo=UTC), now=LONG_AGO) is not None
    assert find_slot(datetime(2026, 12, 1, 9, 15, tzinfo=UTC), now=LONG_AGO) is None
    assert find_slot(datetime(2026, 12, 1, 18, 0, tzinfo=UTC), now=LONG_AGO) is None
