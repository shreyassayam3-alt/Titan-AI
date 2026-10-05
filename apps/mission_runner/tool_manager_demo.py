from __future__ import annotations

import asyncio

from core.tools import PythonToolManager


async def run_tool_manager_demo() -> None:
    manager = PythonToolManager()
    discovered = await manager.discover(query="file")
    print([tool.name for tool in discovered])
    result = await manager.invoke("calculator_add", {"left": 2, "right": 3})
    print(result.output)


if __name__ == "__main__":
    asyncio.run(run_tool_manager_demo())
