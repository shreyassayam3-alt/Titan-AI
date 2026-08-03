"""Agent lifecycle and assignment ownership management."""

from core.coordination.models import Agent, AgentStatus
from core.models import Task


class AgentManager:
    """Registers specialized agents and tracks their task ownership."""

    def __init__(self) -> None:
        """Create an empty agent collection."""
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """Register an agent under its unique identifier."""
        if agent.id in self._agents:
            raise ValueError(f"Agent '{agent.id}' already exists.")
        self._agents[agent.id] = agent

    def create(
        self, name: str, *, capabilities: frozenset[str] = frozenset()
    ) -> Agent:
        """Create, register, and return an available specialized agent."""
        agent = Agent(name=name, capabilities=capabilities)
        self.register(agent)
        return agent

    def get(self, agent_id: str) -> Agent | None:
        """Return an agent by identifier when registered."""
        return self._agents.get(agent_id)

    def available(self) -> tuple[Agent, ...]:
        """Return agents eligible to receive new assignments."""
        return tuple(agent for agent in self._agents.values() if agent.status is AgentStatus.AVAILABLE)

    def assign(self, task: Task, agent_id: str) -> Agent:
        """Assign ``task`` to an available agent and update its workload."""
        agent = self._require(agent_id)
        if agent.status is AgentStatus.OFFLINE:
            raise RuntimeError(f"Agent '{agent_id}' is offline.")
        agent.assigned_task_ids.add(task.id)
        agent.status = AgentStatus.BUSY
        return agent

    def release(self, task_id: str, agent_id: str) -> Agent:
        """Release a task and mark an agent available when its workload is empty."""
        agent = self._require(agent_id)
        agent.assigned_task_ids.discard(task_id)
        if not agent.assigned_task_ids and agent.status is not AgentStatus.OFFLINE:
            agent.status = AgentStatus.AVAILABLE
        return agent

    def _require(self, agent_id: str) -> Agent:
        """Return a registered agent or raise a clear lookup error."""
        agent = self.get(agent_id)
        if agent is None:
            raise KeyError(f"Unknown agent '{agent_id}'.")
        return agent
