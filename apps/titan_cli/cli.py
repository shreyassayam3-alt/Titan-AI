"""Live CLI for running TITAN missions with real-time feedback."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.config.base import Config
from core.models import Goal
from core.orchestrator.learning_orchestrator import LearningOrchestrator


class TitanCLI:
    """Interactive CLI for TITAN mission execution and monitoring."""

    def __init__(self, config: Config | None = None) -> None:
        """Initialize the CLI with runtime configuration."""
        self.config = config or Config.from_env()
        self.orchestrator = LearningOrchestrator.create_default()
        self.mission_history: list[dict] = []

    async def run_mission(self, goal_text: str, description: str | None = None) -> dict:
        """Execute a single mission and return structured results."""
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
            print("[1/4] 🧠 Planning task decomposition...")
            report = await self.orchestrator.execute(goal)

            print("[2/4] ✅ Tasks executed successfully")
            print(f"[3/4] 📚 Learning from outcomes...")
            print(f"[4/4] 💾 Persisting mission state...\n")

            # Build mission record
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

            self.mission_history.append(mission_record)

            # Display results
            print(f"{'='*70}")
            print(f"✨ MISSION COMPLETED")
            print(f"{'='*70}")
            print(f"Goal ID: {goal.id}")
            print(f"Status: {report.goal.status.value.upper()}")
            print(f"Tasks Executed: {len(report.tasks)}")
            print(f"Results Collected: {len(report.results)}")
            print(f"Success Rate: {self.orchestrator.success_rate():.1%}")
            print(f"{'='*70}\n")

            print("📊 Task Execution Summary:")
            for i, task in enumerate(report.tasks, 1):
                print(f"  {i}. {task.title}")
                print(f"     Status: {task.status.value}")
                if i < len(report.results):
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
        """Run TITAN in interactive mode for continuous experimentation."""
        print("\n" + "="*70)
        print("🤖 TITAN AI - Autonomous Mission Executor")
        print("="*70)
        print("Enter mission goals to run them through TITAN's autonomous system.")
        print("Type 'exit' to quit, 'history' to see past missions, 'stats' for summary.\n")

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
                elif goal_text:
                    description = input("   Description (optional, press Enter to skip): ").strip()
                    await self.run_mission(goal_text, description or None)

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user.\n")
                break
            except Exception as error:
                print(f"Error: {error}\n")

    def _print_history(self) -> None:
        """Display mission history."""
        if not self.mission_history:
            print("\n📭 No missions executed yet.\n")
            return

        print(f"\n{'='*70}")
        print(f"📜 MISSION HISTORY ({len(self.mission_history)} total)")
        print(f"{'='*70}")
        for i, mission in enumerate(self.mission_history, 1):
            print(
                f"{i}. {mission['goal_title']} | "
                f"Status: {mission['status']} | "
                f"Tasks: {mission['tasks_count']}"
            )
        print()

    def _print_stats(self) -> None:
        """Display execution statistics."""
        print(f"\n{'='*70}")
        print(f"📈 EXECUTION STATISTICS")
        print(f"{'='*70}")
        print(f"Total Missions: {len(self.mission_history)}")
        print(f"Total Tasks: {sum(m['tasks_count'] for m in self.mission_history)}")
        print(f"Success Rate: {self.orchestrator.success_rate():.1%}")
        print()


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="TITAN AI - Autonomous Mission Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a single mission
  python -m apps.titan_cli.cli "Research market trends" --description "Analyze current AI market"

  # Run interactive mode
  python -m apps.titan_cli.cli --interactive

  # Set custom environment
  TITAN_ENV=production python -m apps.titan_cli.cli "Deploy latest changes"
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

    return parser


async def main(argv: list[str] | None = None) -> int:
    """Main entry point for the TITAN CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    config = Config(
        environment=args.env,
        debug=args.env == "development",
        log_level=args.log_level,
    )

    cli = TitanCLI(config)

    if args.interactive or (not args.goal and not args.interactive):
        await cli.run_interactive()
    else:
        if not args.goal:
            parser.error("the following arguments are required: goal")
        try:
            await cli.run_mission(args.goal, args.description)
        except Exception as error:
            return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
