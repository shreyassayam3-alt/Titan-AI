"""Skill registration and module discovery."""

import inspect
from types import ModuleType

from core.skills.base import Skill


class SkillRegistry:
    """Stores named skills and discovers concrete skill classes from modules."""

    def __init__(self) -> None:
        """Create an empty skill registry."""
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """Register one concrete skill under its stable name."""
        if not skill.name:
            raise ValueError("A skill must define a non-empty name.")
        if skill.name in self._skills:
            raise ValueError(f"A skill named '{skill.name}' is already registered.")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        """Return a registered skill by name, if present."""
        return self._skills.get(name)

    def names(self) -> tuple[str, ...]:
        """Return all registered skill names in registration order."""
        return tuple(self._skills)

    def discover(self, module: ModuleType) -> tuple[str, ...]:
        """Instantiate and register concrete zero-argument skill classes in ``module``."""
        discovered: list[str] = []
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if candidate is Skill or not issubclass(candidate, Skill) or inspect.isabstract(candidate):
                continue
            if candidate.__module__ != module.__name__:
                continue
            skill = candidate()
            self.register(skill)
            discovered.append(skill.name)
        return tuple(discovered)
