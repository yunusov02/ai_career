"""SkillBridge service package."""

from app.services.guide_service import build_fallback_recommendations
from app.services.learning_service import (
    build_fallback_chat,
    build_fallback_learning_path,
)

__all__ = [
    "build_fallback_recommendations",
    "build_fallback_chat",
    "build_fallback_learning_path",
]
