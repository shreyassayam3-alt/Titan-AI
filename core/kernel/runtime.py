"""Titan Kernel composition root."""

from typing import Any

from core.kernel.config import KernelConfig
from core.kernel.decision import DecisionEngine
from core.kernel.events import EventLogger
from core.kernel.goals import GoalManager
from core.kernel.missions import Mission, MissionQueue
from core.kernel.state import StateManager
from core.kernel.worker import BackgroundWorker, MissionHandler


class TitanKernel:
    """Central, recoverable runtime for autonomous mission execution.

    The kernel composes separate goal, queue, decision, state, and worker
    services. Its mission handler is injected so the runtime remains agnostic
    to domain-specific execution logic.
    """

    def __init__(
        self,
        *,
        state_manager: StateManager,
        mission_handler: MissionHandler,
        config: KernelConfig | None = None,
    ) -> None:
        """Create the kernel and recover any state persisted by an earlier instance."""
        self.config = config or KernelConfig()
        self.state_manager = state_manager
        self.event_logger = EventLogger()
        self._decision_results: list[Any] = []
        self._skill_results: list[Any] = []
        self.goal_manager = GoalManager()
        self.mission_queue = MissionQueue(self.event_logger)
        self.decision_engine = DecisionEngine()
        self._recover()
        self.worker = BackgroundWorker(
            self.mission_queue,
            self.decision_engine,
            self.config,
            mission_handler,
            self.persist,
        )

    def create_mission(self, goal_id: str, title: str, **kwargs: Any) -> Mission:
        """Create and enqueue a mission tied to an existing goal."""
        if self.goal_manager.get(goal_id) is None:
            raise KeyError(f"Unknown goal '{goal_id}'.")
        mission = Mission(goal_id=goal_id, title=title, **kwargs)
        self.mission_queue.enqueue(mission)
        self.persist()
        return mission

    def persist(self) -> None:
        """Persist the complete recoverable kernel state."""
        self.state_manager.save(
            {
                "goals": self.goal_manager.snapshot(),
                "missions": self.mission_queue.snapshot(),
                "events": self.event_logger.snapshot(),
                "decision_results": [self._snapshot_decision_result(item) for item in self._decision_results],
                "skill_results": [self._snapshot_skill_result(item) for item in self._skill_results],
            }
        )

    def record_skill_result(self, result: Any) -> None:
        """Record a skill runtime result and persist it with kernel state."""
        self._skill_results.append(result)
        self.persist()

    def record_decision_result(self, result: Any) -> None:
        """Record a decision-engine result and persist it with kernel state."""
        self._decision_results.append(result)
        self.persist()

    def decision_results(self) -> tuple[Any, ...]:
        """Return results reported by an attached decision engine."""
        return tuple(self._decision_results)

    def skill_results(self) -> tuple[Any, ...]:
        """Return results reported by an attached skill runtime."""
        return tuple(self._skill_results)

    @staticmethod
    def _snapshot_skill_result(result: Any) -> Any:
        """Convert standard skill results to JSON-compatible persisted state."""
        if all(hasattr(result, attribute) for attribute in ("execution_id", "skill_name", "status")):
            completed_at = getattr(result, "completed_at", None)
            status = getattr(result, "status")
            return {
                "execution_id": result.execution_id,
                "skill_name": result.skill_name,
                "status": getattr(status, "value", str(status)),
                "output": getattr(result, "output", None),
                "error": getattr(result, "error", None),
                "completed_at": completed_at.isoformat() if completed_at else None,
            }
        return result

    @staticmethod
    def _snapshot_decision_result(result: Any) -> Any:
        """Convert standard decision results to JSON-compatible persisted state."""
        if all(hasattr(result, attribute) for attribute in ("context_id", "scores", "evaluations")):
            return {
                "context_id": result.context_id,
                "selected_action": str(result.selected_action),
                "scores": list(result.scores),
                "evaluations": list(result.evaluations),
                "created_at": result.created_at.isoformat(),
            }
        return result

    def _recover(self) -> None:
        """Restore persisted goals and missions, making interrupted work retryable."""
        state = self.state_manager.load()
        self._decision_results = list(state.get("decision_results", []))
        self._skill_results = list(state.get("skill_results", []))
        self.event_logger.restore(state.get("events", []))
        self.goal_manager.restore(state.get("goals", []))
        self.mission_queue.restore(state.get("missions", []))
