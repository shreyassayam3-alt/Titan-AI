"""Abstract contract for an external-tool registry."""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any


class ToolRegistry(ABC):
    """Discovers external tools and delegates calls to named capabilities.

    Implementations are responsible for tool transport, authentication,
    validation, and error handling; this interface only defines their boundary.
    """

    @abstractmethod
    async def discover(self, *, query: str | None = None) -> Sequence[Any]:
        """Return tools available to the caller, optionally filtered by ``query``."""
        ...

    @abstractmethod
    async def invoke(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
        *,
        context: Any | None = None,
    ) -> Any:
        """Invoke ``tool_name`` with ``arguments`` and return its result."""
        ...
