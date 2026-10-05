"""Enhanced orchestrator with adaptive learning and mission intelligence."""

from __future__ import annotations

from typing import Any

from core.events import EventBus, InMemoryEventBus
from core.executor import Executor
from core.intelligence import MissionIntelligence
from core.learning import InMemoryLearning, Learning
from core.memory import InMemoryMemory, Memory
from core.models import ExecutionReport, Goal, GoalStatus, Task, TaskStatus
from core.orchestrator.base import Orchestrator
from core.persistence import PersistentLearning, StateManager
from core.planner import Planner
from core.reasoner import Reasoner


class AdaptiveOrchestrator(Orchestrator):
    """Orchestrator that learns, adapts, and improves over time with mission intelligence."""

    def __init__(
        self,
        *,
        planner: Planner,
        reasoner: Reasoner,
        executor: Executor,
        learning: Learning,
        memory: Memory,
        event_bus: EventBus,
        state_manager: StateManager | None = None,
    ) -> None:
        """Initialize the adaptive orchestrator."""
        self._planner = planner
        self._reasoner = reasoner
        self._executor = executor
        self._learning = learning
        self._memory = memory
        self._event_bus = event_bus
        self._state_manager = state_manager
        self._mission_intelligence = MissionIntelligence()
        self._execution_count = 0
        self._success_count = 0

    @classmethod
    def create_default(cls, state_manager: StateManager | None = None) -> "AdaptiveOrchestrator":
        """Create a local adaptive orchestrator with in-memory components."""
        from core.executor.skill_executor import SkillExecutor
        from core.planner.enhanced import EnhancedPlanner
        from core.reasoner.weighted import WeightedReasoner

        return cls(
            planner=EnhancedPlanner(),
            reasoner=WeightedReasoner(),
            executor=SkillExecutor(),
            learning=InMemoryLearning(),
            memory=InMemoryMemory(),
            event_bus=InMemoryEventBus(),
            state_manager=state_manager,
        )

    async def execute(self, request: Any, *, context: Any | None = None) -> ExecutionReport:
        """Execute goal with adaptive learning and intelligence."""
        self._execution_count += 1

        if not isinstance(request, Goal):
            raise TypeError("AdaptiveOrchestrator requires a Goal request.")

        goal = request
        goal.status = GoalStatus.IN_PROGRESS
        goal.touch()
        await self._event_bus.publish("goal.received", goal)
        await self._memory.store(f"goal:{goal.id}", goal)

        try:
            # Get adaptive strategy based on mission intelligence
            adaptive_strategy = self._mission_intelligence.get_adaptive_strategy(goal.title)
            await self._event_bus.publish("strategy.selected", adaptive_strategy)

            # Decompose goal into tasks
            tasks = tuple(await self._planner.decompose_goal(goal, context=context))
            await self._event_bus.publish("goal.decomposed", {"goal": goal, "tasks": tasks})

            # Evaluate task options with context from intelligence
            evaluated_tasks = await self._reasoner.evaluate_options(tasks, context=context)
            strategy = await self._reasoner.select_strategy(evaluated_tasks, context=context)

            # Execute tasks
            results = await self._execute_tasks(goal, tasks, strategy=strategy, context=context)

            # Record success in learning system
            self._success_count += 1
            for task, result in zip(tasks, results):
                await self._learning.record_completed_task(task, result)

            goal.status = GoalStatus.COMPLETED
            goal.touch()
            report = ExecutionReport(goal=goal, tasks=tasks, results=results, strategy=strategy)
            await self._memory.store(f"report:{goal.id}", report)
            await self._event_bus.publish("goal.completed", report)

            # Analyze mission for future learning
            mission_record = {
                "goal_id": goal.id,
                "goal_title": goal.title,
                "tasks": [{"title": t.title, "status": t.status.value} for t in tasks],
                "status": goal.status.value,
            }
            intelligence = await self._mission_intelligence.analyze_mission(mission_record)
            await self._event_bus.publish("intelligence.updated", intelligence)

            return report
        except Exception as error:
            goal.status = GoalStatus.FAILED
            goal.touch()
            await self._event_bus.publish("goal.failed", {"goal": goal, "error": str(error)})
            raise

    async def _execute_tasks(
        self,
        goal: Goal,
        tasks: tuple[Task, ...],
        *,
        strategy: Any | None,
        context: Any | None,
    ) -> tuple[Any, ...]:
        """Execute tasks sequentially with error handling."""
        results: list[Any] = []
        for task in tasks:
            task.status = TaskStatus.IN_PROGRESS
            await self._event_bus.publish("task.started", task)
            try:
                result = await self._executor.execute(
                    task,
                    context={"goal": goal, "strategy": strategy},
                )
                task.status = TaskStatus.COMPLETED
                await self._memory.store(f"task:{task.id}", result)
                await self._event_bus.publish("task.completed", {"task": task, "result": result})
                results.append(result)
            except Exception as error:
                task.status = TaskStatus.FAILED
                await self._learning.record_failed_task(task, error)
                await self._event_bus.publish("task.failed", {"task": task, "error": str(error)})
                raise

        return tuple(results)

    def success_rate(self) -> float:
        """Return the current mission success rate."""
        return self._success_count / self._execution_count if self._execution_count > 0 else 0.0

    def get_intelligence_report(self) -> dict[str, Any]:
        """Get the mission intelligence performance report."""
        return self._mission_intelligence.get_performance_report()
