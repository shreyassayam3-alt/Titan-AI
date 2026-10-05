"""Environment-backed runtime configuration for the Titan platform."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Config:
    """Configuration values used by Titan runtime processes and agents."""

    environment: str = os.getenv("TITAN_ENV", "development")
    debug: bool = os.getenv("TITAN_ENV", "development") == "development"
    log_level: str = os.getenv("TITAN_LOG_LEVEL", "INFO")
    state_dir: str = os.getenv("TITAN_STATE_DIR", "./.titan")
    max_retries: int = int(os.getenv("TITAN_MAX_RETRIES", "3"))
    execution_interval_seconds: int = int(os.getenv("TITAN_EXECUTION_INTERVAL_SECONDS", "1"))

    @classmethod
    def from_env(cls) -> "Config":
        """Create a configuration object from environment variables."""
        return cls(
            environment=os.getenv("TITAN_ENV", "development"),
            debug=os.getenv("TITAN_ENV", "development") == "development",
            log_level=os.getenv("TITAN_LOG_LEVEL", "INFO"),
            state_dir=os.getenv("TITAN_STATE_DIR", "./.titan"),
            max_retries=int(os.getenv("TITAN_MAX_RETRIES", "3")),
            execution_interval_seconds=int(os.getenv("TITAN_EXECUTION_INTERVAL_SECONDS", "1")),
        )
