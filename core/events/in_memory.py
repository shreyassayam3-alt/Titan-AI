"""In-memory event bus implementation."""

from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from core.events.base import EventBus, EventHandler


class InMemoryEventBus(EventBus):
    """Delivers published events to local asynchronous subscribers in order."""

    def __init__(self) -> None:
        """Create a bus with no registered subscribers."""
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    async def publish(self, event_name: str, payload: Any) -> None:
        """Await each current subscriber registered for ``event_name``."""
        for handler in self._handlers_for(event_name):
            await handler(payload)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Register ``handler`` for the supplied event name."""
        self._subscribers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Remove ``handler`` if it is subscribed to ``event_name``."""
        handlers = self._subscribers.get(event_name)
        if handlers is not None and handler in handlers:
            handlers.remove(handler)

    def _handlers_for(self, event_name: str) -> Iterable[EventHandler]:
        """Provide a stable subscriber snapshot during event delivery."""
        return tuple(self._subscribers.get(event_name, ()))
