"""Schemas used by the active SkillBridge API."""

from app.schemas.ai import AICareerResponse, AIRecommendedCareer, AIResources, AIRoadmap
from app.schemas.guide import (
    GuideAnalyzeRequest,
    GuideAnswer,
    LearningPathRequest,
    LearningPathResponse,
    ModuleChatRequest,
    ModuleChatResponse,
)

__all__ = [
    "AICareerResponse",
    "AIRecommendedCareer",
    "AIResources",
    "AIRoadmap",
    "GuideAnalyzeRequest",
    "GuideAnswer",
    "LearningPathRequest",
    "LearningPathResponse",
    "ModuleChatRequest",
    "ModuleChatResponse",
]
