"""Vehicle registration (number plate) validation for UK and EU vehicles.

Usage:
    normalise_registration("ab12 cde", "GB")  -> "AB12CDE"
    normalise_registration("nope!", "GB")     -> raises InvalidRegistration

Strict format rules exist for the UK and a few EU countries. Every other EU
country gets a looser sanity check, because formats vary a lot by country
(and some, like Germany's, can't be checked reliably once spaces are removed).
"""

import re
from dataclasses import dataclass, field


class InvalidRegistration(ValueError):
    """Raised with a message that is safe to show to the user."""


@dataclass(frozen=True)
class CountryRules:
    name: str
    patterns: list[str] = field(default_factory=list)  # empty = generic check only
    examples: str = ""


# Patterns are matched against the normalised registration (no spaces/dashes).
GB_PATTERNS = [
    r"[A-Z]{2}[0-9]{2}[A-Z]{3}",  # current, 2001+:          AB12 CDE
    r"[A-Z][0-9]{1,3}[A-Z]{3}",  # prefix, 1983-2001:        A123 BCD
    r"[A-Z]{3}[0-9]{1,3}[A-Z]",  # suffix, 1963-1983:        ABC 123D
    r"[A-Z]{1,3}[0-9]{1,4}",  # dateless & N. Ireland:   ABC 1234, ABZ 1234
    r"[0-9]{1,4}[A-Z]{1,3}",  # dateless, reversed:       1234 AB
]

COUNTRIES: dict[str, CountryRules] = {
    "GB": CountryRules("United Kingdom", GB_PATTERNS, "AB12 CDE, A123 BCD, ABC 123D"),
    # --- EU countries with strict rules ---
    "IE": CountryRules("Ireland", [r"[0-9]{2,3}[A-Z]{1,2}[0-9]{1,6}"], "241-D-12345, 12-KY-1"),
    "FR": CountryRules(
        "France",
        [
            r"[A-Z]{2}[0-9]{3}[A-Z]{2}",  # 2009+: AB-123-CD
            r"[0-9]{1,4}[A-Z]{1,3}(?:[0-9]{2}|2A|2B)",  # pre-2009: 1234 AB 75
        ],
        "AB-123-CD",
    ),
    "IT": CountryRules("Italy", [r"[A-Z]{2}[0-9]{3}[A-Z]{2}"], "AB 123 CD"),
    "ES": CountryRules(
        "Spain",
        [
            r"[0-9]{4}[BCDFGHJKLMNPRSTVWXYZ]{3}",  # 2000+: 1234 BCD
            r"[A-Z]{1,2}[0-9]{4}[A-Z]{0,2}",  # provincial: M-1234-AB
        ],
        "1234 BCD",
    ),
    # --- other EU countries: generic check ---
    "AT": CountryRules("Austria"),
    "BE": CountryRules("Belgium"),
    "BG": CountryRules("Bulgaria"),
    "HR": CountryRules("Croatia"),
    "CY": CountryRules("Cyprus"),
    "CZ": CountryRules("Czechia"),
    "DK": CountryRules("Denmark"),
    "EE": CountryRules("Estonia"),
    "FI": CountryRules("Finland"),
    "DE": CountryRules("Germany"),
    "GR": CountryRules("Greece"),
    "HU": CountryRules("Hungary"),
    "LV": CountryRules("Latvia"),
    "LT": CountryRules("Lithuania"),
    "LU": CountryRules("Luxembourg"),
    "MT": CountryRules("Malta"),
    "NL": CountryRules("Netherlands"),
    "PL": CountryRules("Poland"),
    "PT": CountryRules("Portugal"),
    "RO": CountryRules("Romania"),
    "SK": CountryRules("Slovakia"),
    "SI": CountryRules("Slovenia"),
    "SE": CountryRules("Sweden"),
}

# Generic EU check: 2-10 letters/digits (incl. Nordic/German letters), at least one digit.
GENERIC_PATTERN = r"(?=.*[0-9])[A-Z0-9ÄÖÜÅ]{2,10}"

# Characters people commonly type between parts of a plate; we strip them.
SEPARATORS = re.compile(r"[\s\-.·]")
ALLOWED_CHARS = re.compile(r"[A-Z0-9ÄÖÜÅ]+")


def normalise_registration(raw: str, country: str) -> str:
    """Return the registration in canonical form, or raise InvalidRegistration."""
    rules = COUNTRIES.get(country)
    if rules is None:
        raise InvalidRegistration(f"Unsupported country code: {country!r}")

    reg = SEPARATORS.sub("", raw.strip().upper())

    if not reg:
        raise InvalidRegistration("Enter a registration.")
    if not ALLOWED_CHARS.fullmatch(reg):
        raise InvalidRegistration("Registration can only contain letters and numbers.")

    patterns = rules.patterns or [GENERIC_PATTERN]
    if not any(re.fullmatch(p, reg) for p in patterns):
        hint = f" Examples: {rules.examples}." if rules.examples else ""
        raise InvalidRegistration(f"'{raw.strip()}' isn't a valid {rules.name} registration.{hint}")
    return reg
