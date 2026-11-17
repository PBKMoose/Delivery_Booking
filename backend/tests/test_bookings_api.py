from datetime import UTC, date, datetime, timedelta

from app.services.slots import slots_for_day


def future_slot_start() -> str:
    """A real slot start ~30 days ahead, so the test never hits 'in the past'."""
    day = date.today() + timedelta(days=30)
    return slots_for_day(day)[4].start.isoformat()


def valid_payload(**overrides) -> dict:
    payload = {
        "registration_country": "GB",
        "registration": "ab12 cde",
        "vehicle_type": "artic",
        "mgw_kg": 44000,
        "movement_type": "drop_off",
        "slot_start": future_slot_start(),
    }
    payload.update(overrides)
    return payload


def test_create_booking(client):
    res = client.post("/api/bookings", json=valid_payload())
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["status"] == "pending"
    assert body["reference"].startswith("BK-")
    assert body["vehicle"]["registration"] == "AB12CDE"  # normalised
    assert body["vehicle"]["vehicle_type"] == "artic"


def test_booked_vehicle_is_reused(client, db_session):
    from app.models import Vehicle

    client.post("/api/bookings", json=valid_payload())
    client.post("/api/bookings", json=valid_payload(registration="AB12CDE", mgw_kg=40000))
    vehicles = db_session.query(Vehicle).all()
    assert len(vehicles) == 1
    assert vehicles[0].mgw_kg == 40000  # updated to the latest value entered


def test_list_bookings_returns_created_booking(client):
    client.post("/api/bookings", json=valid_payload())
    res = client.get("/api/bookings")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_invalid_registration_gives_field_error(client):
    res = client.post("/api/bookings", json=valid_payload(registration="NOT A REG!"))
    assert res.status_code == 422
    assert "registration" in res.json()["errors"]


def test_eu_registration_accepted(client):
    res = client.post(
        "/api/bookings",
        json=valid_payload(registration_country="FR", registration="AB-123-CD"),
    )
    assert res.status_code == 201, res.text


def test_unsupported_country_rejected(client):
    res = client.post("/api/bookings", json=valid_payload(registration_country="US"))
    assert res.status_code == 422
    assert res.json()["errors"]["registration_country"] == "Choose a UK or EU country."


def test_mgw_out_of_range(client):
    res = client.post("/api/bookings", json=valid_payload(mgw_kg=60000))
    assert res.status_code == 422
    assert res.json()["errors"]["mgw_kg"] == "Must be at most 44000."


def test_unknown_vehicle_type(client):
    res = client.post("/api/bookings", json=valid_payload(vehicle_type="bus"))
    assert res.status_code == 422
    assert res.json()["errors"]["vehicle_type"] == "Choose one of the options."


def test_time_that_is_not_a_slot_rejected(client):
    off_grid = datetime.fromisoformat(future_slot_start()) + timedelta(minutes=7)
    res = client.post("/api/bookings", json=valid_payload(slot_start=off_grid.isoformat()))
    assert res.status_code == 422
    assert res.json()["errors"]["slot_start"] == "That isn't a valid time slot."


def test_past_slot_rejected(client):
    past = slots_for_day(date.today() - timedelta(days=1))[0].start.isoformat()
    res = client.post("/api/bookings", json=valid_payload(slot_start=past))
    assert res.status_code == 422
    assert "In the past" in res.json()["errors"]["slot_start"]


def test_slot_without_timezone_rejected(client):
    naive = datetime.now(UTC).replace(tzinfo=None).isoformat()
    res = client.post("/api/bookings", json=valid_payload(slot_start=naive))
    assert res.status_code == 422
    assert "slot_start" in res.json()["errors"]


def test_slots_endpoint(client):
    day = (date.today() + timedelta(days=30)).isoformat()
    res = client.get(f"/api/slots?day={day}")
    assert res.status_code == 200
    body = res.json()
    assert body["timezone"] == "Europe/London"
    assert len(body["slots"]) == 22


def test_booking_options(client):
    body = client.get("/api/booking-options").json()
    assert [o["value"] for o in body["vehicle_types"]] == ["car", "van", "rigid", "artic"]
    assert body["countries"][0] == {"value": "GB", "label": "United Kingdom"}
    assert len(body["countries"]) == 28  # UK + 27 EU
