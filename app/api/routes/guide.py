"""Authenticated career guidance endpoints."""

import json
from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from loguru import logger
from sqlalchemy import select

from app.ai.career_advisor import CareerAdvisor
from app.api.deps import CurrentUser, DbSession
from app.core.exceptions import AIServiceError
from app.models.platform import CareerPath
from app.schemas.ai import AICareerResponse
from app.schemas.guide import (
    CareerPathOut,
    ChatMessage,
    GeneratedQuestion,
    GenerateQuestionsRequest,
    GuideAnalyzeRequest,
    LearningPathRequest,
    LearningPathResponse,
    ModuleChatRequest,
    ModuleChatResponse,
    ModuleProgressRequest,
)
from app.services.guide_service import build_fallback_recommendations
from app.services.learning_service import (
    build_fallback_chat,
    build_fallback_learning_path,
)
from app.services.history_service import HistoryService
from app.services.question_service import build_fallback_questions


router = APIRouter()


def get_career_advisor() -> CareerAdvisor:
    """Factory used by route handlers; can be monkeypatched in tests."""
    return CareerAdvisor()


@router.get("/career-paths", response_model=List[CareerPathOut])
async def list_career_paths(
    db: DbSession,
    language: str = "en",
):
    """Return all active career paths from the database."""
    result = await db.execute(
        select(CareerPath).where(CareerPath.is_active == True).order_by(CareerPath.id)  # noqa: E712
    )
    paths = result.scalars().all()
    lang = language if language in ("en", "ru", "uz") else "en"
    return [
        CareerPathOut(
            id=p.id,
            slug=p.slug,
            icon=p.icon,
            title=getattr(p, f"title_{lang}"),
            description=getattr(p, f"description_{lang}"),
        )
        for p in paths
    ]


@router.post("/generate-questions", response_model=List[GeneratedQuestion])
async def generate_questions(
    request: GenerateQuestionsRequest,
    current_user: CurrentUser,
):
    """Generate 25 behavioral assessment questions tailored to selected interests."""
    advisor = get_career_advisor()
    try:
        return await advisor.generate_questions(request)
    except AIServiceError as exc:
        logger.warning(f"AI unavailable for question generation ({exc.message}), using fallback")
        return build_fallback_questions(request)


@router.post("/analyze", response_model=AICareerResponse)
async def analyze_guide(
    request: GuideAnalyzeRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Analyze an assessment and save it to the user's history."""
    advisor = get_career_advisor()
    language_names = {"en": "English", "ru": "Russian", "uz": "Uzbek"}
    answers = [
        {
            "question_text": "Selected career fields",
            "answer_text": ", ".join(request.interests),
            "category": "interests",
        },
        {
            "question_text": "Required response language",
            "answer_text": language_names[request.language],
            "category": "language",
        },
        *[
            {
                "question_text": answer.question,
                "answer_text": f"{answer.score} out of 5",
                "category": answer.category,
            }
            for answer in request.answers
        ],
    ]

    try:
        result = await advisor.analyze_assessment(answers)
    except AIServiceError as exc:
        logger.warning(f"AI unavailable for guide analysis ({exc.message}), using fallback")
        result = build_fallback_recommendations(request)

    await HistoryService(db).save_assessment(current_user.id, request, result)
    return result


@router.post("/learning-path", response_model=LearningPathResponse)
async def create_learning_path(
    request: LearningPathRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a detailed module curriculum for a selected career."""
    advisor = get_career_advisor()
    try:
        path = await advisor.generate_learning_path(request)
    except AIServiceError as exc:
        logger.warning(f"AI unavailable for learning path ({exc.message}), using fallback")
        path = build_fallback_learning_path(request)

    saved = await HistoryService(db).save_learning_path(current_user.id, path)
    path.id = saved.id
    return path


@router.post("/chat", response_model=ModuleChatResponse)
async def chat_with_module_tutor(
    request: ModuleChatRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """Chat with an AI tutor scoped to a selected learning module."""
    advisor = get_career_advisor()
    try:
        response = await advisor.chat_about_module(request)
    except AIServiceError as exc:
        logger.warning(f"AI unavailable for module chat ({exc.message}), using fallback")
        response = build_fallback_chat(request)

    persisted_messages = [
        *request.messages,
        ChatMessage(role="assistant", content=response.answer),
    ]
    request.messages = persisted_messages
    await HistoryService(db).save_chat(current_user.id, request)
    return response


@router.post("/chat/stream")
async def stream_chat(
    request: ModuleChatRequest,
    current_user: CurrentUser,
):
    """Stream AI tutor response as server-sent events."""
    advisor = get_career_advisor()

    if not advisor.available:
        fallback = build_fallback_chat(request)

        async def fallback_stream():
            payload = json.dumps({"chunk": fallback.answer})
            yield f"data: {payload}\n\n"
            if fallback.suggested_questions:
                sq_payload = json.dumps({"suggested_questions": fallback.suggested_questions})
                yield f"data: {sq_payload}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(fallback_stream(), media_type="text/event-stream")

    async def ai_stream():
        try:
            async for chunk in advisor.stream_chat(request):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except AIServiceError as exc:
            yield f"data: {json.dumps({'error': exc.message})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(ai_stream(), media_type="text/event-stream")


@router.put("/learning-path/{path_id}/modules/{module_id}", response_model=dict[str, bool])
async def update_module_progress(
    path_id: int,
    module_id: str,
    payload: ModuleProgressRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        return await HistoryService(db).update_progress(
            current_user.id,
            path_id,
            module_id,
            payload.completed,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
