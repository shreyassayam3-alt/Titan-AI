"""Advanced agent runtime for TITAN: planners, workers, specialist agents, and orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentConfig:
    """Configuration for a TITAN agent worker."""

    name: str
    role: str
    model: str = "local/simple"
    max_concurrency: int = 1
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentTask:
    """A task assigned to a specialist agent."""

    task_id: str
    title: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    assigned_agent: str | None = None


class SpecialistAgent:
    """A specialized agent that performs domain-specific work."""

    def __init__(self, config: AgentConfig) -> None:
        """Initialize the specialist agent."""
        self.config = config

    async def execute(self, task: AgentTask, *, context: Any | None = None) -> dict[str, Any]:
        """Execute the task with a simple local strategy."""
        return {
            "agent": self.config.name,
            "role": self.config.role,
            "task_id": task.task_id,
            "title": task.title,
            "status": "completed",
            "output": f"{self.config.name} completed task: {task.title}",
            "context": context,
        }


class AgentRuntime:
    """Runtime for specialized TITAN agents."""

    def __init__(self) -> None:
        """Create an empty runtime."""
        self._agents: dict[str, SpecialistAgent] = {}

    def register_agent(self, agent: SpecialistAgent) -> None:
        """Register an agent by name."""
        self._agents[agent.config.name] = agent

    async def execute_task(self, task: AgentTask, *, context: Any | None = None) -> dict[str, Any]:
        """Execute a task using the assigned or default agent."""
        agent_name = task.assigned_agent or self._next_agent_name()
        agent = self._agents.get(agent_name)
        if agent is None:
            raise KeyError(f"No agent registered with name '{agent_name}'")
        return await agent.execute(task, context=context)

    def _next_agent_name(self) -> str:
        """Return the first available agent"""
        if not self._agents:
            raise KeyError("No agents available in runtime")
        return next(iter(self._agents.keys()))

    def list_agents(self) -> list[str]:
        """Return the registered agent names."""
        return sorted(self._agents)
