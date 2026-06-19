"""Module-context parsing and deterministic tutor suggestions."""

import re
from functools import lru_cache


class TutorContextService:
    """Extract lesson context and produce localized follow-up prompts."""

    _LESSON_HEADER = re.compile(
        r"(?i)^(lessons?|topics?|temalar|uroqlar|уроки|темы)\s*:"
    )
    _WORD = re.compile(r"[\w']+")

    @lru_cache(maxsize=512)
    def lessons(self, module_context: str) -> tuple[str, ...]:
        for line in module_context.splitlines():
            stripped = line.strip()
            if self._LESSON_HEADER.match(stripped):
                raw = re.sub(r"(?i)^[^:]+:", "", stripped).strip()
                items = [
                    re.sub(r"^\d+\.\s*", "", part).strip()
                    for part in re.split(r"[;,]", raw)
                ]
                result = tuple(item for item in items if len(item) > 2)
                if result:
                    return result[:5]
        lines = (
            re.sub(r"^[\s\-*0-9.]+", "", line).strip()
            for line in module_context.splitlines()
        )
        return tuple(line for line in lines if len(line) > 3)[:5]

    def pick_lesson(self, lessons: list[str] | tuple[str, ...], text: str) -> str:
        if not lessons:
            return "the current module topic"
        words = set(self._WORD.findall(text.casefold()))

        def score(lesson: str) -> int:
            lesson_words = set(self._WORD.findall(lesson.casefold()))
            exact = len(words.intersection(lesson_words)) * 2
            prefix = sum(
                1
                for word in words
                for lesson_word in lesson_words
                if min(len(word), len(lesson_word)) >= 4
                and (word.startswith(lesson_word) or lesson_word.startswith(word))
            )
            return exact + prefix

        return max(
            lessons,
            key=score,
        )

    def suggestions(
        self,
        module_context: str,
        module_title: str,
        language: str,
    ) -> list[str]:
        lessons = self.lessons(module_context)
        focus = lessons[0] if lessons else module_title
        second = lessons[1] if len(lessons) > 1 else module_title
        localized = {
            "uz": [
                f'"{focus}"ni misol bilan tushuntir',
                f'"{second}" bo\'yicha amaliy mashq ber',
                "Meni test qil",
            ],
            "ru": [
                f"Объясни «{focus}» на примере",
                f"Дай практическое упражнение по «{second}»",
                "Проверь мои знания",
            ],
            "en": [
                f'Explain "{focus}" with an example',
                f'Give me a practical exercise on "{second}"',
                "Quiz me on this module",
            ],
        }
        return localized.get(language, localized["en"])
