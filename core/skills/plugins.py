"""File-system plugin loader for independently added skill modules."""

import importlib.util
from pathlib import Path
from types import ModuleType

from core.skills.registry import SkillRegistry


class PluginLoader:
    """Loads Python skill modules from a directory without kernel changes."""

    def __init__(self, registry: SkillRegistry) -> None:
        """Initialize the loader with the registry receiving discovered skills."""
        self._registry = registry

    def load_directory(self, directory: Path) -> tuple[str, ...]:
        """Load each Python module in ``directory`` and register its skills."""
        if not directory.is_dir():
            raise ValueError(f"Plugin directory does not exist: {directory}")
        discovered: list[str] = []
        for path in sorted(directory.glob("*.py")):
            if path.name.startswith("_"):
                continue
            discovered.extend(self._registry.discover(self._load_module(path)))
        return tuple(discovered)

    @staticmethod
    def _load_module(path: Path) -> ModuleType:
        """Load one module under a unique, path-derived module name."""
        module_name = f"titan_plugin_{path.stem}_{abs(hash(path.resolve()))}"
        specification = importlib.util.spec_from_file_location(module_name, path)
        if specification is None or specification.loader is None:
            raise ImportError(f"Unable to load plugin module: {path}")
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        return module
