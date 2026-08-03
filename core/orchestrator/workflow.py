"""Concrete orchestration workflow for local, in-memory execution."""

from collections.abc import Sequence
from typing import Any

from core.events import EventBus, InMemoryEventBus
from core.executor import Executor, PlaceholderExecutor
from core.learning import InMemoryLearning, Learning
from core.memory import InMemoryMemory, Memory
from core.models import ExecutionReport, Goal, GoalStatus, Task, TaskStatus
from core.orchestrator.base import Orchestrator
from core.planner import Planner, SimplePlanner
from core.reasoner import Reasoner, SimpleReasoner


class WorkflowOrchestrator(Orchestrator):
    """Coordinates planning, reasoning, execution, learning, and memory.

    Dependencies are injected to keep this workflow independently testable and
    allow later replacements with durable or externally backed implementations.
    """

    def __init__(
        self,
        *,
        planner: Planner,
        reasoner: Reasoner,
        executor: Executor,
        learning: Learning,
        memory: Memory,
        event_bus: EventBus,
    ) -> None:
        """Initialize the workflow with its collaborating components."""
        self._planner = planner
        self._reasoner = reasoner
        self._executor = executor
        self._learning = learning
        self._memory = memory
        self._event_bus = event_bus

    @classmethod
    def create_default(cls) -> "WorkflowOrchestrator":
        """Create an executable workflow using only local in-memory components."""
        return cls(
            planner=SimplePlanner(),
            reasoner=SimpleReasoner(),
            executor=PlaceholderExecutor(),
            learning=InMemoryLearning(),
            memory=InMemoryMemory(),
            event_bus=InMemoryEventBus(),
        )

    async def execute(self, request: Any, *, context: Any | None = None) -> ExecutionReport:
        """Run the minimal goal-to-report workflow for a ``Goal`` request."""
        if not isinstance(request, Goal):
            raise TypeError("WorkflowOrchestrator requires a Goal request.")

        goal = request
        goal.status = GoalStatus.IN_PROGRESS
        goal.touch()
        await self._event_bus.publish("goal.received", goal)

        try:
            tasks = self._as_tasks(await self._planner.decompose_goal(goal, context=context))
            await self._event_bus.publish("goal.decomposed", {"goal": goal, "tasks": tasks})

            evaluations = await self._reasoner.evaluate_options(tasks, context=context)
            strategy = await self._reasoner.select_strategy(evaluations, context=context)
            results = await self._execute_tasks(tasks, strategy=strategy, context=context)

            goal.status = GoalStatus.COMPLETED
            goal.touch()
            report = ExecutionReport(goal=goal, tasks=tasks, results=results, strategy=strategy)
            await self._memory.store(f"goals:{goal.id}:report", report)
            await self._event_bus.publish("goal.completed", report)
            return report
        except Exception:
            goal.status = GoalStatus.FAILED
            goal.touch()
            await self._event_bus.publish("goal.failed", goal)
            raise

    async def _execute_tasks(
        self, tasks: tuple[Task, ...], *, strategy: Any | None, context: Any | None
    ) -> tuple[Any, ...]:
        """Execute tasks sequentially, retaining each result and lifecycle event."""
        results: list[Any] = []
        for task in tasks:
            task.status = TaskStatus.IN_PROGRESS
            await self._event_bus.publish("task.started", task)
            try:
                result = await self._executor.execute(
                    task,
                    context={"strategy": strategy, "context": context},
                )
            except Exception:
                task.status = TaskStatus.FAILED
                await self._event_bus.publish("task.failed", task)
                raise

            task.status = TaskStatus.COMPLETED
            await self._memory.store(f"goals:{task.parent_goal}:tasks:{task.id}", result)
            await self._learning.record_completed_task(task, result)
            await self._event_bus.publish("task.completed", {"task": task, "result": result})
            results.append(result)
        return tuple(results)

    @staticmethod
    def _as_tasks(tasks: Sequence[Any]) -> tuple[Task, ...]:
        """Validate that a planner returned task domain objects."""
        if not all(isinstance(task, Task) for task in tasks):
            raise TypeError("Planner must return only Task instances.")
        return tuple(tasks)
