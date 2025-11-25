"""
Legacy database helpers were kept for backwards compatibility.
The project now uses a JSON file store so this module intentionally
exposes no working database session.
"""

Base = None
SessionLocal = None

def get_db():
    raise RuntimeError("Database layer removed; use the JSON data store instead.")
