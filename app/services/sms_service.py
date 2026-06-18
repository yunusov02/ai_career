"""Eskiz SMS adapter with a safe console development provider."""

from loguru import logger

from app.core.config import settings


class SmsService:
    async def send_otp(self, phone_number: str, code: str, language: str) -> None:
        message = self._message(code, language)
        if settings.sms_provider.lower() != "eskiz":
            if settings.is_production:
                raise RuntimeError(
                    f"SMS_PROVIDER='{settings.sms_provider}' is not allowed in production. "
                    "Set SMS_PROVIDER=eskiz and configure ESKIZ_EMAIL/ESKIZ_PASSWORD."
                )
            logger.warning(
                "SKILLBRIDGE OTP | phone={} | code={} | expires={} minutes",
                phone_number,
                code,
                settings.otp_expire_minutes,
            )
            return

        if not settings.eskiz_email or not settings.eskiz_password:
            raise RuntimeError("Eskiz credentials are not configured")

        from eskiz import AsyncEskizSMS

        async with AsyncEskizSMS(
            email=settings.eskiz_email,
            password=settings.eskiz_password,
            from_whom=settings.eskiz_from,
        ) as client:
            await client.sms.send(
                mobile_phone=phone_number,
                message=message,
            )

    @staticmethod
    def _message(code: str, language: str) -> str:
        templates = {
            "uz": f"SkillBridge tasdiqlash kodi: {code}. Kodni hech kimga bermang.",
            "ru": f"Код подтверждения SkillBridge: {code}. Никому не сообщайте код.",
            "en": f"Your SkillBridge verification code is {code}. Do not share it.",
        }
        return templates[language]
