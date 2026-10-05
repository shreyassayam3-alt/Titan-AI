"""Persistent learning system that improves over time."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from core.learning.base import Learning
from core.persistence.state_manager import StateManager


class PersistentLearning(Learning):
    """Records task outcomes and generates optimization recommendations."""

    def __init__(self, state_manager: StateManager) -> None:
        """Initialize with a state manager for persistence."""
        self._state_manager = state_manager
        self._session_experiences: list[dict[str, Any]] = []
        self._session_failures: list[dict[str, Any]] = []
        self._task_patterns: defaultdict[str, dict[str, Any]] = defaultdict(lambda: {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "avg_execution_time": 0.0,
        })

    async def record_completed_task(self, task: Any, result: Any) -> None:
        """Record a successful task execution."""
        task_type = self._get_task_type(task)
        pattern = self._task_patterns[task_type]
        pattern["executions"] += 1
        pattern["successes"] += 1

        self._session_experiences.append({
            "task_type": task_type,
            "task": str(task),
            "result": str(result),
            "outcome": "success",
            "timestamp": datetime.now().isoformat(),
        })

    async def record_failed_task(self, task: Any, error: Exception) -> None:
        """Record a failed task execution."""
        task_type = self._get_task_type(task)
        pattern = self._task_patterns[task_type]
        pattern["executions"] += 1
        pattern["failures"] += 1

        self._session_failures.append({
            "task_type": task_type,
            "task": str(task),
            "error": str(error),
            "outcome": "failure",
            "timestamp": datetime.now().isoformat(),
        })

    async def retrieve_experience(
        self, query: Any, *, limit: int | None = None
    ) -> tuple[dict[str, Any], ...]:
        """Retrieve past experiences matching the query."""
        matches = []
        query_str = str(query).lower()

        for exp in self._session_experiences:
            if query_str in exp.get("task_type", "").lower():
                matches.append(exp)

        if limit:
            return tuple(matches[-limit:])
        return tuple(matches)

    def get_optimization_recommendations(self) -> list[str]:
        """Generate recommendations for execution optimization."""
        recommendations = []

        for task_type, pattern in self._task_patterns.items():
            if pattern["executions"] < 2:
                continue

            success_rate = pattern["successes"] / pattern["executions"]

            if success_rate == 1.0:
                recommendations.append(
                    f"✅ '{task_type}': Consistently successful. Can increase parallelization."
                )
            elif success_rate >= 0.8:
                recommendations.append(
                    f"⚠️  '{task_type}': Good success rate ({success_rate:.1%}). Monitor edge cases."
                )
            elif success_rate >= 0.5:
                recommendations.append(
                    f"🔧 '{task_type}': Moderate success rate ({success_rate:.1%}). Needs refinement."
                )
            else:
                recommendations.append(
                    f"❌ '{task_type}': Low success rate ({success_rate:.1%}). Requires redesign."
                )

        return recommendations

    def persist_learning_metrics(self) -> dict[str, Any]:
        """Save learning metrics to persistent storage."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_experiences": len(self._session_experiences),
            "total_failures": len(self._session_failures),
            "task_patterns": dict(self._task_patterns),
            "recommendations": self.get_optimization_recommendations(),
        }

        self._state_manager.save_learning_metrics(metrics)
        return metrics

    def _get_task_type(self, task: Any) -> str:
        """Extract task type from task object."""
        if hasattr(task, "title"):
            title = str(task.title).lower()
            # Extract first meaningful word as task type
            parts = title.split(":")
            return parts[0].strip() if parts else "unknown"
        return "unknown"
