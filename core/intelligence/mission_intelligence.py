"""Adaptive mission intelligence that learns and improves execution strategy."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any


class MissionIntelligence:
    """Analyzes mission patterns and adapts execution for improved outcomes."""

    def __init__(self) -> None:
        """Initialize the intelligence system."""
        self._mission_patterns: dict[str, dict[str, Any]] = {}
        self._task_strategies: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        self._execution_timeline: list[dict[str, Any]] = []
        self._performance_metrics: dict[str, float] = {}

    async def analyze_mission(self, mission_record: dict[str, Any]) -> dict[str, Any]:
        """Analyze a mission execution and extract intelligence."""
        goal_type = self._extract_goal_type(mission_record.get("goal_title", ""))
        tasks = mission_record.get("tasks", [])
        status = mission_record.get("status", "unknown")

        # Record the execution
        execution_data = {
            "goal_type": goal_type,
            "task_count": len(tasks),
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "success": status == "completed",
        }
        self._execution_timeline.append(execution_data)

        # Update goal type patterns
        if goal_type not in self._mission_patterns:
            self._mission_patterns[goal_type] = {
                "total_executions": 0,
                "successes": 0,
                "failures": 0,
                "avg_tasks": 0.0,
                "improvement_score": 0.0,
            }

        pattern = self._mission_patterns[goal_type]
        pattern["total_executions"] += 1
        if status == "completed":
            pattern["successes"] += 1
        else:
            pattern["failures"] += 1
        pattern["avg_tasks"] = (pattern["avg_tasks"] * (pattern["total_executions"] - 1) + len(tasks)) / pattern["total_executions"]

        # Store task strategies for this goal type
        for task in tasks:
            self._task_strategies[goal_type].append({
                "title": task.get("title"),
                "status": task.get("status"),
                "timestamp": datetime.now().isoformat(),
            })

        return self._compute_insights(goal_type)

    def get_adaptive_strategy(self, goal_text: str) -> dict[str, Any]:
        """Return an adaptive execution strategy based on learned patterns."""
        goal_type = self._extract_goal_type(goal_text)
        pattern = self._mission_patterns.get(goal_type)

        if not pattern:
            return {
                "strategy": "default",
                "reasoning": "No prior patterns found for this goal type.",
                "recommendations": [],
            }

        success_rate = pattern["successes"] / pattern["total_executions"] if pattern["total_executions"] > 0 else 0.0
        recommendations = self._generate_strategy_recommendations(goal_type, pattern, success_rate)

        return {
            "strategy": "adaptive",
            "goal_type": goal_type,
            "success_rate": success_rate,
            "total_executions": pattern["total_executions"],
            "recommended_task_count": int(pattern["avg_tasks"]),
            "recommendations": recommendations,
            "improvement_potential": self._compute_improvement_potential(success_rate),
        }

    def get_performance_report(self) -> dict[str, Any]:
        """Generate a comprehensive performance report."""
        total_missions = len(self._execution_timeline)
        successful_missions = sum(1 for m in self._execution_timeline if m.get("success"))
        overall_success_rate = successful_missions / total_missions if total_missions > 0 else 0.0

        goal_type_stats = {}
        for goal_type, pattern in self._mission_patterns.items():
            success_rate = pattern["successes"] / pattern["total_executions"] if pattern["total_executions"] > 0 else 0.0
            goal_type_stats[goal_type] = {
                "success_rate": success_rate,
                "total_executions": pattern["total_executions"],
                "avg_tasks": pattern["avg_tasks"],
            }

        return {
            "total_missions": total_missions,
            "successful_missions": successful_missions,
            "overall_success_rate": overall_success_rate,
            "goal_types_analyzed": len(self._mission_patterns),
            "goal_type_statistics": goal_type_stats,
            "learning_progress": self._compute_learning_progress(),
        }

    def _extract_goal_type(self, goal_text: str) -> str:
        """Extract a category from goal text."""
        text_lower = goal_text.lower()
        keywords = text_lower.split()
        stop_words = {"the", "a", "an", "and", "or", "is", "for", "to", "of", "in", "on", "with"}
        meaningful_words = [w for w in keywords if w not in stop_words and len(w) > 3]
        return meaningful_words[0] if meaningful_words else "general"

    def _compute_insights(self, goal_type: str) -> dict[str, Any]:
        """Compute insights from the current pattern."""
        pattern = self._mission_patterns[goal_type]
        success_rate = pattern["successes"] / pattern["total_executions"] if pattern["total_executions"] > 0 else 0.0

        insights = {
            "goal_type": goal_type,
            "success_rate": success_rate,
            "total_executions": pattern["total_executions"],
        }

        if success_rate >= 0.9:
            insights["status"] = "excellent"
            insights["message"] = "This goal type has excellent success rate. Consider scaling up."
        elif success_rate >= 0.7:
            insights["status"] = "good"
            insights["message"] = "Good success rate. Minor optimizations possible."
        elif success_rate >= 0.5:
            insights["status"] = "moderate"
            insights["message"] = "Moderate success. Needs optimization and refinement."
        else:
            insights["status"] = "poor"
            insights["message"] = "Low success rate. Significant redesign needed."

        return insights

    def _generate_strategy_recommendations(self, goal_type: str, pattern: dict[str, Any], success_rate: float) -> list[str]:
        """Generate actionable recommendations for execution."""
        recommendations = []

        if success_rate >= 0.9:
            recommendations.append("✅ Maintain current approach - excellent results")
            recommendations.append("🚀 Consider parallelizing tasks for faster execution")
        elif success_rate >= 0.7:
            recommendations.append("✓ Continue with current strategy")
            recommendations.append("🔄 Review edge cases that caused failures")
        elif success_rate >= 0.5:
            recommendations.append("⚠️  Significant failures detected")
            recommendations.append("🔧 Optimize task decomposition strategy")
            recommendations.append("📊 Analyze failure patterns for root causes")
        else:
            recommendations.append("❌ Critical failures - strategy redesign needed")
            recommendations.append("🎯 Simplify goal scope and task requirements")
            recommendations.append("🔬 Implement detailed error logging")

        strategies = self._task_strategies.get(goal_type, [])
        if len(strategies) >= 3:
            most_common_task = max(
                set(s["title"] for s in strategies),
                key=lambda x: sum(1 for s in strategies if s["title"] == x),
            )
            recommendations.append(f"📌 Key recurring task: {most_common_task}")

        return recommendations

    def _compute_improvement_potential(self, current_success_rate: float) -> str:
        """Estimate how much improvement is possible."""
        gap_to_perfect = 1.0 - current_success_rate
        if gap_to_perfect < 0.1:
            return "minimal"
        elif gap_to_perfect < 0.3:
            return "moderate"
        elif gap_to_perfect < 0.5:
            return "significant"
        else:
            return "critical"

    def _compute_learning_progress(self) -> dict[str, Any]:
        """Measure how much the system has learned."""
        if not self._execution_timeline:
            return {"stage": "initialization", "progress": 0.0}

        recent_success_rate = sum(1 for m in self._execution_timeline[-10:] if m.get("success")) / min(10, len(self._execution_timeline))
        early_success_rate = sum(1 for m in self._execution_timeline[:10] if m.get("success")) / min(10, len(self._execution_timeline))

        improvement = recent_success_rate - early_success_rate

        if len(self._execution_timeline) < 5:
            stage = "initialization"
        elif len(self._execution_timeline) < 20:
            stage = "learning"
        elif improvement > 0.1:
            stage = "improving"
        elif improvement < -0.1:
            stage = "degrading"
        else:
            stage = "stable"

        return {
            "stage": stage,
            "missions_analyzed": len(self._execution_timeline),
            "improvement_trend": improvement,
            "recent_success_rate": recent_success_rate,
        }
