"""Custom column types."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """A date+time column that is always stored and returned in UTC.

    Why: SQLite has no real timezone support and would silently drop it, while
    PostgreSQL stores it properly. This column type makes both behave the same:
    you always get back a timezone-aware UTC datetime.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):  # Python -> DB
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Refusing to store a datetime without a timezone")
        value = value.astimezone(UTC)
        return value.replace(tzinfo=None) if dialect.name == "sqlite" else value

    def process_result_value(self, value: datetime | None, dialect):  # DB -> Python
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


def str_enum(enum_cls: type[StrEnum]) -> Enum:
    """Store an enum as its plain text value (e.g. "artic"), not a DB-specific type."""
    return Enum(
        enum_cls,
        native_enum=False,
        length=20,
        values_callable=lambda e: [member.value for member in e],
    )


def utcnow() -> datetime:
    return datetime.now(UTC)
