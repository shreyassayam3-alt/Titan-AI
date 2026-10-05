"""Reusable mission execution workflow for Titan applications."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from core.memory import InMemoryMemory, Memory
from core.models import ExecutionReport, Goal, Task


@dataclass(slots=True)
class MissionExecutionResult:
    """Result of a mission run, including the report and intermediate artifacts."""

    goal: Goal
    plan: tuple[Task, ...]
    decision: Any | None
    skill_results: tuple[Any, ...]
    report: ExecutionReport
    history: list[dict[str, Any]]
    log_lines: tuple[str, ...]


class MissionRunner:
    """Compose a goal, planner, decision engine, skill runtime, memory, and orchestrator."""

    def __init__(
        self,
        *,
        kernel: Any | None = None,
        planner: Any | None = None,
        orchestrator: Any | None = None,
        decision_engine: Any | None = None,
        skill_runtime: Any | None = None,
        memory: Memory | None = None,
        logger: Callable[[str], None] | None = None,
    ) -> None:
        self._kernel = kernel
        self._planner = planner
        self._orchestrator = orchestrator
        self._decision_engine = decision_engine
        self._skill_runtime = skill_runtime
        self._memory = memory or InMemoryMemory()
        self._logger = logger or print
        self._log_lines: list[str] = []

    async def run(self, goal_text: str, *, description: str | None = None, priority: int = 0, context: Any | None = None) -> MissionExecutionResult:
        """Execute a single mission end to end and return a structured summary."""
        if not goal_text.strip():
            raise ValueError("goal_text must not be empty")

        goal = self._create_goal(goal_text, description=description, priority=priority)
        self._log("Goal", goal.title)

        plan = tuple(await self._create_plan(goal, context=context))
        self._log("Planning", ", ".join(task.title for task in plan))

        decision_context = self._build_decision_context(goal, plan, context)
        decision = await self._make_decision(decision_context)
        self._log("Reasoning", getattr(decision, "selected_action", None))

        skill_results: list[Any] = []
        for task in plan:
            result = await self._run_skill(goal, task, context=context)
            skill_results.append(result)
        self._log("Skills", ", ".join(str(getattr(result, "skill_name", result)) for result in skill_results))

        history = [
            {"stage": "Goal", "value": goal.title},
            {"stage": "Planning", "value": [task.title for task in plan]},
            {"stage": "Reasoning", "value": getattr(decision, "selected_action", None)},
            {"stage": "Skills", "value": [getattr(result, "output", None) for result in skill_results]},
            {"stage": "Memory", "value": "stored"},
            {"stage": "Decision", "value": getattr(decision, "selected_action", None)},
            {"stage": "Final Result", "value": goal.title},
        ]
        await self._memory.store("mission:history", history)
        self._log("Memory", "mission:history")

        report = await self._run_orchestrator(goal, plan, skill_results, decision, context=context)
        self._log("Decision", getattr(decision, "selected_action", None))
        self._log("Final Result", getattr(report, "goal", goal).title)

        history[-1] = {"stage": "Final Result", "value": getattr(report, "goal", goal).title}
        history[-2] = {"stage": "Decision", "value": getattr(decision, "selected_action", None)}

        return MissionExecutionResult(
            goal=goal,
            plan=plan,
            decision=decision,
            skill_results=tuple(skill_results),
            report=report,
            history=history,
            log_lines=tuple(self._log_lines),
        )

    def _create_goal(self, title: str, *, description: str | None, priority: int) -> Goal:
        if self._kernel is not None and hasattr(self._kernel, "goal_manager"):
            goal_manager = self._kernel.goal_manager
            return goal_manager.create(title, description or title, priority=priority)
        return Goal(title=title, description=description or title, priority=priority)

    async def _create_plan(self, goal: Goal, *, context: Any | None) -> tuple[Task, ...]:
        if self._planner is None:
            return (Task(parent_goal=goal.id, title=goal.title),)
        if hasattr(self._planner, "create_plan"):
            tasks = await self._planner.create_plan(goal, context=context)
        else:
            tasks = await self._planner.decompose_goal(goal, context=context)
        return tuple(tasks)

    def _build_decision_context(self, goal: Goal, plan: tuple[Task, ...], context: Any | None) -> Any:
        from core.decision.models import DecisionContext

        return DecisionContext(actions=plan, metadata={"goal": goal, "context": context})

    async def _make_decision(self, decision_context: Any) -> Any:
        if self._decision_engine is None:
            return type("DecisionResult", (), {"selected_action": "default"})()
        return await self._decision_engine.decide(decision_context)

    async def _run_skill(self, goal: Goal, task: Task, *, context: Any | None) -> Any:
        if self._skill_runtime is None:
            return type("SkillResult", (), {"skill_name": "mission-skill", "output": goal.title})()
        return await self._skill_runtime.execute(
            "research",
            {"goal": goal.title, "task": task.title, "context": context, "memory": self._memory},
        )

    @staticmethod
    def _normalize_skill_result(result: Any) -> Any:
        if hasattr(result, "output") and result.output is not None:
            return result.output
        return result

    async def _run_orchestrator(
        self,
        goal: Goal,
        plan: tuple[Task, ...],
        skill_results: list[Any],
        decision: Any,
        *,
        context: Any | None,
    ) -> ExecutionReport:
        normalized_results = tuple(self._normalize_skill_result(result) for result in skill_results)

        if self._orchestrator is None:
            return ExecutionReport(goal=goal, tasks=plan, results=normalized_results, strategy=decision)

        report = await self._orchestrator.execute(
            goal,
            context={
                "plan": plan,
                "decision": decision,
                "skill_result": normalized_results[-1] if normalized_results else None,
                "context": context,
            },
        )
        if isinstance(report, ExecutionReport):
            return ExecutionReport(
                goal=report.goal,
                tasks=report.tasks or plan,
                results=normalized_results,
                strategy=report.strategy,
            )
        return ExecutionReport(goal=goal, tasks=plan, results=normalized_results, strategy=decision)

    def _log(self, stage: str, value: Any) -> None:
        message = f"{stage}: {value}" if value is not None else stage
        self._log_lines.append(message)
        self._logger(message)

    def format_log(self, execution: MissionExecutionResult) -> str:
        """Render a human-readable mission progress log."""
        lines = ["Mission Log", "==========="]
        for entry in execution.history:
            stage = entry["stage"]
            value = entry["value"]
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            lines.append(f"{stage}: {value}")
        return "\n".join(lines)
