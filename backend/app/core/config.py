"""Application settings.

Every setting has a working default so the app runs with zero setup.
To point at real infrastructure later (e.g. PostgreSQL), set environment
variables or create backend/.env — see backend/.env.example.
"""

from datetime import time
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    app_name: str = "Delivery Booking API"
    environment: str = "development"

    # Default: a local SQLite file, created automatically. No database server needed.
    # Later: postgresql+psycopg://user:password@host:5432/delivery_booking
    database_url: str = f"sqlite:///{BACKEND_DIR / 'dev.db'}"

    # Where the Next.js frontend runs (for CORS).
    frontend_origin: str = "http://localhost:3000"

    # --- Booking slot defaults ---------------------------------------------
    # PLACEHOLDERS: these become per-site settings edited in the admin portal.
    site_timezone: str = "Europe/London"
    slot_minutes: int = 30
    day_start: time = time(7, 0)  # first slot starts at 07:00 local time
    day_end: time = time(18, 0)  # last slot must end by 18:00 local time


settings = Settings()
