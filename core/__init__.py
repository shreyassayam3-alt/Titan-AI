"""Foundational interfaces for the Titan AI core runtime.

This package intentionally defines contracts only. Concrete implementations
belong in higher-level packages and can be composed through these interfaces.
"""

from core.brain import Brain, SimpleBrain
from core.decision import DecisionContext, DecisionEngine, DecisionResult
from core.events import EventBus, InMemoryEventBus
from core.executor import Executor, PlaceholderExecutor
from core.learning import InMemoryLearning, Learning
from core.memory import InMemoryMemory, Memory
from core.kernel import TitanKernel
from core.models import ExecutionReport, Goal, GoalStatus, Task, TaskStatus
from core.orchestrator import Orchestrator, WorkflowOrchestrator
from core.planner import Planner, SimplePlanner
from core.reasoner import Reasoner, SimpleReasoner
from core.registry import Registry
from core.scheduler import Scheduler
from core.skills import Skill, SkillRegistry, SkillRuntime
from core.tools import ToolRegistry

__all__ = [
    "Brain",
    "DecisionContext",
    "DecisionEngine",
    "DecisionResult",
    "EventBus",
    "ExecutionReport",
    "Executor",
    "Goal",
    "GoalStatus",
    "InMemoryEventBus",
    "InMemoryLearning",
    "InMemoryMemory",
    "Learning",
    "Memory",
    "Orchestrator",
    "Planner",
    "PlaceholderExecutor",
    "Reasoner",
    "Registry",
    "Scheduler",
    "Skill",
    "SkillRegistry",
    "SkillRuntime",
    "SimpleBrain",
    "SimplePlanner",
    "SimpleReasoner",
    "Task",
    "TaskStatus",
    "TitanKernel",
    "ToolRegistry",
    "WorkflowOrchestrator",
]
