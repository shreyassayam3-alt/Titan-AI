"""Base contract for executable Titan skills."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, ClassVar


class Skill(ABC):
    """A self-contained capability with validation, execution, and rollback.

    Skills contain their domain behavior while the runtime owns permissions,
    lifecycle reporting, error handling, and plugin discovery.
    """

    name: ClassVar[str]
    required_permissions: ClassVar[frozenset[str]] = frozenset()
    sensitive: ClassVar[bool] = False

    @abstractmethod
    async def validate(self, input_data: Mapping[str, Any]) -> None:
        """Validate input before the runtime permits execution."""
        ...

    @abstractmethod
    async def execute(self, input_data: Mapping[str, Any]) -> Any:
        """Execute the skill and return its implementation-defined output."""
        ...

    @abstractmethod
    async def rollback(self, input_data: Mapping[str, Any], error: Exception) -> None:
        """Compensate for a failed execution when the skill can do so safely."""
        ...
