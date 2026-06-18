"""User history response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CareerHistoryItem(BaseModel):
    id: int
    language: str
    interests: list[str]
    result: dict[str, Any]
    created_at: datetime


class LearningPathHistoryItem(BaseModel):
    id: int
    career_name: str
    path: dict[str, Any]
    progress: dict[str, bool]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserHistoryResponse(BaseModel):
    assessments: list[CareerHistoryItem]
    learning_paths: list[LearningPathHistoryItem]
