"""Durable JSON state storage for recoverable kernel execution."""

import json
from pathlib import Path
from typing import Any


class StateManager:
    """Persists JSON-compatible kernel state and restores it after restart."""

    def __init__(self, path: Path) -> None:
        """Configure the state file location without creating it eagerly."""
        self._path = path

    def save(self, state: dict[str, Any]) -> None:
        """Atomically replace the persisted state with ``state``."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._path.with_suffix(f"{self._path.suffix}.tmp")
        temporary_path.write_text(
            json.dumps(state, default=str, indent=2, sort_keys=True), encoding="utf-8"
        )
        temporary_path.replace(self._path)

    def load(self) -> dict[str, Any]:
        """Return persisted state, or an empty state when none exists yet."""
        if not self._path.exists():
            return {}
        data = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Kernel state must contain a JSON object.")
        return data
