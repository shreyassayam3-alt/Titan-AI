from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import Any

from core.tools import PythonToolManager


class MissionToolRunner:
    """Bridges mission context to the Python tool manager."""

    def __init__(self, tool_manager: PythonToolManager | None = None) -> None:
        self._tool_manager = tool_manager or PythonToolManager()

    async def run(self, goal: str, *, context: Any | None = None) -> dict[str, Any]:
        discovered = await self._tool_manager.discover(query=goal)
        tool_name = None
        if discovered:
            tool_name = discovered[0].name
        if tool_name is None:
            return {"used_tool": False, "reason": "No suitable tool discovered."}
        if tool_name == "filesystem_read":
            arguments = {"path": "README.md"}
        elif tool_name == "filesystem_write":
            arguments = {"path": "tmp_tool_test.txt", "content": "tool demo"}
        else:
            arguments = {"left": 2, "right": 3}
        result = await self._tool_manager.invoke(tool_name, arguments)
        return {"used_tool": result.success, "tool_name": tool_name, "result": asdict(result)}
