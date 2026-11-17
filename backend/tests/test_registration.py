import pytest

from app.services.registration import InvalidRegistration, normalise_registration


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("AB12 CDE", "AB12CDE"),  # current format
        ("ab12cde", "AB12CDE"),  # lowercase, no space
        ("  ab-12-cde ", "AB12CDE"),  # dashes and padding
        ("A123 BCD", "A123BCD"),  # prefix
        ("ABC 123D", "ABC123D"),  # suffix
        ("ABZ 1234", "ABZ1234"),  # Northern Ireland
        ("1 ABC", "1ABC"),  # dateless reversed
    ],
)
def test_valid_uk_registrations(raw, expected):
    assert normalise_registration(raw, "GB") == expected


@pytest.mark.parametrize(
    "raw",
    ["", "   ", "AB12CDEF", "12345678", "AB!2CDE", "ABCDEFG", "A"],
)
def test_invalid_uk_registrations(raw):
    with pytest.raises(InvalidRegistration):
        normalise_registration(raw, "GB")


@pytest.mark.parametrize(
    ("raw", "country", "expected"),
    [
        ("241-D-12345", "IE", "241D12345"),
        ("AB-123-CD", "FR", "AB123CD"),
        ("AB 123 CD", "IT", "AB123CD"),
        ("1234 BCD", "ES", "1234BCD"),
        ("M-AB 1234", "DE", "MAB1234"),  # generic check
        ("XX-99-ZZ", "NL", "XX99ZZ"),  # generic check
    ],
)
def test_valid_eu_registrations(raw, country, expected):
    assert normalise_registration(raw, country) == expected


@pytest.mark.parametrize(
    ("raw", "country"),
    [
        ("1234 AEI", "ES"),  # Spanish plates never use vowels
        ("ABC123", "FR"),
        ("ABCDEF", "DE"),  # generic check needs a digit
        ("A1B2C3D4E5F6", "PL"),  # too long
    ],
)
def test_invalid_eu_registrations(raw, country):
    with pytest.raises(InvalidRegistration):
        normalise_registration(raw, country)


def test_unknown_country_rejected():
    with pytest.raises(InvalidRegistration):
        normalise_registration("AB12CDE", "US")


def test_error_message_is_helpful():
    with pytest.raises(InvalidRegistration, match="isn't a valid United Kingdom registration"):
        normalise_registration("ZZZZZZZ", "GB")
