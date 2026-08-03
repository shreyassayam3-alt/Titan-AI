"""Controlled blackboard-style workspace for collaborating agents."""

from typing import Any

from core.coordination.models import WorkspaceEntry


class SharedWorkspace:
    """Stores shared entries with owner-controlled read and write access."""

    def __init__(self) -> None:
        """Create an empty workspace."""
        self._entries: dict[str, WorkspaceEntry] = {}
        self._readers: dict[str, set[str]] = {}
        self._writers: dict[str, set[str]] = {}

    def put(self, key: str, value: Any, *, actor_id: str) -> WorkspaceEntry:
        """Create or update an entry when ``actor_id`` has write access."""
        current = self._entries.get(key)
        if current is not None and actor_id not in self._writers[key]:
            raise PermissionError(f"Agent '{actor_id}' cannot modify workspace entry '{key}'.")
        version = 1 if current is None else current.version + 1
        owner_id = actor_id if current is None else current.owner_id
        entry = WorkspaceEntry(key=key, value=value, owner_id=owner_id, version=version)
        self._entries[key] = entry
        self._readers.setdefault(key, {owner_id}).add(owner_id)
        self._writers.setdefault(key, {owner_id}).add(owner_id)
        return entry

    def get(self, key: str, *, actor_id: str) -> WorkspaceEntry | None:
        """Return an entry when ``actor_id`` has read access."""
        entry = self._entries.get(key)
        if entry is None:
            return None
        if actor_id not in self._readers[key]:
            raise PermissionError(f"Agent '{actor_id}' cannot read workspace entry '{key}'.")
        return entry

    def grant(self, key: str, *, owner_id: str, agent_id: str, write: bool = False) -> None:
        """Grant read access, and optionally write access, to an entry collaborator."""
        entry = self._entries.get(key)
        if entry is None:
            raise KeyError(f"Unknown workspace entry '{key}'.")
        if entry.owner_id != owner_id:
            raise PermissionError("Only the entry owner can grant workspace access.")
        self._readers[key].add(agent_id)
        if write:
            self._writers[key].add(agent_id)
