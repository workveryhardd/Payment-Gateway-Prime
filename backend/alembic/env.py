"""Database migrations are disabled.

The backend now relies on a JSON file data store instead of SQLAlchemy,
so Alembic should no longer be executed. This file simply raises when
invoked so the reason is obvious if someone accidentally runs Alembic.
"""

raise RuntimeError(
    "Alembic migrations are disabled because the backend now uses a JSON data store."
)

