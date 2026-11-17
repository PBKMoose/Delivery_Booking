"""Alembic runtime config: connects migrations to our app's models and settings."""

from logging.config import fileConfig

import app.models  # noqa: F401  (registers all tables on Base.metadata)
from alembic import context
from app.core.config import settings
from app.core.db import Base, make_engine
from app.models.types import UTCDateTime

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Compare migrations against these table definitions.
target_metadata = Base.metadata


def render_item(type_, obj, autogen_context):
    """Write our custom column type into migration files as a standard type."""
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return "sa.DateTime(timezone=True)"
    return False  # default rendering for everything else


def _configure(**kwargs) -> None:
    context.configure(
        target_metadata=target_metadata,
        render_item=render_item,
        # SQLite can't ALTER most things in place; "batch" mode rebuilds the
        # table instead. Harmless on PostgreSQL.
        render_as_batch=True,
        **kwargs,
    )


def run_migrations_offline() -> None:
    _configure(url=settings.database_url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = make_engine(settings.database_url)
    with engine.connect() as connection:
        _configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
