"""Persistent file-based state manager for TITAN missions."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class StateManager:
    """Persists and recovers mission state to/from the filesystem."""

    def __init__(self, state_dir: str | Path = "./.titan") -> None:
        """Initialize the state manager with a target directory."""
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.missions_dir = self.state_dir / "missions"
        self.missions_dir.mkdir(parents=True, exist_ok=True)
        self.learning_dir = self.state_dir / "learning"
        self.learning_dir.mkdir(parents=True, exist_ok=True)

    def save_mission(self, mission_record: dict[str, Any]) -> str:
        """Save a mission record and return its file path."""
        goal_id = mission_record.get("goal_id", "unknown")
        timestamp = datetime.now().isoformat().replace(":", "-")
        filename = f"mission_{goal_id}_{timestamp}.json"
        filepath = self.missions_dir / filename

        with open(filepath, "w") as f:
            json.dump(mission_record, f, indent=2, default=str)

        return str(filepath)

    def load_missions(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Load all saved mission records."""
        missions = []
        for filepath in sorted(self.missions_dir.glob("mission_*.json"), reverse=True):
            try:
                with open(filepath, "r") as f:
                    mission = json.load(f)
                    missions.append(mission)
            except json.JSONDecodeError:
                continue

        if limit:
            return missions[:limit]
        return missions

    def save_learning_metrics(self, metrics: dict[str, Any]) -> str:
        """Save learning metrics and return the file path."""
        timestamp = datetime.now().isoformat().replace(":", "-")
        filename = f"learning_{timestamp}.json"
        filepath = self.learning_dir / filename

        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2, default=str)

        return str(filepath)

    def load_latest_metrics(self) -> dict[str, Any] | None:
        """Load the most recent learning metrics."""
        metrics_files = sorted(self.learning_dir.glob("learning_*.json"), reverse=True)
        if not metrics_files:
            return None

        try:
            with open(metrics_files[0], "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def get_statistics(self) -> dict[str, Any]:
        """Return aggregated statistics from all saved missions."""
        missions = self.load_missions()
        if not missions:
            return {
                "total_missions": 0,
                "total_tasks": 0,
                "completed_missions": 0,
                "failed_missions": 0,
                "success_rate": 0.0,
            }

        completed = sum(1 for m in missions if m.get("status") == "completed")
        failed = sum(1 for m in missions if m.get("status") == "failed")
        total_tasks = sum(m.get("tasks_count", 0) for m in missions)

        return {
            "total_missions": len(missions),
            "total_tasks": total_tasks,
            "completed_missions": completed,
            "failed_missions": failed,
            "success_rate": completed / len(missions) if missions else 0.0,
        }
