from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple


@dataclass(frozen=True)
class ScenarioMeta:
    id: str
    title: str
    tags: List[str]


class ScenarioRegistry:
    def __init__(self) -> None:
        self._items: Dict[str, Tuple[ScenarioMeta, Callable]] = {}

    def register(self, meta: ScenarioMeta, fn: Callable) -> None:
        # Если случайно зарегистрировали дважды — перезатрём (лучше, чем падать)
        self._items[meta.id] = (meta, fn)

    def get(self, scenario_id: str) -> Tuple[ScenarioMeta, Callable]:
        return self._items[scenario_id]

    def list(self) -> List[ScenarioMeta]:
        return [m for (m, _fn) in self._items.values()]


REGISTRY = ScenarioRegistry()


def scenario(id: str, title: str, tags: list[str]):
    def deco(fn):
        REGISTRY.register(ScenarioMeta(id=id, title=title, tags=tags), fn)
        return fn

    return deco