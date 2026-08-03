"""Research source model."""

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class Source:
    """Identifies an information source returned by a registered provider."""

    name: str
    url: str | None = None
    provider_name: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
