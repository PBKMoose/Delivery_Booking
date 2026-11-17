"""Importing this package registers every table with SQLAlchemy (and Alembic)."""

from app.models.booking import Booking
from app.models.company import Company
from app.models.vehicle import Vehicle

__all__ = ["Booking", "Company", "Vehicle"]
