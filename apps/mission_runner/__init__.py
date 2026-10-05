"""Mission runner package for composing Titan runtime components."""

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps.mission_runner.mission_runner import MissionExecutionResult, MissionRunner

__all__ = ["MissionExecutionResult", "MissionRunner", "build_parser", "build_runner", "main"]


def __getattr__(name: str) -> Any:
    """Lazily expose the CLI helpers without importing the module during package import."""
    if name in {"build_parser", "build_runner", "main"}:
        from apps.mission_runner import run_mission

        return getattr(run_mission, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
