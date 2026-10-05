from __future__ import annotations

import inspect
import os
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import ModuleType
from typing import Any

from core.tools.base import ToolRegistry


@dataclass(slots=True)
class ToolDefinition:
    """Metadata for an auto-discovered Python tool."""

    name: str
    description: str
    callable: Callable[..., Any]
    module: str
    signature: str = ""


@dataclass(slots=True)
class ToolInvocationResult:
    """Normalized result of a tool invocation."""

    tool_name: str
    success: bool
    output: Any
    error: str | None = None


class PythonToolManager(ToolRegistry):
    """Discovers Python callables and exposes them as tools for missions."""

    def __init__(self, modules: Sequence[ModuleType] | None = None) -> None:
        self._modules = list(modules or [])
        self._tools: dict[str, ToolDefinition] = {}
        self._discover_builtin_tools()

    async def discover(self, *, query: str | None = None) -> Sequence[ToolDefinition]:
        self._refresh()
        tools = list(self._tools.values())
        if query:
            query_lower = query.lower()
            tools = [tool for tool in tools if query_lower in tool.name.lower() or query_lower in tool.description.lower()]
        return tools

    async def invoke(self, tool_name: str, arguments: Mapping[str, Any], *, context: Any | None = None) -> ToolInvocationResult:
        self._refresh()
        tool = self._tools.get(tool_name)
        if tool is None:
            raise KeyError(f"Unknown tool '{tool_name}'.")
        try:
            result = tool.callable(**dict(arguments))
            if inspect.isawaitable(result):
                result = await result
            return ToolInvocationResult(tool_name=tool_name, success=True, output=result)
        except Exception as exc:  # pragma: no cover - defensive path
            return ToolInvocationResult(tool_name=tool_name, success=False, output=None, error=str(exc))

    def register(self, tool: Callable[..., Any], *, name: str | None = None, description: str | None = None) -> None:
        tool_name = name or getattr(tool, "__name__", "tool")
        self._tools[tool_name] = ToolDefinition(
            name=tool_name,
            description=description or getattr(tool, "__doc__", "") or tool_name,
            callable=tool,
            module=getattr(tool, "__module__", "__main__"),
            signature=str(inspect.signature(tool)),
        )

    def _refresh(self) -> None:
        if not self._tools:
            self._discover_builtin_tools()

    def _discover_builtin_tools(self) -> None:
        self.register(self._filesystem_read, name="filesystem_read", description="Read a file from the filesystem")
        self.register(self._filesystem_write, name="filesystem_write", description="Write content to a file")
        self.register(self._calculator_add, name="calculator_add", description="Add two numbers")
        self.register(self._calculator_multiply, name="calculator_multiply", description="Multiply two numbers")
        self.register(self._python_exec, name="python_exec", description="Execute a Python expression")
        self.register(self._browser_open, name="browser_open", description="Open a URL in a browser")

    def _filesystem_read(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()

    def _filesystem_write(self, path: str, content: str) -> str:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return f"wrote {path}"

    def _calculator_add(self, left: float, right: float) -> float:
        return float(left + right)

    def _calculator_multiply(self, left: float, right: float) -> float:
        return float(left * right)

    def _python_exec(self, code: str) -> str:
        result = eval(code, {"__builtins__": __builtins__})
        return str(result)

    def _browser_open(self, url: str) -> str:
        return f"browser-open:{url}"
