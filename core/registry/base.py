"""Abstract contract for registering and resolving named objects."""

from abc import ABC, abstractmethod
from typing import Any


class Registry(ABC):
    """Associates string names with implementation-defined objects."""

    @abstractmethod
    def register(self, name: str, value: Any) -> None:
        """Associate ``name`` with ``value``."""
        ...

    @abstractmethod
    def resolve(self, name: str) -> Any:
        """Return the object associated with ``name``."""
        ...

    @abstractmethod
    def unregister(self, name: str) -> None:
        """Remove the object associated with ``name`` if supported."""
        ...
