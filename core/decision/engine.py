"""Policy-driven decision engine and infrastructure integrations."""

import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from core.decision.evaluators import (
    ApprovalEvaluator,
    CostEvaluator,
    RiskEvaluator,
    StrategySelector,
)
from core.decision.models import DecisionContext, DecisionResult
from core.decision.policies import DecisionPolicy
from core.decision.registry import EvaluatorRegistry
from core.events import EventBus
from core.kernel.missions import MissionQueue
from core.memory import Memory

type DecisionReporter = Callable[[DecisionResult], Awaitable[None] | None]


class DecisionEngine:
    """Selects the best approved action through configured evaluator policies.

    The engine does not know an action's domain. Evaluators and policy plugins
    provide every domain-specific judgement, keeping selection extensible.
    """

    def __init__(
        self,
        *,
        policy: DecisionPolicy,
        strategy_selector: StrategySelector,
        risk_evaluator: RiskEvaluator,
        cost_evaluator: CostEvaluator,
        approval_evaluator: ApprovalEvaluator,
        evaluator_registry: EvaluatorRegistry | None = None,
        event_bus: EventBus | None = None,
        memory: Memory | None = None,
        result_reporter: DecisionReporter | None = None,
    ) -> None:
        """Initialize the engine with policy, evaluators, and optional integrations."""
        self._policy = policy
        self._strategy_selector = strategy_selector
        self._risk_evaluator = risk_evaluator
        self._cost_evaluator = cost_evaluator
        self._approval_evaluator = approval_evaluator
        self._evaluator_registry = evaluator_registry or EvaluatorRegistry()
        self._event_bus = event_bus
        self._memory = memory
        self._result_reporter = result_reporter

    async def decide(self, context: DecisionContext) -> DecisionResult:
        """Evaluate each action and return the highest-scoring approved action."""
        evaluations = tuple([await self._evaluate(action, context) for action in context.actions])
        scores = tuple(
            self._policy.score(evaluation) if evaluation["approval"] else None
            for evaluation in evaluations
        )
        selected_index = self._selected_index(scores)
        result = DecisionResult(
            context_id=context.correlation_id,
            selected_action=context.actions[selected_index] if selected_index is not None else None,
            scores=scores,
            evaluations=evaluations,
        )
        await self._publish_and_store(result)
        return result

    async def decide_mission_queue(
        self, queue: MissionQueue, *, require_approval: bool = False
    ) -> DecisionResult:
        """Evaluate the queue's executable missions through the same action engine."""
        missions = queue.executable(require_approval=require_approval)
        return await self.decide(
            DecisionContext(actions=missions, metadata={"source": "mission_queue"})
        )

    async def _evaluate(self, action: Any, context: DecisionContext) -> dict[str, float | bool]:
        """Gather built-in and registered plugin evaluations for one action."""
        evaluations: dict[str, float | bool] = {
            self._strategy_selector.name: await self._strategy_selector.evaluate(action, context),
            self._risk_evaluator.name: await self._risk_evaluator.evaluate(action, context),
            self._cost_evaluator.name: await self._cost_evaluator.evaluate(action, context),
            "approval": await self._approval_evaluator.evaluate(action, context),
        }
        for evaluator in self._evaluator_registry.evaluators():
            evaluations[evaluator.name] = await evaluator.evaluate(action, context)
        return evaluations

    async def _publish_and_store(self, result: DecisionResult) -> None:
        """Deliver a completed result to configured runtime integrations."""
        if self._memory is not None:
            await self._memory.store(f"decisions:{result.context_id}", result)
        if self._event_bus is not None:
            await self._event_bus.publish("decision.completed", result)
        if self._result_reporter is not None:
            reporting_result = self._result_reporter(result)
            if inspect.isawaitable(reporting_result):
                await reporting_result

    @staticmethod
    def _selected_index(scores: tuple[float | None, ...]) -> int | None:
        """Return the first index whose eligible score is maximal."""
        eligible = [(index, score) for index, score in enumerate(scores) if score is not None]
        return max(eligible, key=lambda item: item[1])[0] if eligible else None
