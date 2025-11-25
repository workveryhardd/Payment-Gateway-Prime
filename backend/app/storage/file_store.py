from __future__ import annotations

import copy
import json
import threading
from pathlib import Path
from typing import Any, Callable, Dict, TypeVar

T = TypeVar("T")


def _default_state() -> Dict[str, Any]:
    """Create a fresh default state for the file store."""
    return {
        "users": [],
        "deposits": [],
        "payment_accounts": [],
        "incoming_ledger": [],
        "counters": {
            "users": 0,
            "deposits": 0,
            "payment_accounts": 0,
            "incoming_ledger": 0,
        },
    }


class FileStore:
    """
    Minimal JSON-backed store so the app can persist data without a database.
    Provides simple read/write primitives guarded by a threading lock.
    """

    def __init__(self, file_path: str):
        self._path = Path(file_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self._path.exists():
            with self._path.open("r", encoding="utf-8") as handle:
                try:
                    return json.load(handle)
                except json.JSONDecodeError:
                    # Fall back to a clean state if the file is corrupted.
                    return _default_state()
        return _default_state()

    def _save(self) -> None:
        tmp_path = self._path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(self._data, handle, indent=2)
        tmp_path.replace(self._path)

    def read(self) -> Dict[str, Any]:
        """Return a deep copy of the in-memory data."""
        with self._lock:
            return copy.deepcopy(self._data)

    def write(self, mutator: Callable[[Dict[str, Any]], T]) -> T:
        """
        Apply a mutation function to the in-memory data and persist it.
        The mutator receives the live data dict and should mutate in-place.
        Returns a deep copy of whatever the mutator returns.
        """
        with self._lock:
            result = mutator(self._data)
            self._save()
            return copy.deepcopy(result)


