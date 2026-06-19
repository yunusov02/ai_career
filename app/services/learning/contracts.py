"""Interfaces for the learning domain.

The concrete implementations are intentionally small and replaceable so the
learning workflow can be tested without importing API, database, or AI code.
"""

from collections.abc import Callable, Mapping, Sequence
from typing import Literal, Protocol, TypeAlias

from app.schemas.guide import ModuleQuizQuestion


ResourceType: TypeAlias = Literal[
    "book",
    "course",
    "article",
    "video",
    "documentation",
    "community",
]
ResourceSeed: TypeAlias = tuple[str, str, ResourceType]
ModuleSeed: TypeAlias = tuple[str, str, list[str], list[ResourceSeed]]
QuizFactory: TypeAlias = Callable[
    [str, str, list[str], str],
    list[ModuleQuizQuestion],
]


class CatalogResolver(Protocol):
    """Resolve a localized career name to a curriculum catalog key."""

    def resolve(self, career_name: str) -> str: ...


class LearningCatalogs(Protocol):
    """Read-only curriculum data required by the path builder."""

    common: Mapping[str, Mapping[str, object]]
    broad: Mapping[str, Sequence[ModuleSeed]]
    specialized: Mapping[str, Sequence[ModuleSeed]]
    generic: Mapping[str, Sequence[ModuleSeed]]
