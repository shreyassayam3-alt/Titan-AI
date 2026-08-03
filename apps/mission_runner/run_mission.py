"""CLI entrypoint for running missions through the Titan runtime."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.mission_runner.mission_runner import MissionRunner
from core.decision import DecisionEngine, WeightedDecisionPolicy
from core.decision.evaluators import ApprovalEvaluator, CostEvaluator, RiskEvaluator, StrategySelector
from core.events import InMemoryEventBus
from core.executor import PlaceholderExecutor
from core.kernel import StateManager, TitanKernel
from core.learning import InMemoryLearning
from core.memory import InMemoryMemory
from core.orchestrator import WorkflowOrchestrator
from core.planner import SimplePlanner
from core.reasoner import SimpleReasoner
from core.skills import PermissionManager, Skill, SkillRegistry, SkillRuntime


class _NoopStrategy(StrategySelector):
    name = "strategy"

    async def evaluate(self, action: Any, context: Any) -> float:
        return 1.0


class _NoopRisk(RiskEvaluator):
    name = "risk"

    async def evaluate(self, action: Any, context: Any) -> float:
        return 0.0


class _NoopCost(CostEvaluator):
    name = "cost"

    async def evaluate(self, action: Any, context: Any) -> float:
        return 0.0


class _NoopApproval(ApprovalEvaluator):
    name = "approval"

    async def evaluate(self, action: Any, context: Any) -> bool:
        return True


class _EchoMissionSkill(Skill):
    name = "echo_mission"

    async def validate(self, input_data: dict[str, Any]) -> None:
        if "goal" not in input_data:
            raise ValueError("goal is required")

    async def execute(self, input_data: dict[str, Any]) -> Any:
        return input_data["goal"]

    async def rollback(self, input_data: dict[str, Any], error: Exception) -> None:
        return None


def build_runner(state_path: Path | None = None) -> MissionRunner:
    """Create a runnable mission runner using the local in-memory stack."""
    kernel = TitanKernel(
        state_manager=StateManager(state_path or Path("state.json")),
        mission_handler=lambda _: None,
    )
    planner = SimplePlanner()
    orchestrator = WorkflowOrchestrator(
        planner=planner,
        reasoner=SimpleReasoner(),
        executor=PlaceholderExecutor(),
        learning=InMemoryLearning(),
        memory=InMemoryMemory(),
        event_bus=InMemoryEventBus(),
    )
    decision_engine = DecisionEngine(
        policy=WeightedDecisionPolicy({"strategy": 1.0, "risk": 0.0, "cost": 0.0}),
        strategy_selector=_NoopStrategy(),
        risk_evaluator=_NoopRisk(),
        cost_evaluator=_NoopCost(),
        approval_evaluator=_NoopApproval(),
    )
    registry = SkillRegistry()
    registry.register(_EchoMissionSkill())
    skill_runtime = SkillRuntime(registry, PermissionManager())
    memory = InMemoryMemory()
    return MissionRunner(
        kernel=kernel,
        planner=planner,
        orchestrator=orchestrator,
        decision_engine=decision_engine,
        skill_runtime=skill_runtime,
        memory=memory,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Titan mission")
    parser.add_argument("goal", help="Mission goal to execute")
    parser.add_argument("--description", default=None, help="Optional goal description")
    parser.add_argument("--priority", default=0, type=int, help="Optional goal priority")
    parser.add_argument("--state-file", default="state.json", help="Path to the kernel state file")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse the CLI arguments and run the mission."""
    parser = build_parser()
    args = parser.parse_args(argv)

    async def _run() -> None:
        runner = build_runner(Path(args.state_file))
        execution = await runner.run(args.goal, description=args.description, priority=args.priority)
        print(runner.format_log(execution))

    asyncio.run(_run())
    return 0


if __name__ == "__main__":
    main()
