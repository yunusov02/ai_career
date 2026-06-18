"""Phone OTP authentication service."""

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_otp,
    verify_otp,
    verify_token,
)
from app.models.platform import OtpChallenge, PlatformUser
from app.schemas.auth import Token
from app.services.sms_service import SmsService


class AuthService:
    def __init__(self, session: AsyncSession, sms_service: SmsService | None = None):
        self.session = session
        self.sms_service = sms_service or SmsService()

    async def request_otp(self, phone_number: str, language: str) -> None:
        now = datetime.now(timezone.utc)
        latest = await self.session.scalar(
            select(OtpChallenge)
            .where(OtpChallenge.phone_number == phone_number)
            .order_by(OtpChallenge.created_at.desc())
            .limit(1)
        )
        if latest and latest.created_at.tzinfo is None:
            latest.created_at = latest.created_at.replace(tzinfo=timezone.utc)
        if latest and (now - latest.created_at).total_seconds() < settings.otp_resend_seconds:
            raise ValidationError(message="Please wait before requesting another code")

        code = f"{secrets.randbelow(1_000_000):06d}"
        challenge = OtpChallenge(
            phone_number=phone_number,
            code_hash=hash_otp(phone_number, code),
            expires_at=now + timedelta(minutes=settings.otp_expire_minutes),
        )
        self.session.add(challenge)
        await self.session.flush()
        await self.sms_service.send_otp(phone_number, code, language)

    async def verify_otp(self, phone_number: str, code: str, language: str) -> tuple[PlatformUser, Token]:
        challenge = await self.session.scalar(
            select(OtpChallenge)
            .where(
                OtpChallenge.phone_number == phone_number,
                OtpChallenge.consumed_at.is_(None),
            )
            .order_by(OtpChallenge.created_at.desc())
            .limit(1)
        )
        now = datetime.now(timezone.utc)
        if not challenge:
            raise AuthenticationError(message="Verification code not found")
        expires_at = challenge.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise AuthenticationError(message="Verification code expired")
        if challenge.attempts >= settings.otp_max_attempts:
            raise AuthenticationError(message="Too many verification attempts")

        challenge.attempts += 1
        if not verify_otp(phone_number, code, challenge.code_hash):
            # The route converts this exception to HTTP 401, which would make
            # the request dependency roll back unless the attempt is committed.
            await self.session.commit()
            raise AuthenticationError(message="Invalid verification code")

        challenge.consumed_at = now
        user = await self.session.scalar(
            select(PlatformUser).where(PlatformUser.phone_number == phone_number)
        )
        if not user:
            user = PlatformUser(
                phone_number=phone_number,
                preferred_language=language,
            )
            self.session.add(user)
            await self.session.flush()
        user.preferred_language = language
        user.last_login_at = now
        await self.session.flush()
        return user, self._create_tokens(user.id)

    async def refresh_token(self, refresh_token: str) -> Token:
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise AuthenticationError(message="Invalid or expired refresh token")
        user = await self.session.get(PlatformUser, int(payload["sub"]))
        if not user or not user.is_active:
            raise AuthenticationError(message="User not found or inactive")
        return self._create_tokens(user.id)

    async def get_current_user(self, token: str) -> PlatformUser:
        payload = verify_token(token, token_type="access")
        if not payload:
            raise AuthenticationError(message="Invalid or expired token")
        user = await self.session.get(PlatformUser, int(payload["sub"]))
        if not user or not user.is_active:
            raise AuthenticationError(message="User not found or inactive")
        return user

    @staticmethod
    def _create_tokens(user_id: int) -> Token:
        data = {"sub": str(user_id)}
        return Token(
            access_token=create_access_token(data),
            refresh_token=create_refresh_token(data),
        )
