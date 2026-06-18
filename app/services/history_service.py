"""Persistence for assessments, learning paths, progress, and tutor chats."""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform import CareerHistory, SavedLearningPath, TutorConversation
from app.schemas.ai import AICareerResponse
from app.schemas.guide import (
    GuideAnalyzeRequest,
    LearningPathResponse,
    ModuleChatRequest,
)


class HistoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_assessment(
        self,
        user_id: int,
        request: GuideAnalyzeRequest,
        result: AICareerResponse,
    ) -> CareerHistory:
        item = CareerHistory(
            user_id=user_id,
            language=request.language,
            interests_json=json.dumps(request.interests, ensure_ascii=False),
            answers_json=json.dumps(
                [answer.model_dump() for answer in request.answers],
                ensure_ascii=False,
            ),
            result_json=result.model_dump_json(),
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def save_learning_path(
        self,
        user_id: int,
        path: LearningPathResponse,
    ) -> SavedLearningPath:
        await self.session.execute(
            SavedLearningPath.__table__.update()
            .where(SavedLearningPath.user_id == user_id)
            .values(is_active=False)
        )
        item = SavedLearningPath(
            user_id=user_id,
            career_name=path.career_name,
            path_json=path.model_dump_json(exclude={"id"}),
            progress_json="{}",
            is_active=True,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def update_progress(
        self,
        user_id: int,
        path_id: int,
        module_id: str,
        completed: bool,
    ) -> dict[str, bool]:
        path = await self.session.scalar(
            select(SavedLearningPath).where(
                SavedLearningPath.id == path_id,
                SavedLearningPath.user_id == user_id,
            )
        )
        if not path:
            raise ValueError("Learning path not found")
        progress = json.loads(path.progress_json or "{}")
        progress[module_id] = completed
        path.progress_json = json.dumps(progress)
        await self.session.flush()
        return progress

    async def save_chat(
        self,
        user_id: int,
        request: ModuleChatRequest,
    ) -> None:
        if not request.learning_path_id or not request.module_id:
            return
        conversation = await self.session.scalar(
            select(TutorConversation).where(
                TutorConversation.user_id == user_id,
                TutorConversation.learning_path_id == request.learning_path_id,
                TutorConversation.module_id == request.module_id,
            )
        )
        if not conversation:
            conversation = TutorConversation(
                user_id=user_id,
                learning_path_id=request.learning_path_id,
                module_id=request.module_id,
            )
            self.session.add(conversation)
        conversation.messages_json = json.dumps(
            [message.model_dump() for message in request.messages],
            ensure_ascii=False,
        )
        await self.session.flush()

    async def get_history(self, user_id: int) -> dict:
        assessments = list((await self.session.scalars(
            select(CareerHistory)
            .where(CareerHistory.user_id == user_id)
            .order_by(CareerHistory.created_at.desc())
        )).all())
        paths = list((await self.session.scalars(
            select(SavedLearningPath)
            .where(SavedLearningPath.user_id == user_id)
            .order_by(SavedLearningPath.updated_at.desc())
        )).all())
        return {
            "assessments": [
                {
                    "id": item.id,
                    "language": item.language,
                    "interests": json.loads(item.interests_json),
                    "result": json.loads(item.result_json),
                    "created_at": item.created_at,
                }
                for item in assessments
            ],
            "learning_paths": [
                {
                    "id": item.id,
                    "career_name": item.career_name,
                    "path": json.loads(item.path_json),
                    "progress": json.loads(item.progress_json or "{}"),
                    "is_active": item.is_active,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                }
                for item in paths
            ],
        }
