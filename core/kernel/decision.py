"""Policy-aware mission selection."""

from core.kernel.config import ApprovalPolicy, KernelConfig
from core.kernel.missions import Mission, MissionQueue


class DecisionEngine:
    """Chooses the highest-priority mission whose prerequisites are satisfied."""

    def next_mission(self, queue: MissionQueue, config: KernelConfig) -> Mission | None:
        """Return the next executable mission or ``None`` when no work is ready."""
        missions = queue.executable(
            require_approval=config.approval_policy is ApprovalPolicy.REQUIRE_APPROVAL
        )
        return missions[0] if missions else None
