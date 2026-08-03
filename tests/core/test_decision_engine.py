"""Unit tests for policy-driven, extensible decision selection."""

import asyncio
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.decision import (
    ApprovalEvaluator,
    CostEvaluator,
    DecisionContext,
    DecisionEngine,
    EvaluatorRegistry,
    RiskEvaluator,
    StrategySelector,
    WeightedDecisionPolicy,
)
from core.decision.registry import DecisionEvaluator
from core.events import InMemoryEventBus
from core.kernel import StateManager, TitanKernel
from core.memory import InMemoryMemory


class MappingStrategy(StrategySelector):
    """Test strategy evaluator backed by configured action scores."""

    name = "strategy"

    def __init__(self, values: Mapping[str, float]) -> None:
        """Store strategy values by action name."""
        self._values = values

    async def evaluate(self, action: Any, context: DecisionContext) -> float:
        """Return the configured value for the action."""
        return self._values[action]


class MappingRisk(RiskEvaluator):
    """Test risk evaluator backed by configured action scores."""

    name = "risk"

    async def evaluate(self, action: Any, context: DecisionContext) -> float:
        """Return zero risk for concise test setup."""
        return 0.0


class MappingCost(CostEvaluator):
    """Test cost evaluator backed by configured action scores."""

    name = "cost"

    async def evaluate(self, action: Any, context: DecisionContext) -> float:
        """Return zero cost for concise test setup."""
        return 0.0


class TestApproval(ApprovalEvaluator):
    """Test approval evaluator that can reject selected actions."""

    name = "approval"

    def __init__(self, denied: frozenset[str] = frozenset()) -> None:
        """Configure actions that should be ineligible."""
        self._denied = denied

    async def evaluate(self, action: Any, context: DecisionContext) -> bool:
        """Approve every action not explicitly denied."""
        return action not in self._denied


class BonusEvaluator(DecisionEvaluator):
    """Plugin evaluator used to demonstrate engine extensibility."""

    name = "bonus"

    async def evaluate(self, action: Any, context: DecisionContext) -> float:
        """Favor the action named ``second`` through plugin-provided scoring."""
        return 10.0 if action == "second" else 0.0


def _engine(
    *,
    approval: ApprovalEvaluator | None = None,
    registry: EvaluatorRegistry | None = None,
    memory: InMemoryMemory | None = None,
    event_bus: InMemoryEventBus | None = None,
    reporter: Any = None,
) -> DecisionEngine:
    """Build a deterministic engine for decision tests."""
    return DecisionEngine(
        policy=WeightedDecisionPolicy({"strategy": 1.0, "risk": -1.0, "cost": -1.0, "bonus": 1.0}),
        strategy_selector=MappingStrategy({"first": 5.0, "second": 1.0}),
        risk_evaluator=MappingRisk(),
        cost_evaluator=MappingCost(),
        approval_evaluator=approval or TestApproval(),
        evaluator_registry=registry,
        memory=memory,
        event_bus=event_bus,
        result_reporter=reporter,
    )


def test_engine_selects_best_approved_action_and_integrates_infrastructure(tmp_path: Path) -> None:
    """Select an action, publish it, store it, and report it to the kernel."""
    async def mission_handler(_: object) -> None:
        """Provide the required kernel handler without domain execution."""

    async def run() -> None:
        memory = InMemoryMemory()
        bus = InMemoryEventBus()
        events: list[object] = []

        async def capture(event: object) -> None:
            events.append(event)

        bus.subscribe("decision.completed", capture)
        kernel = TitanKernel(
            state_manager=StateManager(tmp_path / "state.json"), mission_handler=mission_handler
        )
        context = DecisionContext(actions=("first", "second"))
        result = await _engine(memory=memory, event_bus=bus, reporter=kernel.record_decision_result).decide(context)
        assert result.selected_action == "first"
        assert await memory.retrieve(f"decisions:{context.correlation_id}") == result
        assert events == [result]
        assert kernel.decision_results() == (result,)

    asyncio.run(run())


def test_plugin_evaluator_can_change_selection_without_engine_changes() -> None:
    """Register a new evaluator and make its policy weight affect the outcome."""
    async def run() -> None:
        registry = EvaluatorRegistry()
        registry.register(BonusEvaluator())
        assert (await _engine(registry=registry).decide(DecisionContext(actions=("first", "second")))).selected_action == "second"

    asyncio.run(run())


def test_approval_evaluator_excludes_denied_actions() -> None:
    """Leave a denied high-score action out of the engine result."""
    async def run() -> None:
        result = await _engine(approval=TestApproval(frozenset({"first"}))).decide(
            DecisionContext(actions=("first", "second"))
        )
        assert result.selected_action == "second"
        assert result.scores[0] is None

    asyncio.run(run())
