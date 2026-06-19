"""Offline learning-path construction."""

import re
from collections.abc import Mapping, Sequence
from typing import cast

from app.schemas.guide import (
    LearningModule,
    LearningPathRequest,
    LearningPathResponse,
    LearningResource,
)
from app.services.learning.contracts import (
    CatalogResolver,
    ModuleSeed,
    QuizFactory,
)


class LearningPathBuilder:
    """Build validated learning paths from injected catalog data."""

    def __init__(
        self,
        *,
        resolver: CatalogResolver,
        common: Mapping[str, Mapping[str, str | Sequence[str]]],
        broad_catalogs: Mapping[str, Sequence[ModuleSeed]],
        specialized_catalogs: Mapping[str, Sequence[ModuleSeed]],
        generic_catalogs: Mapping[str, Sequence[ModuleSeed]],
        quiz_factory: QuizFactory,
    ) -> None:
        self._resolver = resolver
        self._common = common
        self._broad_catalogs = broad_catalogs
        self._specialized_catalogs = specialized_catalogs
        self._generic_catalogs = generic_catalogs
        self._quiz_factory = quiz_factory

    def build(self, request: LearningPathRequest) -> LearningPathResponse:
        language = request.language
        copy = self._common[language]
        catalog_key = self._resolver.resolve(request.career_name)
        seeds = self._select_seeds(catalog_key, language)
        modules = [
            self._build_module(seed, index, len(seeds), language)
            for index, seed in enumerate(seeds, 1)
        ]
        return LearningPathResponse(
            career_name=request.career_name,
            overview=str(copy["overview"]).format(career=request.career_name),
            total_duration=str(copy["duration"]),
            modules=modules,
        )

    def _select_seeds(self, catalog_key: str, language: str) -> Sequence[ModuleSeed]:
        seeds = (
            self._specialized_catalogs.get(catalog_key)
            or self._broad_catalogs.get(catalog_key)
            or self._generic_catalogs.get(language)
            or self._generic_catalogs["en"]
        )
        if not seeds:
            raise ValueError("Learning catalog must contain at least one module")
        return seeds

    def _build_module(
        self,
        seed: ModuleSeed,
        index: int,
        total: int,
        language: str,
    ) -> LearningModule:
        title, description, lessons, resources = seed
        module_id = self._slug(title, index)
        return LearningModule(
            id=module_id,
            title=title,
            description=description,
            duration=self._duration(index, total),
            objectives=self._objectives(lessons, language),
            lessons=list(lessons),
            project=str(self._common[language]["project"]).format(topic=title),
            resources=[
                LearningResource(title=name, url=url, type=resource_type)
                for name, url, resource_type in resources
            ],
            quiz=self._quiz_factory(module_id, title, list(lessons), language),
        )

    def _objectives(self, lessons: list[str], language: str) -> list[str]:
        if not lessons:
            objectives = self._common[language]["objectives"]
            return list(cast(Sequence[str], objectives))
        suffixes = {
            "en": (
                "— understand and apply in practice",
                "— work with independently",
                "— use in a small project",
            ),
            "uz": (
                "— ni tushunish va amalda qo'llash",
                "— bilan mustaqil ishlash",
                "— asosida kichik loyiha yaratish",
            ),
            "ru": (
                "— понять и применить на практике",
                "— уверенно использовать в работе",
                "— применить в маленьком проекте",
            ),
        }[language]
        picks = (lessons * 3)[:3]
        return [f"{lesson} {suffix}" for lesson, suffix in zip(picks, suffixes)]

    @staticmethod
    def _slug(value: str, index: int) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
        return slug or f"module-{index}"

    @staticmethod
    def _duration(index: int, total: int) -> str:
        if index == 1:
            return "3-4 weeks"
        if index == total:
            return "2-3 weeks"
        return "4-6 weeks"
