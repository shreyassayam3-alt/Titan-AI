"""Abstract contract for publishing and subscribing to events."""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

type EventHandler = Callable[[Any], Awaitable[None]]


class EventBus(ABC):
    """Delivers named events to registered asynchronous handlers."""

    @abstractmethod
    async def publish(self, event_name: str, payload: Any) -> None:
        """Publish ``payload`` under ``event_name``."""
        ...

    @abstractmethod
    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Register ``handler`` to receive future events named ``event_name``."""
        ...

    @abstractmethod
    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Remove ``handler`` from the subscribers for ``event_name``."""
        ...
