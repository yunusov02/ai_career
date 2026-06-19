"""Career-name classification for offline learning catalogs."""

from functools import lru_cache
from types import MappingProxyType
from typing import Final


SPECIALIZED_RULES: Final = MappingProxyType(
    {
        "it_data": (
            "data scientist",
            "machine learning",
            "ml engineer",
            "ai engineer",
            "deep learning",
            "nlp engineer",
            "data science",
            "data fanlari",
            "ma'lumot fanlari",
            "учёный по данным",
            "data muhandis",
            "аналитик данных",
        ),
        "it_devops": (
            "devops",
            "site reliability",
            "sre",
            "platform engineer",
            "cloud engineer",
            "cloud architect",
            "cloud muhandisi",
            "облачный инженер",
            "devops muhandisi",
        ),
        "it_software": (
            "software engineer",
            "backend developer",
            "frontend developer",
            "full stack",
            "fullstack developer",
            "web developer",
            "mobile developer",
            "dasturchi",
            "разработчик",
            "dasturiy ta'minot muhandisi",
            "dasturiy muhandis",
            "разработчик по",
        ),
        "design_ux": (
            "ux/ui",
            "ux designer",
            "ui designer",
            "user experience",
            "user interface",
            "ux/ui dizayner",
            "ux/ui-дизайнер",
        ),
        "design_graphic": (
            "graphic design",
            "visual design",
            "motion design",
            "illustration",
            "grafik dizayner",
            "графический дизайнер",
            "grafik dizayn",
        ),
        "design_product": (
            "product designer",
            "product design",
            "mahsulot dizayneri",
            "продуктовый дизайнер",
        ),
        "marketing_seo": (
            "seo",
            "search engine optim",
            "o'sish tahlilchisi",
            "аналитик роста",
            "growth analyst",
        ),
        "marketing_content": (
            "content strateg",
            "content market",
            "content writer",
            "copywriter",
            "kontent strateg",
            "контент-стратег",
        ),
        "marketing_digital": (
            "digital market",
            "performance market",
            "growth market",
            "paid media",
            "raqamli marketing",
            "цифровому маркетингу",
            "специалист по цифровому",
        ),
        "finance_investment": (
            "investment",
            "equity",
            "portfolio manager",
            "asset manager",
            "fund manager",
            "venture capital",
            "private equity",
            "investitsiya tahlilchisi",
            "инвестиционный аналитик",
        ),
        "finance_planning": (
            "financial planner",
            "financial advisor",
            "wealth manager",
            "cfp",
            "personal finance",
            "moliyaviy rejalashtiruvchi",
            "финансовый планировщик",
        ),
        "finance_analyst": (
            "financial analyst",
            "finance analyst",
            "business analyst finance",
            "credit analyst",
            "fp&a",
            "moliyaviy tahlilchi",
            "финансовый аналитик",
            "tahlilchi moliy",
        ),
        "engineering_electrical": (
            "electrical engineer",
            "electronics engineer",
            "power engineer",
            "rf engineer",
            "embedded",
            "elektr muhandisi",
            "инженер-электрик",
        ),
        "engineering_civil": (
            "civil engineer",
            "structural engineer",
            "geotechnical",
            "transportation engineer",
            "construction",
            "qurilish muhandisi",
            "гражданский инженер",
        ),
        "engineering_mechanical": (
            "mechanical engineer",
            "manufacturing engineer",
            "product engineer",
            "hvac",
            "aerospace",
            "automotive",
            "mexanika muhandisi",
            "инженер-механик",
        ),
        "healthcare_public": (
            "public health",
            "epidemiolog",
            "health policy",
            "community health",
            "global health",
            "jamoat salomatligi",
            "аналитик общественного здоровья",
        ),
        "healthcare_research": (
            "clinical researcher",
            "clinical trial",
            "medical researcher",
            "biomedical researcher",
            "klinik tadqiqotchi",
            "клинический исследователь",
        ),
        "healthcare_clinician": (
            "nurse",
            "doctor",
            "physician",
            "clinician",
            "medical officer",
            "pharmacist",
            "paramedic",
            "healthcare specialist",
            "sog'liqni saqlash mutaxassisi",
            "специалист в здравоохранении",
        ),
        "education_edtech": (
            "edtech",
            "educational technology",
            "learning technology",
            "ed-tech",
            "ta'lim texnologiyalari mutaxassisi",
            "специалист по образовательным технологиям",
        ),
        "education_designer": (
            "instructional designer",
            "curriculum designer",
            "learning designer",
            "course designer",
            "learning experience designer",
            "ta'lim dasturlari metodisti",
            "методист образовательных программ",
        ),
        "education_teacher": (
            "teacher",
            "educator",
            "instructor",
            "tutor",
            "lecturer",
            "professor",
            "o'qituvchi",
            "muallim",
            "преподаватель",
        ),
        "business_pm": (
            "product manager",
            "product owner",
            "mahsulot menejeri",
            "продакт-менеджер",
        ),
        "business_strategy": (
            "strategy consultant",
            "management consultant",
            "corporate strategy",
            "strategist",
            "strategik konsultant",
            "стратегический консультант",
        ),
        "business_analyst": (
            "business analyst",
            "business analysis",
            "systems analyst",
            "biznes tahlilchi",
            "бизнес-аналитик",
        ),
    }
)

BROAD_RULES: Final = MappingProxyType(
    {
        "technology": (
            "software",
            "developer",
            "data scientist",
            "ai ",
            "ml ",
            "machine learning",
            "it ",
            "devops",
            "cyber",
            "cloud",
            "backend",
            "frontend",
            "fullstack",
            "dasturchi",
            "разработ",
            "программист",
        ),
        "finance": (
            "financ",
            "account",
            "moliya",
            "финанс",
            "invest",
            "banker",
            "tahlilchi moliy",
        ),
        "marketing": (
            "market",
            "маркет",
            "content strateg",
            "seo",
            "brand strateg",
        ),
        "education": (
            "teach",
            "educat",
            "learning designer",
            "o'qituv",
            "ta'lim",
            "образован",
            "teacher",
            "tutor",
            "instructor",
            "curriculum",
        ),
        "design": (
            "ux",
            "ui ",
            "graphic design",
            "visual design",
            "product designer",
            "dizayn",
            "дизайн",
            "motion design",
        ),
        "engineering": (
            "engineer",
            "mechanical",
            "electrical",
            "civil",
            "muhandis",
            "инженер",
        ),
        "healthcare": (
            "health",
            "medical",
            "nurse",
            "doctor",
            "clinical",
            "tibbiy",
            "sog'liq",
            "здравоохр",
            "медик",
            "врач",
        ),
        "business": (
            "business",
            "product manager",
            "strategy",
            "biznes",
            "бизнес",
            "стратег",
            "менеджер продукт",
        ),
    }
)


class KeywordCatalogResolver:
    """Deterministic, cached career classifier.

    Specialized rules are evaluated first. Broad-domain rules provide a safe
    fallback, while unknown careers use the localized generic curriculum.
    """

    @lru_cache(maxsize=512)
    def resolve(self, career_name: str) -> str:
        value = " ".join(career_name.casefold().split())
        for key, keywords in SPECIALIZED_RULES.items():
            if any(keyword in value for keyword in keywords):
                return key
        return self.resolve_broad(career_name)

    @lru_cache(maxsize=512)
    def resolve_broad(self, career_name: str) -> str:
        """Resolve only the broad domain, preserving the legacy contract."""
        value = " ".join(career_name.casefold().split())
        for key, keywords in BROAD_RULES.items():
            if any(keyword in value for keyword in keywords):
                return key
        return "generic"
