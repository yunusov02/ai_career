"""Authenticated user history routes."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.history import UserHistoryResponse
from app.services.history_service import HistoryService


router = APIRouter()


@router.get("", response_model=UserHistoryResponse)
async def get_history(db: DbSession, current_user: CurrentUser):
    return await HistoryService(db).get_history(current_user.id)
