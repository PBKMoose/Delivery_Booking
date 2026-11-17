"""Turn validation and rule errors into one simple, form-friendly format:

    422  {"errors": {"registration": "'XYZ' isn't a valid ...", "mgw_kg": "..."}}

The frontend can then show each message next to the matching form field.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.services.bookings import BookingRuleError

FRIENDLY_MESSAGES = {
    "greater_than_equal": "Must be at least {ge}.",
    "less_than_equal": "Must be at most {le}.",
    "int_parsing": "Enter a whole number.",
    "enum": "Choose one of the options.",
    "missing": "This field is required.",
    "timezone_aware": "Time must include a timezone.",
}


def _message(error: dict) -> str:
    template = FRIENDLY_MESSAGES.get(error["type"])
    if template:
        return template.format(**error.get("ctx", {}))
    msg = error["msg"]
    return msg.removeprefix("Value error, ")  # pydantic prefixes our own messages


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors: dict[str, str] = {}
    for error in exc.errors():
        loc = [str(part) for part in error["loc"] if part != "body"]
        field = ".".join(loc) or "body"
        errors.setdefault(field, _message(error))  # keep the first error per field
    return JSONResponse(status_code=422, content={"errors": errors})


async def booking_rule_error_handler(_: Request, exc: BookingRuleError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"errors": {exc.field: exc.message}})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(BookingRuleError, booking_rule_error_handler)
