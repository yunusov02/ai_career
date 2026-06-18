"""Production models for SkillBridge authentication and user data."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class PlatformUser(Base, TimestampMixin):
    __tablename__ = "platform_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    preferred_language: Mapped[str] = mapped_column(String(5), default="uz")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class OtpChallenge(Base):
    __tablename__ = "otp_challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20), index=True)
    code_hash: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class CareerHistory(Base, TimestampMixin):
    __tablename__ = "career_histories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("platform_users.id", ondelete="CASCADE"),
        index=True,
    )
    language: Mapped[str] = mapped_column(String(5))
    interests_json: Mapped[str] = mapped_column(Text)
    answers_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)


class SavedLearningPath(Base, TimestampMixin):
    __tablename__ = "saved_learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("platform_users.id", ondelete="CASCADE"),
        index=True,
    )
    career_name: Mapped[str] = mapped_column(String(200))
    path_json: Mapped[str] = mapped_column(Text)
    progress_json: Mapped[str] = mapped_column(Text, default="{}")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CareerPath(Base, TimestampMixin):
    """Canonical career interest paths shown on the home/selection screen."""

    __tablename__ = "career_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    icon: Mapped[str] = mapped_column(String(10), default="01")
    title_en: Mapped[str] = mapped_column(String(200))
    title_ru: Mapped[str] = mapped_column(String(200))
    title_uz: Mapped[str] = mapped_column(String(200))
    description_en: Mapped[str] = mapped_column(Text)
    description_ru: Mapped[str] = mapped_column(Text)
    description_uz: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class TutorConversation(Base, TimestampMixin):
    __tablename__ = "tutor_conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("platform_users.id", ondelete="CASCADE"),
        index=True,
    )
    learning_path_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("saved_learning_paths.id", ondelete="CASCADE"),
        nullable=True,
    )
    module_id: Mapped[str] = mapped_column(String(160))
    messages_json: Mapped[str] = mapped_column(Text, default="[]")
