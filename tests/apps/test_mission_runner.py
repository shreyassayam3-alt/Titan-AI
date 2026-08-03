"""Unit tests for the mission runner orchestration workflow."""

import asyncio
from types import SimpleNamespace

from apps.mission_runner import MissionRunner, build_parser
from core.models import ExecutionReport, Goal, Task


class RecordingGoalManager:
    def __init__(self) -> None:
        self.created_goals: list[Goal] = []

    def create(self, title: str, description: str, *, priority: int = 0) -> Goal:
        goal = Goal(title=title, description=description, priority=priority)
        self.created_goals.append(goal)
        return goal


class RecordingPlanner:
    def __init__(self) -> None:
        self.calls: list[tuple[Goal, object | None]] = []

    async def create_plan(self, goal: Goal, *, context: object | None = None) -> tuple[Task, ...]:
        self.calls.append((goal, context))
        return (Task(parent_goal=goal.id, title=f"Plan for {goal.title}"),)


class RecordingDecisionEngine:
    def __init__(self) -> None:
        self.calls: list[object] = []

    async def decide(self, context: object) -> object:
        self.calls.append(context)
        return SimpleNamespace(selected_action="plan", scores=(1.0,), evaluations=(("plan", 1.0),))


class RecordingSkillRuntime:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    async def execute(self, skill_name: str, input_data: dict[str, object]) -> object:
        self.calls.append((skill_name, input_data))
        return SimpleNamespace(skill_name=skill_name, output={"goal": input_data["goal"]}, status="completed")


class RecordingMemory:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    async def store(self, key: str, value: object) -> None:
        self.values[key] = value

    async def retrieve(self, key: str) -> object | None:
        return self.values.get(key)

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)


class RecordingOrchestrator:
    def __init__(self) -> None:
        self.calls: list[tuple[Goal, object | None]] = []

    async def execute(self, request: Goal, *, context: object | None = None) -> ExecutionReport:
        self.calls.append((request, context))
        return ExecutionReport(
            goal=request,
            tasks=context["plan"],
            results=(context["skill_result"],),
            strategy=context["decision"],
        )


def test_run_mission_executes_and_records_history() -> None:
    async def run() -> None:
        goal_manager = RecordingGoalManager()
        planner = RecordingPlanner()
        decision_engine = RecordingDecisionEngine()
        skill_runtime = RecordingSkillRuntime()
        memory = RecordingMemory()
        orchestrator = RecordingOrchestrator()
        kernel = SimpleNamespace(goal_manager=goal_manager)

        runner = MissionRunner(
            kernel=kernel,
            planner=planner,
            orchestrator=orchestrator,
            decision_engine=decision_engine,
            skill_runtime=skill_runtime,
            memory=memory,
        )

        result = await runner.run("Launch the mission")

        assert result.goal.title == "Launch the mission"
        assert result.report.goal.title == "Launch the mission"
        assert result.plan[0].title == "Plan for Launch the mission"
        assert result.skill_results[0].output["goal"] == "Launch the mission"
        assert planner.calls
        assert decision_engine.calls
        assert skill_runtime.calls
        assert await memory.retrieve("mission:history") is not None
        assert orchestrator.calls[0][0].title == "Launch the mission"

    asyncio.run(run())


def test_build_parser_accepts_goal_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--goal", "Research today's AI news"])
    assert args.goal_flag == "Research today's AI news"
