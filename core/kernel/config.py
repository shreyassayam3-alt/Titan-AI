"""Configuration objects for the Titan Kernel runtime."""

from dataclasses import dataclass
from enum import StrEnum


class ApprovalPolicy(StrEnum):
    """Determines whether a mission must receive explicit approval to run."""

    AUTO_APPROVE = "auto_approve"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True, slots=True)
class KernelConfig:
    """Runtime settings kept separate from scheduling and execution behavior."""

    execution_interval_seconds: float = 1.0
    approval_policy: ApprovalPolicy = ApprovalPolicy.AUTO_APPROVE

    def __post_init__(self) -> None:
        """Reject invalid polling intervals before a worker is started."""
        if self.execution_interval_seconds <= 0:
            raise ValueError("execution_interval_seconds must be greater than zero.")
