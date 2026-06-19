"""Unit tests for the offline learning domain."""

import pytest

from app.schemas.guide import LearningPathRequest
from app.services.learning import (
    KeywordCatalogResolver,
    LearningPathBuilder,
    TutorContextService,
)
from app.services.learning_service import (
    CATALOGS,
    COMMON,
    LOCALIZED_GENERIC_SEEDS,
    SUB_CATALOGS,
    _quiz,
    build_fallback_learning_path,
)


@pytest.mark.parametrize(
    ("career_name", "expected"),
    [
        ("Software Engineer", "it_software"),
        ("Data fanlari mutaxassisi", "it_data"),
        ("UX/UI-дизайнер", "design_ux"),
        ("Moliyaviy tahlilchi", "finance_analyst"),
        ("Klinik tadqiqotchi", "healthcare_research"),
        ("Unknown role", "generic"),
    ],
)
def test_catalog_resolver_supports_localized_career_names(
    career_name: str,
    expected: str,
):
    assert KeywordCatalogResolver().resolve(career_name) == expected


def test_catalog_resolver_can_return_legacy_broad_domain():
    assert KeywordCatalogResolver().resolve_broad("Software Engineer") == "technology"


@pytest.mark.parametrize("language", ["en", "ru", "uz"])
def test_fallback_learning_path_has_production_shape(language: str):
    path = build_fallback_learning_path(
        LearningPathRequest(
            language=language,
            career_name="Completely Unknown Career",
        )
    )

    assert len(path.modules) == 6
    assert len({module.id for module in path.modules}) == 6
    assert all(len(module.objectives) == 3 for module in path.modules)
    assert all(len(module.lessons) == 5 for module in path.modules)
    assert all(len(module.quiz) == 5 for module in path.modules)
    assert all(
        len(question.options) == 4
        for module in path.modules
        for question in module.quiz
    )


def test_path_builder_accepts_injected_resolver():
    class FixedResolver:
        def resolve(self, career_name: str) -> str:
            return "technology"

    builder = LearningPathBuilder(
        resolver=FixedResolver(),
        common=COMMON,
        broad_catalogs=CATALOGS,
        specialized_catalogs=SUB_CATALOGS,
        generic_catalogs=LOCALIZED_GENERIC_SEEDS,
        quiz_factory=_quiz,
    )

    path = builder.build(
        LearningPathRequest(language="en", career_name="Custom internal title")
    )

    assert path.modules[0].title == CATALOGS["technology"][0][0]


def test_tutor_context_extracts_lessons_and_builds_localized_suggestions():
    service = TutorContextService()
    context = "Description\nLessons: Variables; Functions; Loops\nProject: CLI"

    assert service.lessons(context) == ("Variables", "Functions", "Loops")
    assert (
        service.pick_lesson(service.lessons(context), "function nima?") == "Functions"
    )
    assert service.suggestions(context, "Python", "uz") == [
        '"Variables"ni misol bilan tushuntir',
        '"Functions" bo\'yicha amaliy mashq ber',
        "Meni test qil",
    ]
