"""Enhanced CLI with persistent mission history and self-learning."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.config.base import Config
from core.models import Goal
from core.orchestrator.learning_orchestrator import LearningOrchestrator
from core.persistence import PersistentLearning, StateManager


class TitanCLI:
    """Enhanced CLI for TITAN mission execution with persistence and learning."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize the CLI with persistent state management."""
        self.config = config or Config.from_env()
        self.state_manager = StateManager(self.config.state_dir)
        self.persistent_learning = PersistentLearning(self.state_manager)
        self.orchestrator = LearningOrchestrator.create_default()

    async def run_mission(self, goal_text: str, description: str | None = None) -> dict:
        """Execute a mission and persist the results."""
        print(f"\n{'='*70}")
        print(f"🚀 TITAN MISSION STARTED")
        print(f"{'='*70}")
        print(f"⏰ Time: {datetime.now().isoformat()}")
        print(f"📋 Goal: {goal_text}")
        if description:
            print(f"📝 Description: {description}")
        print(f"🔧 Environment: {self.config.environment}")
        print(f"{'='*70}\n")

        goal = Goal(
            title=goal_text,
            description=description or goal_text,
            priority=1,
        )

        try:
            print("[1/5] 🧠 Planning task decomposition...")
            report = await self.orchestrator.execute(goal)

            print("[2/5] ✅ Tasks executed successfully")
            print(f"[3/5] 📚 Learning from outcomes...")

            # Record learning
            for task, result in zip(report.tasks, report.results):
                await self.persistent_learning.record_completed_task(task, result)

            print(f"[4/5] 💾 Persisting mission state...")

            # Build and save mission record
            mission_record = {
                "goal_id": goal.id,
                "goal_title": goal.title,
                "goal_description": goal.description,
                "tasks_count": len(report.tasks),
                "results_count": len(report.results),
                "status": report.goal.status.value,
                "timestamp": datetime.now().isoformat(),
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "status": task.status.value,
                    }
                    for task in report.tasks
                ],
                "results": [
                    {
                        "status": result.get("status", "unknown"),
                        "output": result.get("output", ""),
                    }
                    for result in report.results
                ],
            }

            mission_path = self.state_manager.save_mission(mission_record)
            print(f"[5/5] 📊 Computing optimization metrics...\n")

            # Display results
            print(f"{'='*70}")
            print(f"✨ MISSION COMPLETED")
            print(f"{'='*70}")
            print(f"Goal ID: {goal.id}")
            print(f"Status: {report.goal.status.value.upper()}")
            print(f"Tasks Executed: {len(report.tasks)}")
            print(f"Results Collected: {len(report.results)}")
            print(f"Saved to: {mission_path}")
            print(f"Success Rate: {self.orchestrator.success_rate():.1%}")
            print(f"{'='*70}\n")

            print("📋 Task Execution Summary:")
            for i, task in enumerate(report.tasks, 1):
                print(f"  {i}. {task.title}")
                print(f"     Status: {task.status.value}")
                if i <= len(report.results):
                    result = report.results[i - 1]
                    print(f"     Output: {result.get('output', 'N/A')}")
                print()

            return mission_record

        except Exception as error:
            print(f"\n❌ MISSION FAILED")
            print(f"Error: {str(error)}")
            print(f"{'='*70}\n")
            raise

    async def run_interactive(self) -> None:
        """Run TITAN in interactive experimental mode."""
        print("\n" + "="*70)
        print("🤖 TITAN AI - Autonomous Mission Executor")
        print("="*70)
        print("Enter mission goals to run through TITAN's autonomous system.")
        print("Commands: 'history' | 'stats' | 'learn' | 'export' | 'exit'\n")

        while True:
            try:
                goal_text = input("🎯 Enter mission goal (or command): ").strip()

                if goal_text.lower() == "exit":
                    print("\n👋 Goodbye!\n")
                    break
                elif goal_text.lower() == "history":
                    self._print_history()
                elif goal_text.lower() == "stats":
                    self._print_stats()
                elif goal_text.lower() == "learn":
                    self._print_learning_recommendations()
                elif goal_text.lower() == "export":
                    self._export_data()
                elif goal_text:
                    description = input("   Description (optional, press Enter to skip): ").strip()
                    await self.run_mission(goal_text, description or None)

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user.\n")
                break
            except Exception as error:
                print(f"Error: {error}\n")

    def _print_history(self) -> None:
        """Display mission execution history."""
        missions = self.state_manager.load_missions(limit=10)
        if not missions:
            print("\n📭 No missions executed yet.\n")
            return

        print(f"\n{'='*70}")
        print(f"📜 MISSION HISTORY (Last {len(missions)} missions)")
        print(f"{'='*70}")
        for i, mission in enumerate(missions, 1):
            timestamp = mission.get("timestamp", "Unknown")
            print(
                f"{i}. {mission['goal_title']} | "
                f"Status: {mission['status'].upper()} | "
                f"Tasks: {mission['tasks_count']} | "
                f"Time: {timestamp[:19]}"
            )
        print()

    def _print_stats(self) -> None:
        """Display execution statistics."""
        stats = self.state_manager.get_statistics()
        print(f"\n{'='*70}")
        print(f"📊 EXECUTION STATISTICS")
        print(f"{'='*70}")
        print(f"Total Missions: {stats['total_missions']}")
        print(f"Completed: {stats['completed_missions']}")
        print(f"Failed: {stats['failed_missions']}")
        print(f"Total Tasks Executed: {stats['total_tasks']}")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        print(f"{'='*70}\n")

    def _print_learning_recommendations(self) -> None:
        """Display self-learning optimization recommendations."""
        metrics = self.persistent_learning.persist_learning_metrics()
        recommendations = metrics.get("recommendations", [])

        print(f"\n{'='*70}")
        print(f"🧠 LEARNING RECOMMENDATIONS")
        print(f"{'='*70}")

        if not recommendations:
            print("No patterns identified yet. Run more missions to build learning data.")
        else:
            for rec in recommendations:
                print(f"  {rec}")

        print(f"\nTask Patterns Analyzed: {len(metrics.get('task_patterns', {}))}")
        print(f"Total Experiences: {metrics.get('total_experiences', 0)}")
        print(f"{'='*70}\n")

    def _export_data(self) -> None:
        """Export mission data and learning metrics."""
        export_dir = Path(self.config.state_dir) / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        # Export missions
        missions = self.state_manager.load_missions()
        missions_file = export_dir / f"missions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(missions_file, "w") as f:
            json.dump(missions, f, indent=2, default=str)

        # Export stats
        stats = self.state_manager.get_statistics()
        stats_file = export_dir / f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2, default=str)

        print(f"\n{'='*70}")
        print(f"📁 DATA EXPORTED")
        print(f"{'='*70}")
        print(f"Missions: {missions_file}")
        print(f"Statistics: {stats_file}")
        print(f"{'='*70}\n")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="🤖 TITAN AI - Autonomous Mission Executor with Self-Learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  # Run a single mission
  python -m apps.titan_cli "Research market trends" --description "Analyze current AI market"

  # Run interactive mode
  python -m apps.titan_cli --interactive

  # Set custom environment
  TITAN_ENV=production python -m apps.titan_cli "Deploy latest changes"

  # Custom state directory
  python -m apps.titan_cli --state-dir /tmp/titan --interactive
        """,
    )

    parser.add_argument(
        "goal",
        nargs="?",
        default=None,
        help="Mission goal to execute",
    )
    parser.add_argument(
        "--description",
        default=None,
        help="Extended goal description",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode",
    )
    parser.add_argument(
        "--env",
        default="development",
        choices=["development", "staging", "production"],
        help="Runtime environment",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity",
    )
    parser.add_argument(
        "--state-dir",
        default="./.titan",
        help="Directory for persistent mission state",
    )

    return parser


async def main(argv: list[str] | None = None) -> int:
    """Main entry point for the TITAN CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    config = Config(
        environment=args.env,
        debug=args.env == "development",
        log_level=args.log_level,
        state_dir=args.state_dir,
    )

    cli = TitanCLI(config)

    if args.interactive or (not args.goal and not args.interactive):
        await cli.run_interactive()
    else:
        if not args.goal:
            parser.error("the following arguments are required: goal")
        try:
            await cli.run_mission(args.goal, args.description)
        except Exception:
            return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
