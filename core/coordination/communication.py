"""Agent message passing over the Titan EventBus."""

from collections.abc import Awaitable, Callable

from core.coordination.models import AgentMessage
from core.events import EventBus

type MessageHandler = Callable[[AgentMessage], Awaitable[None]]


class AgentCommunicationLayer:
    """Publishes direct and broadcast messages through standard event channels."""

    def __init__(self, event_bus: EventBus) -> None:
        """Initialize communication on the supplied EventBus."""
        self._event_bus = event_bus

    async def send(self, message: AgentMessage) -> None:
        """Publish a message to its topic and optional recipient-specific channel."""
        await self._event_bus.publish(f"agents.messages.{message.topic}", message)
        if message.recipient_id is not None:
            await self._event_bus.publish(f"agents.inbox.{message.recipient_id}", message)

    def subscribe(self, agent_id: str, handler: MessageHandler) -> None:
        """Subscribe an agent handler to its direct inbox channel."""
        self._event_bus.subscribe(f"agents.inbox.{agent_id}", handler)
