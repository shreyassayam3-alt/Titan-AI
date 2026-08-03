"""Background mission worker with a testable single execution cycle."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from core.kernel.config import KernelConfig
from core.kernel.decision import DecisionEngine
from core.kernel.missions import Mission, MissionQueue

type MissionHandler = Callable[[Mission], Awaitable[Any]]


class BackgroundWorker:
    """Polls a mission queue and runs one selected mission at a time."""

    def __init__(
        self,
        queue: MissionQueue,
        decision_engine: DecisionEngine,
        config: KernelConfig,
        handler: MissionHandler,
        persist: Callable[[], None],
    ) -> None:
        """Initialize the worker with a mission handler and persistence callback."""
        self._queue = queue
        self._decision_engine = decision_engine
        self._config = config
        self._handler = handler
        self._persist = persist
        self._running = False

    async def run_once(self) -> bool:
        """Execute one selected mission and return whether work was performed."""
        mission = self._decision_engine.next_mission(self._queue, self._config)
        if mission is None:
            return False
        self._queue.mark_running(mission.id)
        self._persist()
        try:
            await self._handler(mission)
        except Exception as error:
            self._queue.fail(mission.id, error)
        else:
            self._queue.complete(mission.id)
        self._persist()
        return True

    async def run(self) -> None:
        """Continuously poll the mission queue until :meth:`stop` is called."""
        self._running = True
        while self._running:
            await self.run_once()
            await asyncio.sleep(self._config.execution_interval_seconds)

    def stop(self) -> None:
        """Request that the continuous polling loop exits after its current cycle."""
        self._running = False
