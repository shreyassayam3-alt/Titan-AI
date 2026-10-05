import asyncio

from apps.mission_runner.mission_tool_runner import MissionToolRunner


def test_mission_tool_runner_invokes_builtin_tool() -> None:
    async def run() -> None:
        runner = MissionToolRunner()
        result = await runner.run("read a file")
        assert result["used_tool"] is True
        assert result["tool_name"].startswith("filesystem")

    asyncio.run(run())
