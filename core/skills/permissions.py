"""Approval-aware permission enforcement for skill execution."""

from core.kernel import ApprovalPolicy
from core.skills.base import Skill


class PermissionManager:
    """Enforces configured approval policy before sensitive skill actions run."""

    def __init__(self, policy: ApprovalPolicy = ApprovalPolicy.AUTO_APPROVE) -> None:
        """Create a manager with no explicit approvals."""
        self._policy = policy
        self._approvals: set[tuple[str, str]] = set()

    def approve(self, skill_name: str, permission: str = "execute") -> None:
        """Approve one permission for a named skill."""
        self._approvals.add((skill_name, permission))

    def revoke(self, skill_name: str, permission: str = "execute") -> None:
        """Withdraw an explicit approval when it exists."""
        self._approvals.discard((skill_name, permission))

    def require(self, skill: Skill) -> None:
        """Raise ``PermissionError`` when ``skill`` lacks required approval."""
        if self._policy is ApprovalPolicy.AUTO_APPROVE:
            return
        permissions = skill.required_permissions or ({"execute"} if skill.sensitive else set())
        denied = [permission for permission in permissions if (skill.name, permission) not in self._approvals]
        if denied:
            raise PermissionError(f"Skill '{skill.name}' requires approval for: {', '.join(denied)}.")
