"""
Career Advisor AI Service

Handles AI-powered career recommendations using OpenAI's API.
"""

import json
import re
from typing import List, Dict, Any, Optional, AsyncIterator

from openai import AsyncOpenAI, AuthenticationError, RateLimitError, APIConnectionError
from loguru import logger

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.schemas.ai import AICareerResponse
from app.ai.prompts import CAREER_ADVISOR_PROMPT, CAREER_ADVISOR_SYSTEM_PROMPT
from app.ai.learning_prompts import (
    LEARNING_PATH_PROMPT,
    LEARNING_PATH_SYSTEM_PROMPT,
    MODULE_TUTOR_PROMPT,
    MODULE_TUTOR_SYSTEM_PROMPT,
)
from app.ai.question_prompts import QUESTION_PROMPT, QUESTION_SYSTEM_PROMPT
from app.schemas.guide import (
    GeneratedQuestion,
    GenerateQuestionsRequest,
    LearningPathRequest,
    LearningPathResponse,
    ModuleChatRequest,
    ModuleChatResponse,
)


class CareerAdvisor:
    """AI-powered career advisor. Create a new instance per request."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.openai_model

        if not self.api_key:
            logger.debug("OpenAI API key not configured — fallback mode active")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)

    @property
    def available(self) -> bool:
        return self.client is not None

    def _format_answers_for_prompt(self, answers: List[Dict[str, Any]]) -> str:
        formatted = []
        for i, answer in enumerate(answers, 1):
            question_text = answer.get("question_text", f"Question {i}")
            answer_text = answer.get("answer_text", "No answer provided")
            category = answer.get("category", "General")
            formatted.append(
                f"**Question {i}** ({category}):\n{question_text}\n**Answer**: {answer_text}\n"
            )
        return "\n".join(formatted)

    def _require_client(self) -> AsyncOpenAI:
        if not self.client:
            raise AIServiceError(
                message="OpenAI API key not configured",
                details={"hint": "Set OPENAI_API_KEY in your .env file"},
            )
        return self.client

    def _classify_error(self, exc: Exception) -> AIServiceError:
        if isinstance(exc, AuthenticationError):
            logger.error("OpenAI authentication failed — check OPENAI_API_KEY")
            return AIServiceError(
                message="AI service authentication failed",
                details={"hint": "Verify your OPENAI_API_KEY is valid"},
            )
        if isinstance(exc, RateLimitError):
            logger.warning("OpenAI rate limit exceeded")
            return AIServiceError(
                message="AI service rate limit reached — please try again shortly",
            )
        if isinstance(exc, APIConnectionError):
            logger.error("Cannot reach OpenAI API")
            return AIServiceError(message="AI service connection failed")
        logger.error(f"Unexpected AI error: {exc}")
        return AIServiceError(
            message="AI analysis failed",
            details={"error": str(exc)},
        )

    async def analyze_assessment(self, answers: List[Dict[str, Any]]) -> AICareerResponse:
        client = self._require_client()
        if not answers:
            raise AIServiceError(message="No answers provided for analysis")

        formatted_answers = self._format_answers_for_prompt(answers)
        prompt = CAREER_ADVISOR_PROMPT.format(answers=formatted_answers)
        logger.info(f"Analyzing assessment with {len(answers)} answers")

        try:
            response = await client.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": CAREER_ADVISOR_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=6000,
                response_format=AICareerResponse,
            )
            career_response = response.choices[0].message.parsed
            if career_response is None:
                raise AIServiceError(message="AI returned no structured career result")
            logger.info(f"Generated {len(career_response.recommended_careers)} career recommendations")
            return career_response
        except AIServiceError:
            raise
        except Exception as exc:
            raise self._classify_error(exc)

    async def generate_learning_path(self, request: LearningPathRequest) -> LearningPathResponse:
        client = self._require_client()
        lang_map = {"uz": "Uzbek", "ru": "Russian", "en": "English"}
        prompt = LEARNING_PATH_PROMPT.format(
            career_name=request.career_name,
            career_reason=request.career_reason or "Not provided",
            language=lang_map[request.language],
        )
        try:
            response = await client.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": LEARNING_PATH_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=7000,
                response_format=LearningPathResponse,
            )
            path = response.choices[0].message.parsed
            if path is None:
                raise AIServiceError(message="AI returned no structured learning path")
            return path
        except AIServiceError:
            raise
        except Exception as exc:
            raise self._classify_error(exc)

    def _build_tutor_context(self, request: ModuleChatRequest, language: str) -> str:
        """Build the module-specific system context for the tutor."""
        lesson_ref = request.module_title
        for line in request.module_context.splitlines():
            stripped = line.strip()
            if re.match(r"(?i)^(lessons?|topics?)\s*:", stripped):
                raw = re.sub(r"(?i)^[^:]+:", "", stripped).strip()
                parts = [p.strip() for p in re.split(r"[;,]", raw) if len(p.strip()) > 2]
                if parts:
                    lesson_ref = parts[0]
                break
        return MODULE_TUTOR_PROMPT.format(
            career_name=request.career_name,
            module_title=request.module_title,
            module_context=request.module_context,
            language=language,
            lesson_ref=lesson_ref,
        )

    async def chat_about_module(self, request: ModuleChatRequest) -> ModuleChatResponse:
        client = self._require_client()
        lang_map = {"uz": "Uzbek", "ru": "Russian", "en": "English"}
        context_prompt = self._build_tutor_context(request, lang_map[request.language])
        messages = [
            {"role": "system", "content": MODULE_TUTOR_SYSTEM_PROMPT},
            {"role": "system", "content": context_prompt},
            *[message.model_dump() for message in request.messages],
        ]
        try:
            response = await client.chat.completions.parse(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1500,
                response_format=ModuleChatResponse,
            )
            tutor_response = response.choices[0].message.parsed
            if tutor_response is None:
                raise AIServiceError(message="AI returned no structured tutor response")
            return tutor_response
        except AIServiceError:
            raise
        except Exception as exc:
            raise self._classify_error(exc)

    async def generate_questions(self, request: GenerateQuestionsRequest) -> List[GeneratedQuestion]:
        """Generate 25 behavioral assessment questions via AI."""
        client = self._require_client()
        lang_map = {"uz": "Uzbek", "ru": "Russian", "en": "English"}
        interests_str = ", ".join(request.interests)
        first_interest = request.interests[0]
        interests_list = str(request.interests)
        prompt = QUESTION_PROMPT.format(
            interests=interests_str,
            language=lang_map[request.language],
            first_interest=first_interest,
            interests_list=interests_list,
        )
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": QUESTION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
                max_tokens=3000,
            )
            raw = response.choices[0].message.content or "[]"
            # Strip any accidental markdown fences
            raw = re.sub(r"^```[a-z]*\n?", "", raw.strip(), flags=re.MULTILINE)
            raw = re.sub(r"\n?```$", "", raw.strip(), flags=re.MULTILINE)
            data = json.loads(raw)
            questions = [GeneratedQuestion(**item) for item in data[:25]]
            if len(questions) < 25:
                raise AIServiceError(message=f"AI returned only {len(questions)} questions")
            return questions
        except AIServiceError:
            raise
        except Exception as exc:
            raise self._classify_error(exc)

    async def stream_chat(self, request: ModuleChatRequest) -> AsyncIterator[str]:
        """Yield text chunks for SSE streaming."""
        client = self._require_client()
        lang_map = {"uz": "Uzbek", "ru": "Russian", "en": "English"}
        context_prompt = self._build_tutor_context(request, lang_map[request.language])
        messages = [
            {"role": "system", "content": MODULE_TUTOR_SYSTEM_PROMPT},
            {"role": "system", "content": context_prompt},
            *[message.model_dump() for message in request.messages],
        ]
        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1500,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except AIServiceError:
            raise
        except Exception as exc:
            raise self._classify_error(exc)
