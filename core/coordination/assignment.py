"""Capability-aware task routing for registered agents."""

from core.coordination.agents import AgentManager
from core.coordination.models import Agent
from core.models import Task


class TaskAssignmentEngine:
    """Routes tasks to the least-loaded available capable agent."""

    def __init__(self, agent_manager: AgentManager) -> None:
        """Initialize routing against the shared agent manager."""
        self._agent_manager = agent_manager

    def assign(self, task: Task, *, required_capabilities: frozenset[str] = frozenset()) -> Agent:
        """Select and assign the best eligible agent for ``task``."""
        candidates = [
            agent
            for agent in self._agent_manager.available()
            if required_capabilities.issubset(agent.capabilities)
        ]
        if not candidates:
            raise LookupError("No available agent satisfies the task capabilities.")
        selected = min(candidates, key=lambda agent: (len(agent.assigned_task_ids), agent.id))
        return self._agent_manager.assign(task, selected.id)
