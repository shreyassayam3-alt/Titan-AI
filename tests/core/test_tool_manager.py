import asyncio

from core.tools import PythonToolManager
from core.reasoner.tool_aware import ToolAwareReasoner


def test_python_tool_manager_discovers_and_invokes_builtin_tools() -> None:
    async def run() -> None:
        manager = PythonToolManager()
        discovered = await manager.discover(query="file")
        assert discovered
        result = await manager.invoke("filesystem_write", {"path": "tmp_tool_test.txt", "content": "hello"})
        assert result.success is True
        read_result = await manager.invoke("filesystem_read", {"path": "tmp_tool_test.txt"})
        assert read_result.output == "hello"

    asyncio.run(run())


def test_tool_aware_reasoner_selects_tool_for_goal() -> None:
    async def run() -> None:
        manager = PythonToolManager()
        reasoner = ToolAwareReasoner(tool_registry=manager)
        selection = await reasoner.select_strategy(["default"], context={"goal": "read a file"})
        assert selection.startswith("tool:")

    asyncio.run(run())
