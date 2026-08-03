"""Deterministic resolution of competing plan proposals."""

from collections.abc import Sequence

from core.coordination.models import PlanProposal


class ConflictResolver:
    """Selects the highest-confidence proposal with deterministic tie-breaking."""

    def resolve(self, proposals: Sequence[PlanProposal]) -> PlanProposal | None:
        """Return the preferred proposal or ``None`` when no proposal exists."""
        return (
            max(proposals, key=lambda item: (item.confidence, item.agent_id))
            if proposals
            else None
        )
